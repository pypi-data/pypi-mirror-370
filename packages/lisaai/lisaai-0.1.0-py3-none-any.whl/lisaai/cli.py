#!/usr/bin/env python3
"""
Enhanced CLI for LISA AI library with model repair and fine-tuning capabilities.

Usage examples:
    # Inspect model and diagnose issues
    python -m lisaai inspect ./models/lisa_youtube_kenya/LISA\ V3.5/

    # Repair model automatically
    python -m lisaai repair ./models/lisa_youtube_kenya/LISA\ V3.5/ --output ./repaired_model/

    # Load and test inference
    python -m lisaai infer ./models/lisa_youtube_kenya/LISA\ V3.5/ --image test.jpg --audio test.wav

    # Fine-tune model
    python -m lisaai finetune ./models/lisa_youtube_kenya/LISA\ V3.5/ --data ./training_data/ --epochs 5
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

import torch
import numpy as np

from . import (
    load_model, infer, inspect_model, repair_model_interactive, 
    FineTuner, FineTuningConfig, ModelRepairTrainer, LoadOptions
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def setup_cli_parser():
    """Setup comprehensive CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="LISA AI Library CLI - Model Repair and Fine-tuning Tools",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Inspect command
    inspect_parser = subparsers.add_parser('inspect', help='Inspect model and diagnose issues')
    inspect_parser.add_argument('model_dir', help='Path to model directory')
    inspect_parser.add_argument('--output', '-o', help='Output file for detailed report (JSON)')
    inspect_parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    # Repair command
    repair_parser = subparsers.add_parser('repair', help='Repair model dimension mismatches')
    repair_parser.add_argument('model_dir', help='Path to model directory')
    repair_parser.add_argument('--output', '-o', help='Output directory for repaired model')
    repair_parser.add_argument('--vision-dim', type=int, help='Target vision embedding dimension')
    repair_parser.add_argument('--audio-dim', type=int, help='Target audio embedding dimension')
    repair_parser.add_argument('--fusion-dim', type=int, help='Target fusion hidden dimension')
    repair_parser.add_argument('--interactive', action='store_true', help='Interactive repair mode')
    
    # Inference command
    infer_parser = subparsers.add_parser('infer', help='Run inference on model')
    infer_parser.add_argument('model_dir', help='Path to model directory')
    infer_parser.add_argument('--image', help='Path to input image')
    infer_parser.add_argument('--audio', help='Path to input audio file')
    infer_parser.add_argument('--device', default='auto', help='Device to use (auto, cpu, cuda)')
    infer_parser.add_argument('--output', '-o', help='Output file for results (JSON)')
    infer_parser.add_argument('--auto-repair', action='store_true', help='Auto-repair model if needed')
    
    # Fine-tuning command
    finetune_parser = subparsers.add_parser('finetune', help='Fine-tune model')
    finetune_parser.add_argument('model_dir', help='Path to model directory')
    finetune_parser.add_argument('--data', required=True, help='Path to training data directory')
    finetune_parser.add_argument('--output', '-o', default='./finetuned_model', help='Output directory')
    finetune_parser.add_argument('--epochs', type=int, default=5, help='Number of training epochs')
    finetune_parser.add_argument('--batch-size', type=int, default=8, help='Batch size')
    finetune_parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    finetune_parser.add_argument('--device', default='auto', help='Device to use')
    finetune_parser.add_argument('--fusion-only', action='store_true', help='Fine-tune fusion layer only')
    finetune_parser.add_argument('--auto-repair', action='store_true', help='Auto-repair model before training')
    
    # Demo command
    demo_parser = subparsers.add_parser('demo', help='Run interactive demo')
    demo_parser.add_argument('model_dir', help='Path to model directory')
    demo_parser.add_argument('--device', default='auto', help='Device to use')
    demo_parser.add_argument('--steps', type=int, default=5, help='Number of demo steps')
    demo_parser.add_argument('--auto-repair', action='store_true', help='Auto-repair model if needed')
    
    return parser


def cmd_inspect(args):
    """Handle inspect command."""
    logger.info(f"Inspecting model: {args.model_dir}")
    
    try:
        report = inspect_model(args.model_dir)
        
        if args.verbose:
            print(json.dumps(report, indent=2))
        else:
            # Print summary
            print(f"\nLISA Model Inspection Report")
            print(f"=" * 40)
            print(f"Model Path: {args.model_dir}")
            print(f"Total Parameters: {report.get('saved_param_count', 'Unknown'):,}")
            
            inferred_dims = report.get('inferred_dimensions', {})
            if inferred_dims:
                print(f"Detected Dimensions:")
                for key, value in inferred_dims.items():
                    print(f"  {key}: {value}")
            
            mismatches = report.get('dimension_mismatches', {})
            if mismatches:
                print(f"\nDimension Mismatches:")
                for key, mismatch in mismatches.items():
                    print(f"  {key}: saved={mismatch['saved']}, config={mismatch['config']}")
            
            suggestions = report.get('repair_suggestions', [])
            if suggestions:
                print(f"\nRepair Suggestions ({len(suggestions)}):")
                for i, suggestion in enumerate(suggestions[:5], 1):
                    print(f"  {i}. {suggestion}")
                if len(suggestions) > 5:
                    print(f"  ... and {len(suggestions) - 5} more")
            else:
                print(f"\n[SUCESS] No issues found!")
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"\nDetailed report saved to: {args.output}")
        
        return 0 if not report.get('repair_suggestions') else 1
        
    except Exception as e:
        logger.error(f"Inspection failed: {e}")
        return 1


