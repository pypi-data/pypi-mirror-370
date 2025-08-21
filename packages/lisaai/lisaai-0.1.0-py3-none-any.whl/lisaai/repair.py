"""
Model Repair and Dimension Adaptation Module

This module provides tools to automatically repair and adapt LISA models
with dimension mismatches, missing components, or incompatible architectures.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import json

import torch
import torch.nn as nn
from safetensors.torch import load_file, save_file

from .inspector import summarize_checkpoint
from .runtime import (
    LisaViT, LisaObjectDetector, LisaSpeechRecognizer, 
    LisaSoundClassifier, LisaEmotionDetector, LisaVAD, 
    FusionAttention, AudioEncoder
)


logger = logging.getLogger(__name__)


class ModelRepairer:
    """Comprehensive model repair and adaptation utilities."""
    
    def __init__(self, model_dir: str):
        self.model_dir = Path(model_dir)
        self.checkpoint_path = self.model_dir / "model.safetensors"
        self.config_path = self.model_dir / "config.json"
        
        # Analyze current state
        self.analysis = summarize_checkpoint(str(self.model_dir))
        self.tensors = load_file(str(self.checkpoint_path))
        
        logger.info(f"ModelRepairer initialized for {model_dir}")
        logger.info(f"Found {len(self.analysis['repair_suggestions'])} issues to address")
        
        # Track which tensors need repair
        self.tensor_repairs_needed = self._analyze_tensor_mismatches()
    
    def _analyze_tensor_mismatches(self) -> Dict[str, Dict[str, Any]]:
        """Analyze specific tensor dimension mismatches that need repair."""
        repairs = {}
        
        # Check for Vision ViT norm layer mismatches (512 vs 768)
        if 'vision.vit.norm.weight' in self.tensors:
            norm_weight = self.tensors['vision.vit.norm.weight']
            if norm_weight.shape[0] == 512:  # Saved as 512 but config expects 768
                repairs['vision.vit.norm'] = {
                    'component': 'vision_vit_norm',
                    'saved_dim': 512,
                    'target_dim': 768,
                    'tensors': ['vision.vit.norm.weight', 'vision.vit.norm.bias']
                }
        
        # Check for fusion layer mismatches (512x512 vs 1024x1024)
        fusion_keys = [k for k in self.tensors.keys() if 'model.out_proj' in k]
        if fusion_keys:
            out_proj_weight = self.tensors.get('model.out_proj.weight')
            if out_proj_weight is not None and out_proj_weight.shape == (512, 512):
                repairs['fusion_attention'] = {
                    'component': 'fusion_attention',
                    'saved_dim': 512,
                    'target_dim': 1024,
                    'tensors': ['model.q_proj.weight', 'model.k_proj.weight', 
                              'model.v_proj.weight', 'model.out_proj.weight', 'model.out_proj.bias']
                }
        
        return repairs
    
    def diagnose(self) -> Dict[str, Any]:
        """Return detailed diagnosis of model issues."""
        return {
            'checkpoint_path': str(self.checkpoint_path),
            'total_parameters': self.analysis['saved_param_count'],
            'detected_dimensions': self.analysis['inferred_dimensions'],
            'dimension_mismatches': self.analysis['dimension_mismatches'],
            'tensor_repairs_needed': self.tensor_repairs_needed,
            'issues_found': len(self.analysis['repair_suggestions']),
            'repair_suggestions': self.analysis['repair_suggestions']
        }
    
    def repair_tensors(self) -> Dict[str, torch.Tensor]:
        """Repair tensor dimension mismatches by adapting saved tensors."""
        repaired_tensors = dict(self.tensors)  # Start with original tensors
        
        for repair_name, repair_info in self.tensor_repairs_needed.items():
            logger.info(f"Repairing {repair_name}: {repair_info['saved_dim']} -> {repair_info['target_dim']}")
            
            if repair_name == 'vision.vit.norm':
                # Repair ViT norm layer (512 -> 768)
                repaired_tensors.update(self._repair_vit_norm_layer(repair_info))
                
            elif repair_name == 'fusion_attention':
                # Repair fusion attention (512 -> 1024)
                repaired_tensors.update(self._repair_fusion_attention(repair_info))
        
        return repaired_tensors
    
    def _repair_vit_norm_layer(self, repair_info: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Repair ViT norm layer dimension mismatch."""
        repaired = {}
        saved_dim = repair_info['saved_dim']
        target_dim = repair_info['target_dim']
        
        # Get original tensors
        norm_weight = self.tensors['vision.vit.norm.weight']  # [512]
        norm_bias = self.tensors['vision.vit.norm.bias']      # [512]
        
        # Expand dimensions by interpolation + padding
        if target_dim > saved_dim:
            # Create expanded tensors
            new_weight = torch.zeros(target_dim)
            new_bias = torch.zeros(target_dim)
            
            # Copy original values to first part
            new_weight[:saved_dim] = norm_weight
            new_bias[:saved_dim] = norm_bias
            
            # Initialize remaining dimensions with small values
            remaining_dims = target_dim - saved_dim
            new_weight[saved_dim:] = torch.normal(0, 0.02, (remaining_dims,))
            new_bias[saved_dim:] = torch.zeros(remaining_dims)
            
            repaired['vision.vit.norm.weight'] = new_weight
            repaired['vision.vit.norm.bias'] = new_bias
            
            logger.info(f"Expanded ViT norm layer: {norm_weight.shape} -> {new_weight.shape}")
        
        return repaired
    
    def _repair_fusion_attention(self, repair_info: Dict[str, Any]) -> Dict[str, torch.Tensor]:
        """Repair fusion attention dimension mismatch."""
        repaired = {}
        saved_dim = repair_info['saved_dim']
        target_dim = repair_info['target_dim']
        
        for tensor_name in repair_info['tensors']:
            if tensor_name in self.tensors:
                original = self.tensors[tensor_name]
                
                if 'weight' in tensor_name and len(original.shape) == 2:
                    # 2D weight matrix [out_dim, in_dim] or [dim, dim]
                    if original.shape == (saved_dim, saved_dim):
                        # Square matrix: expand both dimensions
                        new_tensor = torch.zeros(target_dim, target_dim)
                        new_tensor[:saved_dim, :saved_dim] = original
                        
                        # Initialize new connections with Xavier/Glorot initialization
                        remaining = target_dim - saved_dim
                        if remaining > 0:
                            std = torch.sqrt(torch.tensor(2.0 / (saved_dim + target_dim)))
                            new_tensor[saved_dim:, :] = torch.normal(0, std, (remaining, target_dim))
                            new_tensor[:, saved_dim:] = torch.normal(0, std, (target_dim, remaining))
                        
                        repaired[tensor_name] = new_tensor
                        logger.info(f"Expanded {tensor_name}: {original.shape} -> {new_tensor.shape}")
                    
                elif 'bias' in tensor_name and len(original.shape) == 1:
                    # 1D bias vector
                    if original.shape[0] == saved_dim:
                        new_tensor = torch.zeros(target_dim)
                        new_tensor[:saved_dim] = original
                        repaired[tensor_name] = new_tensor
                        logger.info(f"Expanded {tensor_name}: {original.shape} -> {new_tensor.shape}")
        
        return repaired
    
    def repair_config(self) -> bool:
        """Automatically repair config.json based on checkpoint dimensions."""
        try:
            config = self.analysis['config'].copy()
            inferred_dims = self.analysis['inferred_dimensions']
            
            # Update vision config
            if 'vision_embed_dim' in inferred_dims:
                if 'vision_config' not in config:
                    config['vision_config'] = {}
                config['vision_config']['embed_dim'] = inferred_dims['vision_embed_dim']
                logger.info(f"Updated vision embed_dim to {inferred_dims['vision_embed_dim']}")
            
            if 'vision_depth' in inferred_dims:
                config['vision_config']['num_layers'] = inferred_dims['vision_depth']
            
            if 'vision_num_heads' in inferred_dims:
                config['vision_config']['num_heads'] = inferred_dims['vision_num_heads']
            
            # Update audio config
            if 'audio_speech_embed_dim' in inferred_dims:
                if 'audio_config' not in config:
                    config['audio_config'] = {}
                config['audio_config']['embed_dim'] = inferred_dims['audio_speech_embed_dim']
                logger.info(f"Updated audio embed_dim to {inferred_dims['audio_speech_embed_dim']}")
            
            if 'audio_speech_depth' in inferred_dims:
                config['audio_config']['num_layers'] = inferred_dims['audio_speech_depth']
            
            # Update multimodal config
            if 'fusion_hidden_dim' in inferred_dims:
                if 'multimodal_config' not in config:
                    config['multimodal_config'] = {}
                config['multimodal_config']['hidden_dim'] = inferred_dims['fusion_hidden_dim']
                logger.info(f"Updated fusion hidden_dim to {inferred_dims['fusion_hidden_dim']}")
            
            # Save updated config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Config.json successfully repaired")
            return True
            
        except Exception as e:
            logger.error(f"Failed to repair config: {e}")
            return False
    
    def repair_missing_components(self) -> Dict[str, torch.nn.Module]:
        """Create and initialize missing model components."""
        missing_components = {}
        inferred_dims = self.analysis['inferred_dimensions']
        saved_prefixes = set(self.analysis['saved_prefix_param_counts'].keys())
        
        # Standard LISA components
        expected_components = {
            'vision.vit': ('ViT', 'vision_embed_dim'),
            'vision.object_detector': ('ObjectDetector', 'vision_embed_dim'),
            'audio.speech_recognizer': ('SpeechRecognizer', 'audio_speech_embed_dim'),
            'audio.sound_classifier': ('SoundClassifier', 'audio_sound_embed_dim'),
            'audio.emotion_detector': ('EmotionDetector', 'audio_sound_embed_dim'),
            'audio.vad_model': ('VAD', None),
            'model': ('Fusion', 'fusion_hidden_dim')
        }
        
        for prefix, (component_type, dim_key) in expected_components.items():
            if prefix not in saved_prefixes:
                logger.info(f"Creating missing component: {prefix}")
                
                if component_type == 'ViT':
                    embed_dim = inferred_dims.get(dim_key, 768)
                    component = LisaViT(
                        img_size=112, embed_dim=embed_dim, 
                        depth=inferred_dims.get('vision_depth', 12),
                        num_heads=max(1, embed_dim // 64)
                    )
                elif component_type == 'ObjectDetector':
                    embed_dim = inferred_dims.get(dim_key, 768)
                    num_classes = inferred_dims.get('object_detection_classes', 80)
                    component = LisaObjectDetector(embed_dim=embed_dim, num_classes=num_classes)
                elif component_type == 'SpeechRecognizer':
                    embed_dim = inferred_dims.get(dim_key, 512)
                    component = LisaSpeechRecognizer(embed_dim=embed_dim)
                elif component_type == 'SoundClassifier':
                    embed_dim = inferred_dims.get(dim_key, 512)
                    component = LisaSoundClassifier(embed_dim=embed_dim)
                elif component_type == 'EmotionDetector':
                    embed_dim = inferred_dims.get(dim_key, 512)
                    component = LisaEmotionDetector(embed_dim=embed_dim)
                elif component_type == 'VAD':
                    component = LisaVAD()
                elif component_type == 'Fusion':
                    hidden_dim = inferred_dims.get(dim_key, 1024)
                    component = FusionAttention(hidden_dim=hidden_dim)
                else:
                    continue
                
                missing_components[prefix] = component
        
        return missing_components
    
    def adapt_dimensions(self, target_dims: Dict[str, int], 
                        tensors: Optional[Dict[str, torch.Tensor]] = None) -> Dict[str, torch.Tensor]:
        """Adapt model weights to new dimensions through interpolation or truncation."""
        if tensors is None:
            adapted_tensors = {}
            for name, tensor in self.tensors.items():
                adapted_tensors[name] = tensor.clone()
        else:
            adapted_tensors = {}
            for name, tensor in tensors.items():
                adapted_tensors[name] = tensor.clone()
        
        # Vision ViT dimension adaptation
        if 'vision_embed_dim' in target_dims:
            target_dim = target_dims['vision_embed_dim']
            adapted_tensors = self._adapt_vision_dimensions(adapted_tensors, target_dim)
        
        # Audio dimension adaptation  
        if 'audio_embed_dim' in target_dims:
            target_dim = target_dims['audio_embed_dim']
            adapted_tensors = self._adapt_audio_dimensions(adapted_tensors, target_dim)
        
        # Fusion dimension adaptation
        if 'fusion_hidden_dim' in target_dims:
            target_dim = target_dims['fusion_hidden_dim']
            adapted_tensors = self._adapt_fusion_dimensions(adapted_tensors, target_dim)
        
        return adapted_tensors
    
    def _adapt_vision_dimensions(self, tensors: Dict[str, torch.Tensor], target_dim: int) -> Dict[str, torch.Tensor]:
        """Adapt vision model dimensions."""
        current_dim = self.analysis['inferred_dimensions'].get('vision_embed_dim')
        if current_dim is None or current_dim == target_dim:
            return tensors
        
        logger.info(f"Adapting vision dimensions from {current_dim} to {target_dim}")
        
        # Adapt key vision tensors
        vision_keys_to_adapt = [
            'vision.vit.norm.weight', 'vision.vit.norm.bias',
            'vision.vit.cls_token', 'vision.vit.pos_embed'
        ]
        
        for key in vision_keys_to_adapt:
            if key in tensors:
                tensor = tensors[key]
                if 'norm' in key and tensor.numel() == current_dim:
                    # For norm layers, interpolate or truncate
                    if target_dim > current_dim:
                        # Pad with mean values
                        pad_size = target_dim - current_dim
                        mean_val = tensor.mean().item()
                        if tensor.ndim == 1:
                            padding = torch.full((pad_size,), mean_val, dtype=tensor.dtype)
                            tensors[key] = torch.cat([tensor, padding])
                        else:
                            # Handle multi-dimensional case
                            padding_shape = list(tensor.shape)
                            padding_shape[-1] = pad_size
                            padding = torch.full(padding_shape, mean_val, dtype=tensor.dtype)
                            tensors[key] = torch.cat([tensor, padding], dim=-1)
                    else:
                        # Truncate
                        tensors[key] = tensor[:target_dim] if tensor.ndim == 1 else tensor[..., :target_dim]
        
        # Adapt transformer blocks
        for key in list(tensors.keys()):
            if 'vision.vit.blocks.' in key and any(x in key for x in ['qkv.weight', 'qkv.bias', 'proj.weight', 'proj.bias']):
                tensors[key] = self._adapt_attention_tensor(tensors[key], current_dim, target_dim, key)
            elif 'vision.vit.blocks.' in key and any(x in key for x in ['mlp.', 'norm']):
                tensors[key] = self._adapt_mlp_tensor(tensors[key], current_dim, target_dim, key)
        
        return tensors
    
    def _adapt_audio_dimensions(self, tensors: Dict[str, torch.Tensor], target_dim: int) -> Dict[str, torch.Tensor]:
        """Adapt audio model dimensions."""
        # Find current audio dimension
        current_dim = None
        for key in ['audio.speech_recognizer.encoder.input_proj.weight', 'audio.sound_classifier.encoder.input_proj.weight']:
            if key in tensors:
                current_dim = tensors[key].shape[0]
                break
        
        if current_dim is None or current_dim == target_dim:
            return tensors
        
        logger.info(f"Adapting audio dimensions from {current_dim} to {target_dim}")
        
        # Adapt audio tensors
        for key in list(tensors.keys()):
            if ('audio.speech_recognizer.' in key or 'audio.sound_classifier.' in key or 'audio.emotion_detector.' in key):
                tensor = tensors[key]
                if 'input_proj.weight' in key and tensor.shape[0] == current_dim:
                    tensors[key] = self._resize_linear_weight(tensor, (target_dim, tensor.shape[1]))
                elif 'input_proj.bias' in key and tensor.shape[0] == current_dim:
                    tensors[key] = self._resize_tensor(tensor, (target_dim,))
                elif any(x in key for x in ['norm', 'linear']) and current_dim in tensor.shape:
                    tensors[key] = self._adapt_generic_tensor(tensor, current_dim, target_dim)
        
        return tensors
    
    def _adapt_fusion_dimensions(self, tensors: Dict[str, torch.Tensor], target_dim: int) -> Dict[str, torch.Tensor]:
        """Adapt fusion model dimensions."""
        current_dim = self.analysis['inferred_dimensions'].get('fusion_hidden_dim')
        if current_dim is None or current_dim == target_dim:
            return tensors
        
        logger.info(f"Adapting fusion dimensions from {current_dim} to {target_dim}")
        
        fusion_keys = ['model.q_proj', 'model.k_proj', 'model.v_proj', 'model.out_proj']
        for base_key in fusion_keys:
            weight_key = f"{base_key}.weight"
            bias_key = f"{base_key}.bias"
            
            if weight_key in tensors:
                tensors[weight_key] = self._resize_linear_weight(
                    tensors[weight_key], (target_dim, target_dim)
                )
            if bias_key in tensors:
                tensors[bias_key] = self._resize_tensor(tensors[bias_key], (target_dim,))
        
        return tensors
    
    def _resize_linear_weight(self, tensor: torch.Tensor, target_shape: Tuple[int, int]) -> torch.Tensor:
        """Resize linear layer weight with intelligent interpolation."""
        current_shape = tensor.shape
        if current_shape == target_shape:
            return tensor
        
        target_out, target_in = target_shape
        current_out, current_in = current_shape
        
        # Handle output dimension
        if target_out != current_out:
            if target_out > current_out:
                # Pad with Xavier-like initialization
                pad_size = target_out - current_out
                std = (2.0 / (current_in + target_out)) ** 0.5
                padding = torch.randn(pad_size, current_in, dtype=tensor.dtype) * std
                tensor = torch.cat([tensor, padding], dim=0)
            else:
                # Truncate
                tensor = tensor[:target_out, :]
        
        # Handle input dimension
        if target_in != current_in:
            if target_in > current_in:
                # Pad with Xavier-like initialization
                pad_size = target_in - current_in
                std = (2.0 / (target_in + tensor.shape[0])) ** 0.5
                padding = torch.randn(tensor.shape[0], pad_size, dtype=tensor.dtype) * std
                tensor = torch.cat([tensor, padding], dim=1)
            else:
                # Truncate
                tensor = tensor[:, :target_in]
        
        return tensor
    
    def _resize_tensor(self, tensor: torch.Tensor, target_shape: Tuple[int, ...]) -> torch.Tensor:
        """Resize tensor with interpolation or truncation."""
        if tensor.shape == target_shape:
            return tensor
        
        if len(target_shape) == 1:
            target_size = target_shape[0]
            current_size = tensor.shape[0]
            
            if target_size > current_size:
                # Pad with mean value
                mean_val = tensor.mean().item()
                pad_size = target_size - current_size
                padding = torch.full((pad_size,) + tensor.shape[1:], mean_val, dtype=tensor.dtype)
                return torch.cat([tensor, padding], dim=0)
            else:
                # Truncate
                return tensor[:target_size]
        
        # For higher dimensions, use interpolation
        return torch.nn.functional.interpolate(
            tensor.unsqueeze(0).unsqueeze(0), 
            size=target_shape, 
            mode='nearest'
        ).squeeze(0).squeeze(0)
    
    def _adapt_attention_tensor(self, tensor: torch.Tensor, current_dim: int, target_dim: int, key: str) -> torch.Tensor:
        """Adapt attention-related tensors."""
        if 'qkv.weight' in key:
            # QKV weight has shape [3*embed_dim, embed_dim]
            return self._resize_linear_weight(tensor, (3 * target_dim, target_dim))
        elif 'qkv.bias' in key:
            # QKV bias has shape [3*embed_dim]
            return self._resize_tensor(tensor, (3 * target_dim,))
        elif 'proj.weight' in key:
            return self._resize_linear_weight(tensor, (target_dim, target_dim))
        elif 'proj.bias' in key:
            return self._resize_tensor(tensor, (target_dim,))
        return tensor
    
    def _adapt_mlp_tensor(self, tensor: torch.Tensor, current_dim: int, target_dim: int, key: str) -> torch.Tensor:
        """Adapt MLP and normalization tensors."""
        if 'norm' in key and tensor.numel() == current_dim:
            return self._resize_tensor(tensor, (target_dim,))
        elif 'mlp.0.weight' in key or 'mlp.fc1.weight' in key:
            # First MLP layer: [hidden_dim, embed_dim] -> [target_hidden, target_dim]
            mlp_ratio = tensor.shape[0] // current_dim
            target_hidden = target_dim * mlp_ratio
            return self._resize_linear_weight(tensor, (target_hidden, target_dim))
        elif 'mlp.0.bias' in key or 'mlp.fc1.bias' in key:
            mlp_ratio = tensor.shape[0] // current_dim
            target_hidden = target_dim * mlp_ratio
            return self._resize_tensor(tensor, (target_hidden,))
        elif 'mlp.3.weight' in key or 'mlp.fc2.weight' in key:
            # Second MLP layer: [embed_dim, hidden_dim] -> [target_dim, target_hidden]
            mlp_ratio = tensor.shape[1] // current_dim
            target_hidden = target_dim * mlp_ratio
            return self._resize_linear_weight(tensor, (target_dim, target_hidden))
        elif 'mlp.3.bias' in key or 'mlp.fc2.bias' in key:
            return self._resize_tensor(tensor, (target_dim,))
        return tensor
    
    def _adapt_generic_tensor(self, tensor: torch.Tensor, current_dim: int, target_dim: int) -> torch.Tensor:
        """Generic tensor dimension adaptation."""
        shape = list(tensor.shape)
        for i, dim in enumerate(shape):
            if dim == current_dim:
                shape[i] = target_dim
        return self._resize_tensor(tensor, tuple(shape))
    
    def save_repaired_model(self, output_dir: Optional[str] = None, 
                          dimension_overrides: Optional[Dict[str, int]] = None) -> str:
        """Save repaired model with adapted dimensions and tensor-level fixes."""
        if output_dir is None:
            output_dir = str(self.model_dir / "repaired")
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Start with tensor-level repairs for specific mismatches
        tensors_to_save = self.repair_tensors()
        
        # Apply additional dimension adaptations if requested
        if dimension_overrides:
            tensors_to_save = self.adapt_dimensions(dimension_overrides, tensors_to_save)
        
        # Add missing components
        missing_components = self.repair_missing_components()
        for prefix, component in missing_components.items():
            component_state = component.state_dict()
            for param_name, param_tensor in component_state.items():
                full_key = f"{prefix}.{param_name}"
                tensors_to_save[full_key] = param_tensor
            logger.info(f"Added missing component: {prefix}")
        
        # Save repaired checkpoint
        output_checkpoint = output_path / "model.safetensors"
        save_file(tensors_to_save, str(output_checkpoint))
        
        # Copy and repair config
        import shutil
        shutil.copy2(self.config_path, output_path / "config.json")
        
        # Apply config repairs to the copied file
        with open(output_path / "config.json", 'r') as f:
            config = json.load(f)
        
        # Update config dimensions to match repaired tensors
        if self.tensor_repairs_needed:
            if 'vision.vit.norm' in self.tensor_repairs_needed:
                config['vision_config']['embed_dim'] = self.tensor_repairs_needed['vision.vit.norm']['target_dim']
                logger.info(f"Updated vision embed_dim to {config['vision_config']['embed_dim']}")
            
            if 'fusion_attention' in self.tensor_repairs_needed:
                fusion_dim = self.tensor_repairs_needed['fusion_attention']['target_dim']
                if 'multimodal_config' not in config:
                    config['multimodal_config'] = {}
                config['multimodal_config']['fusion_hidden_dim'] = fusion_dim
                logger.info(f"Updated fusion hidden_dim to {fusion_dim}")
        
        # Apply standard config repairs
        self.repair_config_file(output_path / "config.json")
        
        logger.info(f"Repaired model saved to {output_path}")
        return str(output_path)


    def repair_config_file(self, config_path: Path) -> bool:
        """Repair config.json file with updated dimensions."""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Update based on detected dimensions
            inferred = self.analysis['inferred_dimensions']
            
            if 'vision_embed_dim' in inferred:
                config['vision_config']['embed_dim'] = inferred['vision_embed_dim']
                logger.info(f"Updated vision embed_dim to {inferred['vision_embed_dim']}")
            
            if 'audio_speech_embed_dim' in inferred:
                config['audio_config']['embed_dim'] = inferred['audio_speech_embed_dim']
                logger.info(f"Updated audio embed_dim to {inferred['audio_speech_embed_dim']}")
            
            if 'fusion_hidden_dim' in inferred:
                if 'multimodal_config' not in config:
                    config['multimodal_config'] = {}
                config['multimodal_config']['fusion_hidden_dim'] = inferred['fusion_hidden_dim']
                logger.info(f"Updated fusion hidden_dim to {inferred['fusion_hidden_dim']}")
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            logger.info("Config.json successfully repaired")
            return True
            
        except Exception as e:
            logger.error(f"Failed to repair config: {e}")
            return False


def repair_model(model_dir: str, output_dir: Optional[str] = None, 
                target_dimensions: Optional[Dict[str, int]] = None) -> str:
    """High-level function to repair a LISA model with mismatched parameters."""
    repairer = ModelRepairer(model_dir)
    
    # Print diagnosis
    diagnosis = repairer.diagnose()
    logger.info("Model Diagnosis:")
    for suggestion in diagnosis['repair_suggestions']:
        logger.info(f"  - {suggestion}")
    
    # Apply repairs
    return repairer.save_repaired_model(output_dir, target_dimensions)
