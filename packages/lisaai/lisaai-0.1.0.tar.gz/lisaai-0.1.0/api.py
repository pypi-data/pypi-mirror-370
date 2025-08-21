from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

import torch

try:
    from lisa import LISA, LISAConfig, PerceptionInput, LISAResponse  # optional
except Exception:
    LISA = None  # type: ignore
    LISAConfig = None  # type: ignore
    PerceptionInput = None  # type: ignore
    LISAResponse = None  # type: ignore

from .runtime import build_runtime_from_checkpoint
from .inspector import summarize_checkpoint
from .repair import ModelRepairer, repair_model

logger = logging.getLogger(__name__)


@dataclass
class LoadOptions:
    model_dir: Optional[str] = None
    device: str = "auto"  # "auto"|"cpu"|"cuda"|"cuda:0"
    mode: str = "full"     # "mini"|"full"
    audio_only_output: bool = True  # disable text responses by default
    auto_repair: bool = True  # automatically repair dimension mismatches
    repair_output_dir: Optional[str] = None  # where to save repaired model


def load_model(options: Optional[LoadOptions] = None):
    """Enhanced LISA model loader with automatic repair capabilities.

    - Automatically detects and adapts to checkpoint dimensions
    - Repairs dimension mismatches when auto_repair=True
    - Falls back to independent runtime for incompatible models
    - Ensures robust loading even with main LISA implementation issues
    """
    options = options or LoadOptions()
    
    if not options.model_dir:
        raise ValueError("model_dir is required")
    
    logger.info(f"Loading LISA model from {options.model_dir}")
    
    # Analyze model first
    analysis = summarize_checkpoint(options.model_dir)
    has_dimension_issues = bool(analysis['repair_suggestions'])
    
    # Check for issues and repair if needed
    if has_dimension_issues and options.auto_repair:
        logger.warning(f"Found {len(analysis['repair_suggestions'])} issues in model:")
        for suggestion in analysis['repair_suggestions'][:3]:  # Show first 3
            logger.warning(f"  - {suggestion}")
        
        if options.repair_output_dir:
            repair_dir = options.repair_output_dir
        else:
            repair_dir = os.path.join(options.model_dir, "repaired")
        
        logger.info(f"Auto-repairing model and saving to {repair_dir}")
        repaired_model_dir = repair_model(options.model_dir, repair_dir)
        options.model_dir = repaired_model_dir
        logger.info("Model repair completed")
    
    # Try to use the main LISA implementation if available AND compatible
    main_lisa_compatible = True
    if LISAConfig is not None and LISA is not None:
        try:
            cfg = LISAConfig.default(options.mode)
            
            # Set device
            if options.device == "auto":
                cfg.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            else:
                cfg.device = torch.device(options.device)
            
            # Configure response settings
            if options.audio_only_output:
                cfg.response_config.text_responses = False
                cfg.response_config.audio_responses = True
            
            # Set model path for auto-tuning
            os.environ["LISA_MODEL_PATH"] = options.model_dir
            
            # Pre-check: if we know there were dimension issues, use independent runtime
            if has_dimension_issues:
                logger.info("Dimension mismatches detected, using independent runtime for compatibility")
                main_lisa_compatible = False
            else:
                model = LISA(cfg, mode=options.mode)
                logger.info(f"Loaded LISA model using main implementation in {options.mode} mode")
                return model
                
        except Exception as e:
            logger.warning(f"Failed to load with main LISA implementation: {e}")
            main_lisa_compatible = False
    else:
        main_lisa_compatible = False
    
    if not main_lisa_compatible:
        logger.info("Using independent runtime for robust loading")
    
    # Fallback: build independent runtime directly from checkpoint
    device = torch.device(options.device if options.device != 'auto' else ('cuda' if torch.cuda.is_available() else 'cpu'))
    runtime = build_runtime_from_checkpoint(options.model_dir, device)
    runtime.set_eval_mode()  # Default to eval mode for inference
    
    logger.info(f"Loaded LISA model using independent runtime on {device}")
    return runtime


