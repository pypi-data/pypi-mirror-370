from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from safetensors.torch import load_file
import torch


def _load_config_dict(model_dir: Path) -> Dict[str, Any]:
    cfg_path = model_dir / "config.json"
    if cfg_path.exists():
        try:
            return json.loads(cfg_path.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def _infer_architecture_details(tensors: Dict[str, torch.Tensor]) -> Dict[str, Any]:
    """Enhanced architecture detection from checkpoint tensors."""
    details = {}
    
    # Vision ViT architecture detection
    vit_norm = tensors.get('vision.vit.norm.weight')
    if vit_norm is not None:
        details['vision_embed_dim'] = int(vit_norm.numel())
    
    # Try to infer ViT depth from transformer blocks
    vit_blocks = [k for k in tensors.keys() if k.startswith('vision.vit.blocks.') and k.endswith('.norm1.weight')]
    if vit_blocks:
        # Extract block numbers
        block_nums = [int(k.split('.')[3]) for k in vit_blocks]
        details['vision_depth'] = max(block_nums) + 1 if block_nums else 12
    
    # Infer number of heads from attention projections
    qkv_weight = tensors.get('vision.vit.blocks.0.attn.qkv.weight')
    if qkv_weight is not None and 'vision_embed_dim' in details:
        embed_dim = details['vision_embed_dim']
        # QKV weight shape should be [3*embed_dim, embed_dim]
        if qkv_weight.shape[0] == 3 * embed_dim:
            # Assume head_dim = 64 (common ViT practice)
            details['vision_num_heads'] = embed_dim // 64
    
    # Audio architecture detection
    # Speech recognizer
    sr_input_proj = tensors.get('audio.speech_recognizer.encoder.input_proj.weight')
    if sr_input_proj is not None:
        details['audio_speech_embed_dim'] = int(sr_input_proj.shape[0])
    
    # Sound classifier  
    sc_input_proj = tensors.get('audio.sound_classifier.encoder.input_proj.weight')
    if sc_input_proj is not None:
        details['audio_sound_embed_dim'] = int(sc_input_proj.shape[0])
    
    # Try to infer audio transformer depth
    sr_layers = [k for k in tensors.keys() if k.startswith('audio.speech_recognizer.encoder.transformer.layers.') and k.endswith('.norm1.weight')]
    if sr_layers:
        layer_nums = [int(k.split('.')[5]) for k in sr_layers]
        details['audio_speech_depth'] = max(layer_nums) + 1 if layer_nums else 6
    
    sc_layers = [k for k in tensors.keys() if k.startswith('audio.sound_classifier.encoder.transformer.layers.') and k.endswith('.norm1.weight')]
    if sc_layers:
        layer_nums = [int(k.split('.')[5]) for k in sc_layers]
        details['audio_sound_depth'] = max(layer_nums) + 1 if layer_nums else 4
    
    # Fusion model detection
    fusion_out_proj = tensors.get('model.out_proj.weight')
    if fusion_out_proj is not None and fusion_out_proj.ndim == 2:
        if fusion_out_proj.shape[0] == fusion_out_proj.shape[1]:
            details['fusion_hidden_dim'] = int(fusion_out_proj.shape[0])
    
    # Object detector classes
    obj_cls_head = None
    for k, v in tensors.items():
        if k.startswith('vision.object_detector.') and 'cls_head' in k and v.ndim == 4:
            # Conv2d weight shape: [out_channels, in_channels, kernel_h, kernel_w]
            # For classification head: [3 * num_classes, ...]
            if v.shape[2] == 1 and v.shape[3] == 1:  # 1x1 conv
                num_classes = v.shape[0] // 3  # 3 anchors per position
                details['object_detection_classes'] = num_classes
                break
    
    return details


def _analyze_dimension_mismatches(tensors: Dict[str, torch.Tensor], config: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze potential dimension mismatches between saved tensors and config."""
    mismatches = {}
    arch_details = _infer_architecture_details(tensors)
    
    # Compare with config
    vision_config = config.get('vision_config', {})
    audio_config = config.get('audio_config', {})
    
    if 'vision_embed_dim' in arch_details:
        config_embed_dim = vision_config.get('embed_dim', 768)
        if arch_details['vision_embed_dim'] != config_embed_dim:
            mismatches['vision_embed_dim'] = {
                'saved': arch_details['vision_embed_dim'],
                'config': config_embed_dim,
                'recommended': arch_details['vision_embed_dim']
            }
    
    if 'audio_speech_embed_dim' in arch_details:
        config_embed_dim = audio_config.get('embed_dim', 256)
        if arch_details['audio_speech_embed_dim'] != config_embed_dim:
            mismatches['audio_embed_dim'] = {
                'saved': arch_details['audio_speech_embed_dim'],
                'config': config_embed_dim,
                'recommended': arch_details['audio_speech_embed_dim']
            }
    
    return mismatches


def _generate_model_repair_suggestions(tensors: Dict[str, torch.Tensor], mismatches: Dict[str, Any]) -> List[str]:
    """Generate specific suggestions for fixing the model."""
    suggestions = []
    
    if 'vision_embed_dim' in mismatches:
        mismatch = mismatches['vision_embed_dim']
        suggestions.append(
            f"Vision ViT dimension mismatch: saved model uses {mismatch['saved']} but config expects {mismatch['config']}. "
            f"Recommend updating vision_config.embed_dim to {mismatch['recommended']} in config.json"
        )
    
    if 'audio_embed_dim' in mismatches:
        mismatch = mismatches['audio_embed_dim']
        suggestions.append(
            f"Audio model dimension mismatch: saved model uses {mismatch['saved']} but config expects {mismatch['config']}. "
            f"Recommend updating audio_config.embed_dim to {mismatch['recommended']} in config.json"
        )
    
    # Check for missing model components
    saved_prefixes = set()
    for k in tensors.keys():
        parts = k.split('.')
        if len(parts) >= 2:
            saved_prefixes.add('.'.join(parts[:2]))
    
    expected_prefixes = {
        'vision.vit', 'vision.object_detector', 'vision.depth_estimator',
        'audio.speech_recognizer', 'audio.sound_classifier', 'audio.vad_model', 'audio.emotion_detector',
        'model'  # fusion model
    }
    
    missing_prefixes = expected_prefixes - saved_prefixes
    if missing_prefixes:
        suggestions.append(f"Missing model components in checkpoint: {', '.join(sorted(missing_prefixes))}")
    
    unexpected_prefixes = saved_prefixes - expected_prefixes
    if unexpected_prefixes:
        suggestions.append(f"Unexpected model components in checkpoint: {', '.join(sorted(unexpected_prefixes))}")
    
    return suggestions


def summarize_checkpoint(model_dir_or_file: str) -> Dict[str, Any]:
    """Enhanced checkpoint inspector with dimension detection and repair suggestions.

    Returns a comprehensive report with:
      - saved_param_count
      - saved_prefixes and counts  
      - inferred_dimensions (detailed architecture detection)
      - dimension_mismatches (compared to config)
      - repair_suggestions (specific fixes needed)
    """
    path = Path(model_dir_or_file)
    if path.is_dir():
        ckpt_path = path / "model.safetensors"
        model_dir = path
    else:
        ckpt_path = path
        model_dir = path.parent

    tensors = load_file(str(ckpt_path))
    saved_param_count = int(sum(int(t.numel()) for t in tensors.values()))

    # Group by first two segments as in saved keys
    def top2(key: str) -> str:
        parts = key.split('.')
        return '.'.join(parts[:2]) if len(parts) >= 2 else parts[0]

    prefix_to_count: Dict[str, int] = {}
    for k, t in tensors.items():
        p = top2(k)
        prefix_to_count[p] = prefix_to_count.get(p, 0) + int(t.numel())

    # Enhanced architecture analysis
    arch_details = _infer_architecture_details(tensors)
    cfg = _load_config_dict(model_dir)
    
    # Analyze mismatches
    mismatches = _analyze_dimension_mismatches(tensors, cfg)
    suggestions = _generate_model_repair_suggestions(tensors, mismatches)

    return {
        'checkpoint_path': str(ckpt_path),
        'saved_param_count': saved_param_count,
        'saved_prefix_param_counts': prefix_to_count,
        'inferred_dimensions': arch_details,
        'dimension_mismatches': mismatches,
        'repair_suggestions': suggestions,
        'config': cfg,
    }