def cmd_repair(args):
    """Handle repair command."""
    logger.info(f"Repairing model: {args.model_dir}")
    
    try:
        if args.interactive:
            repaired_path = repair_model_interactive(args.model_dir, args.output)
        else:
            from .repair import repair_model
            
            # Build dimension overrides if specified
            dimension_overrides = {}
            if args.vision_dim:
                dimension_overrides['vision_embed_dim'] = args.vision_dim
            if args.audio_dim:
                dimension_overrides['audio_embed_dim'] = args.audio_dim
            if args.fusion_dim:
                dimension_overrides['fusion_hidden_dim'] = args.fusion_dim
            
            repaired_path = repair_model(
                args.model_dir, 
                args.output, 
                dimension_overrides if dimension_overrides else None
            )
        
        print(f"\n[SUCESS] Model repaired successfully!")
        print(f"Repaired model saved to: {repaired_path}")
        return 0
        
    except Exception as e:
        logger.error(f"Repair failed: {e}")
        return 1


def cmd_infer(args):
    """Handle inference command."""
    logger.info(f"Running inference with model: {args.model_dir}")
    
    async def run_inference():
        try:
            # Load model
            options = LoadOptions(
                model_dir=args.model_dir,
                device=args.device,
                auto_repair=args.auto_repair
            )
            model = load_model(options)
            
            # Prepare inputs
            video_frame = None
            audio_chunk = None
            
            if args.image:
                logger.info(f"Loading image: {args.image}")
                try:
                    import cv2
                    image = cv2.imread(args.image)
                    if image is None:
                        raise ValueError(f"Cannot load image: {args.image}")
                    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    video_frame = image
                except ImportError:
                    logger.warning("OpenCV not available, using dummy image")
                    video_frame = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
            
            if args.audio:
                logger.info(f"Loading audio: {args.audio}")
                try:
                    import librosa
                    audio, sr = librosa.load(args.audio, sr=16000)
                    # Convert to mel spectrogram
                    mel_spec = librosa.feature.melspectrogram(
                        y=audio, sr=sr, n_mels=80, hop_length=160, win_length=400
                    )
                    mel_spec = librosa.power_to_db(mel_spec, ref=np.max)
                    audio_chunk = mel_spec.T  # [time, n_mels]
                except ImportError:
                    logger.warning("librosa not available, using dummy audio")
                    audio_chunk = np.random.randn(100, 80).astype(np.float32)
            
            # Use dummy data if no inputs provided
            if video_frame is None:
                video_frame = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
            if audio_chunk is None:
                audio_chunk = np.random.randn(100, 80).astype(np.float32)
            
            # Run inference
            logger.info("Running inference...")
            results = await infer(model, video_frame=video_frame, audio_chunk=audio_chunk)
            
            # Process results - handle both dict and LISAResponse types
            if isinstance(results, dict) and 'error' in results:
                print(f"[FAILED] Inference failed: {results['error']}")
                return 1
            elif hasattr(results, 'error') and results.error:
                print(f"[FAILED] Inference failed: {results.error}")
                return 1
            
            print(f"\n[SUCESS] Inference completed successfully!")
            
            # Handle different result types
            if hasattr(results, '__dict__'):
                # LISAResponse object
                print(f"Response type: {type(results).__name__}")
                if hasattr(results, 'vision_summary') and results.vision_summary:
                    print(f"  Vision: {results.vision_summary}")
                if hasattr(results, 'audio_summary') and results.audio_summary:
                    print(f"  Audio: {results.audio_summary}")
                if hasattr(results, 'response_text') and results.response_text:
                    print(f"  Text: {results.response_text}")
            elif isinstance(results, dict):
                # Dictionary results
                print(f"Results summary:")
                for key, value in results.items():
                    if isinstance(value, torch.Tensor):
                        print(f"  {key}: tensor {value.shape} (device: {value.device})")
                    elif isinstance(value, dict):
                        print(f"  {key}: {len(value)} items")
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, torch.Tensor):
                                print(f"    {subkey}: tensor {subvalue.shape}")
                            else:
                                print(f"    {subkey}: {type(subvalue).__name__}")
                    else:
                        print(f"  {key}: {type(value).__name__}")
            else:
                print(f"Result type: {type(results).__name__}")
            
            # Save results if requested
            if args.output:
                # Convert tensors to lists for JSON serialization
                serializable_results = {}
                for key, value in results.items():
                    if isinstance(value, torch.Tensor):
                        serializable_results[key] = {
                            'shape': list(value.shape),
                            'dtype': str(value.dtype),
                            'device': str(value.device),
                            'data': value.detach().cpu().tolist() if value.numel() < 1000 else "too_large"
                        }
                    elif isinstance(value, dict):
                        serializable_results[key] = {}
                        for subkey, subvalue in value.items():
                            if isinstance(subvalue, torch.Tensor):
                                serializable_results[key][subkey] = {
                                    'shape': list(subvalue.shape),
                                    'dtype': str(subvalue.dtype),
                                    'device': str(subvalue.device)
                                }
                    else:
                        serializable_results[key] = str(value)
                
                with open(args.output, 'w') as f:
                    json.dump(serializable_results, f, indent=2)
                print(f"Results saved to: {args.output}")
            
            return 0
            
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return asyncio.run(run_inference())