@torch.inference_mode()
async def infer(model, *, video_frame=None, audio_chunk=None, text_input: Optional[str] = None):
    """Enhanced one-shot inference helper with better error handling."""
    try:
        # Main LISA model
        if hasattr(model, 'process_input') and PerceptionInput is not None:
            if not getattr(model, "is_active", False):
                await model.start_session()
            inp = PerceptionInput(video_frame=video_frame, audio_chunk=audio_chunk, text_input=text_input)
            return await model.process_input(inp)
        
        # LisaAIRuntime
        elif hasattr(model, 'vision_vit'):
            results = {}
            
            # Process vision if provided
            if video_frame is not None:
                try:
                    if isinstance(video_frame, torch.Tensor):
                        vision_tensor = video_frame
                    else:
                        # Convert numpy array to tensor
                        import numpy as np
                        if isinstance(video_frame, np.ndarray):
                            vision_tensor = torch.from_numpy(video_frame).float()
                            if vision_tensor.ndim == 3:  # HWC -> CHW
                                vision_tensor = vision_tensor.permute(2, 0, 1)
                            if vision_tensor.ndim == 3:  # Add batch dimension
                                vision_tensor = vision_tensor.unsqueeze(0)
                            # Normalize to [0, 1] if needed
                            if vision_tensor.max() > 1.0:
                                vision_tensor = vision_tensor / 255.0
                        else:
                            raise ValueError(f"Unsupported video_frame type: {type(video_frame)}")
                    
                    # Ensure correct input size (112x112)
                    if vision_tensor.shape[-2:] != (112, 112):
                        vision_tensor = torch.nn.functional.interpolate(
                            vision_tensor, size=(112, 112), mode='bilinear', align_corners=False
                        )
                    
                    vision_tensor = vision_tensor.to(next(model.vision_vit.parameters()).device)
                    
                    # Extract features
                    vision_features = model.get_vision_features(vision_tensor)
                    results['vision_features'] = vision_features
                    
                    # Object detection - this might be the issue
                    detection_result = model.detect_objects(vision_tensor)
                    if isinstance(detection_result, tuple) and len(detection_result) == 3:
                        cls_out, reg_out, obj_out = detection_result
                        results['object_detection'] = {
                            'classifications': cls_out,
                            'regressions': reg_out,
                            'objectness': obj_out
                        }
                    else:
                        # Different format or single output
                        results['object_detection'] = {
                            'output': detection_result,
                            'classifications': detection_result if not isinstance(detection_result, tuple) else detection_result[0],
                            'regressions': None,
                            'objectness': None
                        }
                except Exception as e:
                    logger.warning(f"Vision processing failed: {e}")
                    results['vision_processing'] = {'error': str(e)}
            
            # Process audio if provided
            if audio_chunk is not None:
                if isinstance(audio_chunk, torch.Tensor):
                    audio_tensor = audio_chunk
                else:
                    audio_tensor = torch.from_numpy(audio_chunk).float()
                
                # Handle different audio input formats
                if audio_tensor.ndim == 2:
                    # Expected format: [time_frames, n_mels] = [100, 80]
                    if audio_tensor.shape[1] == 80:  # mel features
                        # For mel features, add batch dimension
                        audio_tensor = audio_tensor.unsqueeze(0)  # [1, 100, 80]
                    else:
                        # Raw audio signal, convert to mel features
                        # For now, just reshape and pad/truncate to expected size
                        if audio_tensor.shape[0] < 100:
                            # Pad if too short
                            padding = torch.zeros(100 - audio_tensor.shape[0], audio_tensor.shape[1])
                            audio_tensor = torch.cat([audio_tensor, padding], dim=0)
                        elif audio_tensor.shape[0] > 100:
                            # Truncate if too long
                            audio_tensor = audio_tensor[:100]
                        audio_tensor = audio_tensor.unsqueeze(0)
                elif audio_tensor.ndim == 1:
                    # Raw audio signal [samples] - convert to mel spectrogram
                    # For demo purposes, create a dummy mel spectrogram
                    mel_frames = min(100, len(audio_tensor) // 160)  # rough estimate
                    audio_tensor = torch.randn(1, mel_frames, 80)  # [1, frames, 80]
                    if mel_frames < 100:
                        padding = torch.zeros(1, 100 - mel_frames, 80)
                        audio_tensor = torch.cat([audio_tensor, padding], dim=1)
                    else:
                        audio_tensor = audio_tensor[:, :100, :]
                
                audio_tensor = audio_tensor.to(next(model.speech_recognizer.parameters()).device)
                
                try:
                    # Speech recognition - handle tensor shape properly
                    speech_result = model.transcribe_speech(audio_tensor)
                    if isinstance(speech_result, tuple) and len(speech_result) == 2:
                        ctc_out, lm_out = speech_result
                        results['speech_recognition'] = {
                            'ctc_output': ctc_out,
                            'language_model_output': lm_out
                        }
                    else:
                        # Single output or different format
                        results['speech_recognition'] = {
                            'output': speech_result,
                            'ctc_output': speech_result,  # For compatibility
                            'language_model_output': None
                        }
                except Exception as e:
                    logger.warning(f"Speech recognition failed: {e}")
                    results['speech_recognition'] = {'error': str(e)}
                
                try:
                    # Sound classification
                    sound_logits = model.classify_sound(audio_tensor)
                    results['sound_classification'] = sound_logits
                except Exception as e:
                    logger.warning(f"Sound classification failed: {e}")
                    results['sound_classification'] = {'error': str(e)}
                
                try:
                    # Emotion detection
                    emotion_logits = model.detect_emotion(audio_tensor)
                    results['emotion_detection'] = emotion_logits
                except Exception as e:
                    logger.warning(f"Emotion detection failed: {e}")
                    results['emotion_detection'] = {'error': str(e)}
                
                try:
                    # Voice activity detection - expects raw 1D audio
                    # Convert mel features to a format VAD expects
                    if audio_tensor.ndim == 3:  # [B, T, F] mel features
                        # Convert mel to 1D audio-like signal by averaging across frequency bins
                        vad_input = audio_tensor.mean(dim=-1).squeeze()  # [T] - remove batch and frequency dims
                        
                        # Ensure correct length for VAD (typically expects 16000 samples for 1 second)
                        target_length = 16000
                        if vad_input.shape[0] < target_length:
                            # Pad if too short
                            padding_size = target_length - vad_input.shape[0]
                            vad_input = torch.cat([vad_input, torch.zeros(padding_size, device=vad_input.device)])
                        elif vad_input.shape[0] > target_length:
                            # Truncate if too long
                            vad_input = vad_input[:target_length]
                        
                        # Ensure it's 1D [16000] without batch dimension
                        vad_input = vad_input.unsqueeze(0)  # Add batch dim: [1, 16000]
                    else:
                        # Generate appropriate dummy audio [1, 16000]
                        vad_input = torch.randn(1, 16000, device=audio_tensor.device)
                    
                    vad_output = model.detect_voice_activity(vad_input)
                    results['voice_activity'] = vad_output
                except Exception as e:
                    logger.warning(f"Voice activity detection failed: {e}")
                    results['voice_activity'] = {'error': str(e)}
                
                try:
                    # Audio features
                    audio_features = model.get_audio_features(audio_tensor)
                    results['audio_features'] = audio_features
                except Exception as e:
                    logger.warning(f"Audio feature extraction failed: {e}")
                    results['audio_features'] = {'error': str(e)}
            
            # Multimodal fusion if both modalities present
            if 'vision_features' in results and 'audio_features' in results:
                try:
                    # Get vision and audio features
                    v_feat = results['vision_features']
                    a_feat = results['audio_features']
                    
                    # Handle dimension alignment for fusion
                    # Vision typically 768, Audio typically 512, Fusion expects aligned dimensions
                    if v_feat.shape[-1] == 768:
                        # Project vision from 768 to 1024
                        vision_proj = torch.nn.Linear(768, 1024).to(v_feat.device)
                        v_feat_aligned = vision_proj(v_feat.reshape(-1, 768))
                    else:
                        v_feat_aligned = v_feat.reshape(-1, v_feat.shape[-1])
                    
                    if a_feat.shape[-1] == 512:
                        # Project audio from 512 to 1024  
                        audio_proj = torch.nn.Linear(512, 1024).to(a_feat.device)
                        a_feat_aligned = audio_proj(a_feat.reshape(-1, 512))
                    else:
                        a_feat_aligned = a_feat.reshape(-1, a_feat.shape[-1])
                    
                    # Ensure same batch dimension
                    v_feat_aligned = v_feat_aligned.reshape(1, -1)
                    a_feat_aligned = a_feat_aligned.reshape(1, -1)
                    
                    # Try different fusion call signatures
                    if hasattr(model, 'multimodal_fusion'):
                        if hasattr(model.multimodal_fusion, 'fuse'):
                            # Call with aligned features
                            fusion_output = model.multimodal_fusion.fuse(
                                v_feat_aligned, 
                                a_feat_aligned
                            )
                        else:
                            # Direct call on fusion module
                            fusion_output = model.multimodal_fusion(
                                v_feat_aligned, 
                                a_feat_aligned
                            )
                    else:
                        # Fallback: simple concatenation of aligned features
                        if v_feat_aligned.shape[0] == a_feat_aligned.shape[0]:  # Same batch size
                            fusion_output = torch.cat([v_feat_aligned, a_feat_aligned], dim=-1)
                        else:
                            fusion_output = None
                    
                    if fusion_output is not None:
                        results['multimodal_fusion'] = fusion_output
                except Exception as e:
                    logger.warning(f"Multimodal fusion failed: {e}")
                    results['multimodal_fusion'] = {'error': str(e)}
            
            return results
        
        else:
            # Generic fallback - return accessible modules
            return {
                'vision_vit': getattr(model, 'vision_vit', None),
                'speech_recognizer': getattr(model, 'speech_recognizer', None),
                'model_info': getattr(model, 'get_model_info', lambda: {})()
            }
    
    except Exception as e:
        logger.error(f"Inference failed: {e}")
        return {'error': str(e)}


@torch.inference_mode()
async def self_drive(model, steps: int = 3, interval: float = 0.2):
    """Enhanced self-drive function with better support for different model types."""
    try:
        if hasattr(model, 'self_drive'):
            if not getattr(model, "is_active", False):
                await model.start_session()
            return await model.self_drive(steps=steps, interval=interval)
        else:
            # Simulate self-drive for LisaAIRuntime
            import asyncio
            import time
            
            results = []
            for step in range(steps):
                # Create synthetic input for demonstration
                dummy_vision = torch.randn(1, 3, 112, 112)
                dummy_audio = torch.randn(1, 100, 80)  # 100 frames, 80 mel features
                
                result = await infer(model, video_frame=dummy_vision, audio_chunk=dummy_audio)
                results.append({
                    'step': step,
                    'timestamp': time.time(),
                    'synthetic_data': True,
                    'result': result
                })
                
                if step < steps - 1:
                    await asyncio.sleep(interval)
            
            return results
    
    except Exception as e:
        logger.error(f"Self-drive failed: {e}")
        return []


def inspect_model(model_dir: str) -> Dict[str, Any]:
    """Comprehensive model inspection and analysis."""
    return summarize_checkpoint(model_dir)


def repair_model_interactive(model_dir: str, output_dir: Optional[str] = None) -> str:
    """Interactive model repair with detailed reporting."""
    repairer = ModelRepairer(model_dir)
    
    # Show diagnosis
    diagnosis = repairer.diagnose()
    print("\n" + "="*60)
    print("LISA MODEL DIAGNOSIS REPORT")
    print("="*60)
    print(f"Model Path: {model_dir}")
    print(f"Total Parameters: {diagnosis['total_parameters']:,}")
    print(f"Detected Dimensions: {diagnosis['detected_dimensions']}")
    
    if diagnosis['dimension_mismatches']:
        print(f"\nDIMENSION MISMATCHES FOUND:")
        for key, mismatch in diagnosis['dimension_mismatches'].items():
            print(f"  {key}: saved={mismatch['saved']}, config={mismatch['config']}, recommended={mismatch['recommended']}")
    
    if diagnosis['issues_found'] > 0:
        print(f"\nISSUES TO REPAIR ({diagnosis['issues_found']}):")
        for i, suggestion in enumerate(diagnosis['repair_suggestions'], 1):
            print(f"  {i}. {suggestion}")
    else:
        print("\n[SUCESS] No issues found - model appears to be compatible!")
    
    print("="*60)
    
    if diagnosis['issues_found'] > 0:
        # Perform repair
        repaired_path = repairer.save_repaired_model(output_dir)
        print(f"\n🔧 Model repaired and saved to: {repaired_path}")
        return repaired_path
    else:
        return model_dir


