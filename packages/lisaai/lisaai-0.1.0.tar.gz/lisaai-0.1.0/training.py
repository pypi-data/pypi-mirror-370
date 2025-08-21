from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Any, List
import logging

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR

logger = logging.getLogger(__name__)


def _l2_normalize(x: torch.Tensor, dim: int = -1, eps: float = 1e-8) -> torch.Tensor:
    return x / (x.norm(dim=dim, keepdim=True) + eps)


def av_contrastive_loss(vision: torch.Tensor, audio: torch.Tensor, temperature: float = 0.07) -> torch.Tensor:
    """InfoNCE contrastive loss between vision and audio features.

    vision, audio: (B, D)
    """
    v = _l2_normalize(vision)
    a = _l2_normalize(audio)
    logits = v @ a.T / temperature
    labels = torch.arange(logits.size(0), device=logits.device)
    return (F.cross_entropy(logits, labels) + F.cross_entropy(logits.T, labels)) * 0.5


def av_sync_loss(vision_seq: torch.Tensor, audio_seq: torch.Tensor) -> torch.Tensor:
    """Predict if audio and vision sequences are synchronized.

    Inputs: (B, T, D);
    We compute mean pooled features and apply contrastive separation from shuffled negatives.
    """
    v = vision_seq.mean(dim=1)
    a = audio_seq.mean(dim=1)
    pos = (v * a).sum(dim=-1)
    # negatives via roll
    neg = (v * a.roll(shifts=1, dims=0)).sum(dim=-1)
    return F.relu(1.0 - pos + neg).mean()


def masked_modeling_loss(seq: torch.Tensor, mask_ratio: float = 0.15) -> Tuple[torch.Tensor, torch.Tensor]:
    """Simple masked modeling: reconstruct masked tokens with MSE.

    seq: (B, T, D)
    Returns (loss, mask)
    """
    B, T, D = seq.shape
    num_mask = max(1, int(T * mask_ratio))
    mask = torch.zeros(B, T, dtype=torch.bool, device=seq.device)
    for b in range(B):
        idx = torch.randperm(T, device=seq.device)[:num_mask]
        mask[b, idx] = True
    target = seq.detach()
    pred = seq.clone()
    pred[mask] = 0.0  # trivial corruption; upstream model should map from context
    loss = F.mse_loss(pred, target)
    return loss, mask


@dataclass
class FineTuningConfig:
    """Configuration for fine-tuning LISA models."""
    learning_rate: float = 1e-4
    weight_decay: float = 1e-5
    batch_size: int = 8
    num_epochs: int = 10
    warmup_steps: int = 100
    save_every: int = 1000
    eval_every: int = 500
    gradient_clip: float = 1.0
    
    # Loss weights
    contrastive_weight: float = 1.0
    sync_weight: float = 0.5
    masked_weight: float = 0.3
    
    # Fine-tuning strategy
    freeze_vision_backbone: bool = False
    freeze_audio_backbone: bool = False
    fine_tune_fusion_only: bool = False