def cmd_finetune(args):
    """Handle fine-tuning command."""
    logger.info(f"Fine-tuning model: {args.model_dir}")
    
    try:
        # Load model
        options = LoadOptions(
            model_dir=args.model_dir,
            device=args.device,
            auto_repair=args.auto_repair
        )
        model = load_model(options)
        
        # Setup fine-tuning config
        config = FineTuningConfig(
            learning_rate=args.lr,
            batch_size=args.batch_size,
            num_epochs=args.epochs,
            fine_tune_fusion_only=args.fusion_only
        )
        
        # Create trainer
        trainer = ModelRepairTrainer(model, config)
        trainer.setup_training(args.output)
        
        # Load training data (simplified - would need real data loader)
        logger.warning("Using synthetic training data - implement real data loading for production")
        train_data = []
        for i in range(100):  # 100 synthetic batches
            vision_batch = torch.randn(args.batch_size, 3, 112, 112)
            audio_batch = torch.randn(args.batch_size, 100, 80)
            train_data.append((vision_batch, audio_batch))
        
        # Run training
        results = trainer.repair_and_train(train_data, output_dir=args.output)
        
        print(f"\n[SUCESS] Fine-tuning completed!")
        print(f"Total steps: {results['total_steps']}")
        print(f"Final model saved to: {results['final_model_path']}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Fine-tuning failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


def cmd_demo(args):
    """Handle demo command."""
    logger.info(f"Running demo with model: {args.model_dir}")
    
    async def run_demo():
        try:
            # Load model
            options = LoadOptions(
                model_dir=args.model_dir,
                device=args.device,
                auto_repair=args.auto_repair
            )
            model = load_model(options)
            
            print(f"\n LISA AI Demo Starting...")
            print(f"Model: {args.model_dir}")
            print(f"Device: {args.device}")
            print(f"Steps: {args.steps}")
            print("-" * 50)
            
            # Get model info
            if hasattr(model, 'get_model_info'):
                info = model.get_model_info()
                print(f"Model Info:")
                print(f"  Total Parameters: {info.get('total_parameters', 'Unknown'):,}")
                print(f"  Architecture: {info.get('architecture', 'Unknown')}")
                detected_dims = info.get('detected_dimensions', {})
                if detected_dims:
                    print(f"  Detected Dimensions: {detected_dims}")
            
            # Run demo steps
            for step in range(args.steps):
                print(f"\n--- Demo Step {step + 1}/{args.steps} ---")
                
                # Create synthetic inputs
                vision_frame = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
                audio_chunk = np.random.randn(100, 80).astype(np.float32)
                
                # Run inference
                result = await infer(model, video_frame=vision_frame, audio_chunk=audio_chunk)
                
                if 'error' in result:
                    print(f"[FAILED] Step {step + 1} failed: {result['error']}")
                else:
                    print(f"[SUCESS] Step {step + 1} completed")
                    print(f"   Generated {len(result)} output components")
                    
                    # Show some sample outputs
                    for key, value in list(result.items())[:3]:
                        if isinstance(value, torch.Tensor):
                            print(f"   {key}: {value.shape}")
                        elif isinstance(value, dict):
                            print(f"   {key}: {len(value)} items")
                
                # Small delay for demo effect
                await asyncio.sleep(0.5)
            
            print(f"\n[SUCESSFULL] Demo completed successfully!")
            return 0
            
        except Exception as e:
            logger.error(f"Demo failed: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    return asyncio.run(run_demo())


def main():
    """Main CLI entry point."""
    parser = setup_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Dispatch to command handlers
    command_handlers = {
        'inspect': cmd_inspect,
        'repair': cmd_repair, 
        'infer': cmd_infer,
        'finetune': cmd_finetune,
        'demo': cmd_demo
    }
    
    handler = command_handlers.get(args.command)
    if handler:
        return handler(args)
    else:
        logger.error(f"Unknown command: {args.command}")
        return 1


if __name__ == '__main__':
    sys.exit(main())


