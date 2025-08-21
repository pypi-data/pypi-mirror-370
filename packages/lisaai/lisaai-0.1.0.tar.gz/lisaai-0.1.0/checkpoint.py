from __future__ import annotations

import os
from pathlib import Path
from typing import Optional, Dict, Any

from safetensors.torch import load_file

from .api import LoadOptions, load_model
from .inspector import summarize_checkpoint


def inspect_checkpoint(model_safetensors: str) -> Dict[str, Any]:
    """Independent inspector that does not rely on project tools.

    If given a directory, it will look for model.safetensors and config.json.
    """
    return summarize_checkpoint(model_safetensors)


def compare_param_counts(model_dir: str) -> Dict[str, Any]:
    """Pure checkpoint-based count; independent of runtime modules.

    Returns:
      - checkpoint_saved_params
      - saved_prefix_param_counts
    """
    rep = summarize_checkpoint(model_dir)
    return {
        'checkpoint_saved_params': rep.get('saved_param_count'),
        'saved_prefix_param_counts': rep.get('saved_prefix_param_counts', {}),
        'inferred_dimensions': rep.get('inferred_dimensions', {}),
    }


def resave_checkpoint(model_dir: str) -> str:
    """Re-save using runtime saver if `lisa` package is importable.

    Falls back to no-op if lisa is unavailable.
    """
    try:
        from lisa.core.model_saver import save_lisa_model
        from lisa import LISA, LISAConfig
        cfg = LISAConfig.default("full")
        os.environ['LISA_MODEL_PATH'] = model_dir
        model = LISA(cfg, mode='full')
        save_lisa_model(
            vision_processor=model.vision_processor,
            audio_processor=model.audio_processor,
            save_path=model_dir,
            optimizer_state_dict=None,
            full_model=getattr(model, 'multimodal_fusion', None).fusion_model if hasattr(model, 'multimodal_fusion') else None,
        )
        return str(Path(model_dir) / 'model.safetensors')
    except Exception:
        # No-op if project runtime isn't present
        return str(Path(model_dir) / 'model.safetensors')