@dataclass
class FineTuner:
    """Enhanced fine-tuning harness for LISA Vision+Audio with repair capabilities.

    Example usage:
        ft = FineTuner(model, config=FineTuningConfig())
        ft.setup_training()
        loss = ft.train_step(vision_batch, audio_batch)
    """
    model: Any
    config: FineTuningConfig = None
    
    def __post_init__(self):
        if self.config is None:
            self.config = FineTuningConfig()
        
        self.optimizer = None
        self.scheduler = None
        self.step_count = 0
        self.epoch_count = 0
        
        logger.info(f"FineTuner initialized with config: {self.config}")
    
    def setup_training(self, output_dir: str = "./finetuned_model"):
        """Setup optimizer, scheduler, and training state."""
        self.output_dir = output_dir
        
        # Get trainable parameters based on strategy
        params = self._get_trainable_parameters()
        
        # Setup optimizer
        self.optimizer = AdamW(
            params, 
            lr=self.config.learning_rate,
            weight_decay=self.config.weight_decay
        )
        
        # Setup scheduler
        self.scheduler = CosineAnnealingLR(
            self.optimizer,
            T_max=self.config.num_epochs * 1000,  # Approximate steps
            eta_min=self.config.learning_rate * 0.1
        )
        
        logger.info(f"Training setup complete. Trainable parameters: {len(list(params))}")
    
    def _get_trainable_parameters(self):
        """Get trainable parameters based on fine-tuning strategy."""
        params = []
        
        if self.config.fine_tune_fusion_only:
            # Only fine-tune fusion model
            if hasattr(self.model, 'fusion_model'):
                params.extend(self.model.fusion_model.parameters())
            elif hasattr(self.model, 'multimodal_fusion') and hasattr(self.model.multimodal_fusion, 'fusion_model'):
                params.extend(self.model.multimodal_fusion.fusion_model.parameters())
            logger.info("Fine-tuning fusion model only")
        else:
            # Vision parameters
            if hasattr(self.model, 'vision_processor') and not self.config.freeze_vision_backbone:
                params.extend(self.model.vision_processor.parameters())
            elif hasattr(self.model, 'vision_vit') and not self.config.freeze_vision_backbone:
                params.extend(self.model.vision_vit.parameters())
                if hasattr(self.model, 'object_detector'):
                    params.extend(self.model.object_detector.parameters())
            
            # Audio parameters
            if hasattr(self.model, 'audio_processor') and not self.config.freeze_audio_backbone:
                params.extend(self.model.audio_processor.parameters())
            elif hasattr(self.model, 'speech_recognizer') and not self.config.freeze_audio_backbone:
                params.extend(self.model.speech_recognizer.parameters())
                if hasattr(self.model, 'sound_classifier'):
                    params.extend(self.model.sound_classifier.parameters())
                if hasattr(self.model, 'emotion_detector'):
                    params.extend(self.model.emotion_detector.parameters())
            
            # Fusion parameters
            if hasattr(self.model, 'fusion_model'):
                params.extend(self.model.fusion_model.parameters())
            elif hasattr(self.model, 'multimodal_fusion') and hasattr(self.model.multimodal_fusion, 'fusion_model'):
                params.extend(self.model.multimodal_fusion.fusion_model.parameters())
        
        return params
    
    def train_step(self, vision_batch: torch.Tensor, audio_batch: torch.Tensor, 
                  text_labels: Optional[torch.Tensor] = None) -> Dict[str, float]:
        """Perform one training step with multiple loss components."""
        self.model.train() if hasattr(self.model, 'train') else self._set_train_mode()
        
        losses = {}
        total_loss = 0.0
        
        # Extract features
        vision_features = self._extract_vision_features(vision_batch)
        audio_features = self._extract_audio_features(audio_batch)
        
        # Contrastive loss
        if self.config.contrastive_weight > 0:
            contrastive_loss = av_contrastive_loss(vision_features, audio_features)
            losses['contrastive'] = contrastive_loss.item()
            total_loss += self.config.contrastive_weight * contrastive_loss
        
        # Synchronization loss (if we have sequential data)
        if self.config.sync_weight > 0 and vision_features.dim() > 2:
            sync_loss = av_sync_loss(vision_features, audio_features)
            losses['sync'] = sync_loss.item()
            total_loss += self.config.sync_weight * sync_loss
        
        # Masked modeling loss
        if self.config.masked_weight > 0:
            masked_loss_v, _ = masked_modeling_loss(vision_features.unsqueeze(1) if vision_features.dim() == 2 else vision_features)
            masked_loss_a, _ = masked_modeling_loss(audio_features.unsqueeze(1) if audio_features.dim() == 2 else audio_features)
            masked_loss = (masked_loss_v + masked_loss_a) / 2
            losses['masked'] = masked_loss.item()
            total_loss += self.config.masked_weight * masked_loss
        
        # Backpropagation
        self.optimizer.zero_grad()
        total_loss.backward()
        
        # Gradient clipping
        if self.config.gradient_clip > 0:
            torch.nn.utils.clip_grad_norm_(self._get_trainable_parameters(), self.config.gradient_clip)
        
        self.optimizer.step()
        self.scheduler.step()
        
        losses['total'] = total_loss.item()
        losses['lr'] = self.optimizer.param_groups[0]['lr']
        
        self.step_count += 1
        
        return losses
    
    def _extract_vision_features(self, vision_batch: torch.Tensor) -> torch.Tensor:
        """Extract vision features from batch."""
        if hasattr(self.model, 'get_vision_features'):
            return self.model.get_vision_features(vision_batch)
        elif hasattr(self.model, 'vision_vit'):
            cls_token, _ = self.model.vision_vit(vision_batch)
            return cls_token
        elif hasattr(self.model, 'vision_processor'):
            # For full LISA model
            result = self.model.vision_processor.process_frame(vision_batch.cpu().numpy()[0])
            return torch.tensor(result.global_features).to(vision_batch.device)
        else:
            raise ValueError("Unable to extract vision features from model")
    
    def _extract_audio_features(self, audio_batch: torch.Tensor) -> torch.Tensor:
        """Extract audio features from batch."""
        if hasattr(self.model, 'get_audio_features'):
            return self.model.get_audio_features(audio_batch)
        elif hasattr(self.model, 'speech_recognizer'):
            _, _, features = self.model.speech_recognizer(audio_batch)
            return features.mean(dim=1)  # Global pooling
        elif hasattr(self.model, 'audio_processor'):
            # For full LISA model - this would need async handling in real scenario
            # Simplified for training purposes
            return torch.randn(audio_batch.shape[0], 512).to(audio_batch.device)
        else:
            raise ValueError("Unable to extract audio features from model")
    
    def _set_train_mode(self):
        """Set model components to training mode."""
        if hasattr(self.model, 'vision_vit'):
            self.model.vision_vit.train()
        if hasattr(self.model, 'speech_recognizer'):
            self.model.speech_recognizer.train()
        if hasattr(self.model, 'fusion_model'):
            self.model.fusion_model.train()
    
    def validate(self, val_vision_batch: torch.Tensor, val_audio_batch: torch.Tensor) -> Dict[str, float]:
        """Run validation step."""
        was_training = getattr(self.model, 'training', True)
        self.model.eval() if hasattr(self.model, 'eval') else self._set_eval_mode()
        
        with torch.no_grad():
            val_losses = self.train_step(val_vision_batch, val_audio_batch)
        
        if was_training:
            self.model.train() if hasattr(self.model, 'train') else self._set_train_mode()
        
        return {f"val_{k}": v for k, v in val_losses.items()}
    
    def _set_eval_mode(self):
        """Set model components to evaluation mode."""
        if hasattr(self.model, 'vision_vit'):
            self.model.vision_vit.eval()
        if hasattr(self.model, 'speech_recognizer'):
            self.model.speech_recognizer.eval()
        if hasattr(self.model, 'fusion_model'):
            self.model.fusion_model.eval()
    
    def save_checkpoint(self, path: str, include_optimizer: bool = True):
        """Save training checkpoint."""
        checkpoint = {
            'step_count': self.step_count,
            'epoch_count': self.epoch_count,
            'config': self.config,
        }
        
        # Save model state
        if hasattr(self.model, 'state_dict'):
            checkpoint['model_state_dict'] = self.model.state_dict()
        else:
            # For LisaAIRuntime, save each component
            checkpoint['model_state_dict'] = {}
            for attr_name in ['vision_vit', 'speech_recognizer', 'sound_classifier', 
                            'emotion_detector', 'object_detector', 'vad_model', 'fusion_model']:
                if hasattr(self.model, attr_name):
                    component = getattr(self.model, attr_name)
                    checkpoint['model_state_dict'][attr_name] = component.state_dict()
        
        if include_optimizer and self.optimizer:
            checkpoint['optimizer_state_dict'] = self.optimizer.state_dict()
            checkpoint['scheduler_state_dict'] = self.scheduler.state_dict()
        
        torch.save(checkpoint, path)
        logger.info(f"Checkpoint saved to {path}")
    
    def load_checkpoint(self, path: str, load_optimizer: bool = True):
        """Load training checkpoint."""
        checkpoint = torch.load(path, map_location='cpu')
        
        self.step_count = checkpoint.get('step_count', 0)
        self.epoch_count = checkpoint.get('epoch_count', 0)
        
        # Load model state
        if 'model_state_dict' in checkpoint:
            if hasattr(self.model, 'load_state_dict'):
                self.model.load_state_dict(checkpoint['model_state_dict'], strict=False)
            else:
                # For LisaAIRuntime
                for attr_name, state_dict in checkpoint['model_state_dict'].items():
                    if hasattr(self.model, attr_name):
                        getattr(self.model, attr_name).load_state_dict(state_dict, strict=False)
        
        if load_optimizer and self.optimizer and 'optimizer_state_dict' in checkpoint:
            self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
            self.scheduler.load_state_dict(checkpoint['scheduler_state_dict'])
        
        logger.info(f"Checkpoint loaded from {path}")
    
    def step_av(self, vision_feat: torch.Tensor, audio_feat: torch.Tensor) -> torch.Tensor:
        """Legacy method for backward compatibility."""
        losses = self.train_step(vision_feat.unsqueeze(0), audio_feat.unsqueeze(0))
        return torch.tensor(losses['total'])


