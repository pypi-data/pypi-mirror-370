"""lisaai: High-level APIs for LISA Vision+Audio model

This package wraps the in-repo `lisa` implementation with stable, clean
APIs for loading, inference, diagnostics, fine-tuning utilities, and
automatic model repair capabilities.

Key Features:
- Automatic dimension detection and model repair
- Independent runtime that doesn't rely on main codebase
- Enhanced fine-tuning and training capabilities
- Comprehensive model inspection and diagnostics
- Robust error handling and dimension adaptation
"""

from .api import load_model, infer, self_drive, inspect_model, repair_model_interactive, LoadOptions
from .checkpoint import inspect_checkpoint, compare_param_counts, resave_checkpoint
from .training import (
    av_contrastive_loss,
    av_sync_loss,
    masked_modeling_loss,
    FineTuner,
    FineTuningConfig,
    ModelRepairTrainer,
)
from .runtime import build_runtime_from_checkpoint, LisaAIRuntime
from .repair import ModelRepairer, repair_model
from .inspector import summarize_checkpoint

__version__ = "1.0.0"
__author__ = "LISA Team"

__all__ = [
    # Main API functions
    "load_model",
    "infer", 
    "self_drive",
    "inspect_model",
    "repair_model_interactive",
    "LoadOptions",
    
    # Checkpoint utilities
    "inspect_checkpoint",
    "compare_param_counts", 
    "resave_checkpoint",
    
    # Training and fine-tuning
    "av_contrastive_loss",
    "av_sync_loss",
    "masked_modeling_loss",
    "FineTuner",
    "FineTuningConfig", 
    "ModelRepairTrainer",
    
    # Runtime and repair
    "build_runtime_from_checkpoint",
    "LisaAIRuntime",
    "ModelRepairer",
    "repair_model",
    "summarize_checkpoint",
]