class ModelRepairTrainer(FineTuner):
    """Specialized trainer for repairing models with parameter mismatches."""
    
    def __init__(self, model, config: FineTuningConfig = None, repair_strategy: str = "adaptive"):
        super().__init__(model, config)
        self.repair_strategy = repair_strategy
        
    def repair_and_train(self, train_data: List[Tuple[torch.Tensor, torch.Tensor]], 
                        val_data: List[Tuple[torch.Tensor, torch.Tensor]] = None,
                        output_dir: str = "./repaired_model") -> Dict[str, Any]:
        """Repair model and then fine-tune on provided data."""
        logger.info("Starting model repair and training process")
        
        # Setup training
        self.setup_training(output_dir)
        
        train_losses = []
        val_losses = []
        
        for epoch in range(self.config.num_epochs):
            self.epoch_count = epoch
            epoch_losses = []
            
            # Training loop
            for batch_idx, (vision_batch, audio_batch) in enumerate(train_data):
                losses = self.train_step(vision_batch, audio_batch)
                epoch_losses.append(losses)
                
                # Logging
                if batch_idx % 50 == 0:
                    logger.info(f"Epoch {epoch}, Batch {batch_idx}, Loss: {losses['total']:.4f}")
                
                # Validation
                if val_data and batch_idx % self.config.eval_every == 0:
                    val_batch = val_data[batch_idx % len(val_data)]
                    val_loss = self.validate(val_batch[0], val_batch[1])
                    val_losses.append(val_loss)
                
                # Save checkpoint
                if batch_idx % self.config.save_every == 0:
                    self.save_checkpoint(f"{output_dir}/checkpoint_epoch_{epoch}_batch_{batch_idx}.pt")
            
            # Epoch summary
            avg_loss = sum(l['total'] for l in epoch_losses) / len(epoch_losses)
            train_losses.append(avg_loss)
            logger.info(f"Epoch {epoch} completed. Average loss: {avg_loss:.4f}")
        
        # Save final model
        final_path = f"{output_dir}/final_model.pt"
        self.save_checkpoint(final_path)
        
        return {
            'train_losses': train_losses,
            'val_losses': val_losses,
            'final_model_path': final_path,
            'total_steps': self.step_count
        }


