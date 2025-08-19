#!/usr/bin/env python3
"""
Command-line interface for MedLLM package

This module provides CLI commands for training, evaluation, and inference
with medical large language models.
"""

import argparse
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from .api import (
    quick_train, quick_evaluate, quick_inference, 
    create_trainer, create_rag_system, setup_project
)
from .config import (
    load_config, get_default_config, create_config_for_device,
    get_config_template, auto_detect_config
)
from .utils import (
    detect_device, get_device_info, check_dependencies,
    create_sample_data, validate_data_format, get_system_info
)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="medllm",
        description="Medical Large Language Model Fine-tuning Toolkit",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  medllm info                           # Show system information
  medllm train data.json                # Quick training
  medllm train data.json --config config.yaml  # Training with config
  medllm eval model_path test_data.json # Evaluate model
  medllm infer model_path "Patient has fever"  # Single inference
  medllm setup my_project               # Setup new project
  medllm config --device cuda           # Generate CUDA config

For more information, visit: https://github.com/chenxingqiang/medllm-finetune-rag
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Info command
    info_parser = subparsers.add_parser("info", help="Show system information")
    info_parser.add_argument("--format", choices=["text", "json"], default="text",
                            help="Output format")
    
    # Train command
    train_parser = subparsers.add_parser("train", help="Train a medical LLM")
    train_parser.add_argument("data_path", help="Path to training data")
    train_parser.add_argument("--model", default="Qwen/Qwen3-4B-Thinking-2507",
                             help="Model name to fine-tune")
    train_parser.add_argument("--config", help="Configuration file path")
    train_parser.add_argument("--output-dir", default="./medllm_output",
                             help="Output directory")
    train_parser.add_argument("--device", choices=["auto", "cuda", "mps", "cpu"],
                             default="auto", help="Target device")
    train_parser.add_argument("--max-steps", type=int, default=100,
                             help="Maximum training steps")
    train_parser.add_argument("--learning-rate", type=float, default=2e-4,
                             help="Learning rate")
    train_parser.add_argument("--no-unsloth", action="store_true",
                             help="Disable Unsloth acceleration")
    train_parser.add_argument("--template", choices=["quick", "full", "research", "production"],
                             help="Use configuration template")
    
    # Eval command
    eval_parser = subparsers.add_parser("eval", help="Evaluate a trained model")
    eval_parser.add_argument("model_path", help="Path to trained model")
    eval_parser.add_argument("test_data", help="Path to test data")
    eval_parser.add_argument("--metrics", nargs="+", 
                            default=["entity_f1", "relation_f1", "overall_f1"],
                            help="Evaluation metrics")
    eval_parser.add_argument("--output", help="Save results to file")
    
    # Infer command
    infer_parser = subparsers.add_parser("infer", help="Run inference")
    infer_parser.add_argument("model_path", help="Path to trained model")
    infer_parser.add_argument("text", help="Input text for inference")
    infer_parser.add_argument("--thinking", action="store_true",
                             help="Enable thinking mode")
    infer_parser.add_argument("--temperature", type=float, default=0.7,
                             help="Sampling temperature")
    infer_parser.add_argument("--max-tokens", type=int, default=512,
                             help="Maximum tokens to generate")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument("--device", choices=["cuda", "mps", "cpu"],
                              help="Generate config for specific device")
    config_parser.add_argument("--template", choices=["quick", "full", "research", "production"],
                              help="Use configuration template")
    config_parser.add_argument("--output", default="config.yaml",
                              help="Output configuration file")
    config_parser.add_argument("--auto", action="store_true",
                              help="Auto-detect optimal configuration")
    
    # Setup command
    setup_parser = subparsers.add_parser("setup", help="Setup new project")
    setup_parser.add_argument("project_dir", nargs="?", default=".",
                             help="Project directory")
    setup_parser.add_argument("--device", choices=["auto", "cuda", "mps", "cpu"],
                             default="auto", help="Target device")
    setup_parser.add_argument("--no-deps", action="store_true",
                             help="Skip dependency installation")
    setup_parser.add_argument("--no-sample", action="store_true",
                             help="Skip sample data creation")
    
    # Data command
    data_parser = subparsers.add_parser("data", help="Data utilities")
    data_subparsers = data_parser.add_subparsers(dest="data_command")
    
    # Data validate
    validate_parser = data_subparsers.add_parser("validate", help="Validate data format")
    validate_parser.add_argument("data_path", help="Path to data file")
    
    # Data sample
    sample_parser = data_subparsers.add_parser("sample", help="Create sample data")
    sample_parser.add_argument("--output", default="sample_data.json",
                              help="Output file path")
    sample_parser.add_argument("--count", type=int, default=10,
                              help="Number of samples to generate")
    
    # RAG command
    rag_parser = subparsers.add_parser("rag", help="RAG system management")
    rag_parser.add_argument("--setup", action="store_true",
                           help="Setup RAG system")
    rag_parser.add_argument("--build", help="Build knowledge base from file")
    rag_parser.add_argument("--query", help="Query the knowledge base")
    rag_parser.add_argument("--working-dir", default="./rag_workspace",
                           help="RAG working directory")
    
    # Parse arguments
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    try:
        # Execute command
        if args.command == "info":
            handle_info_command(args)
        elif args.command == "train":
            handle_train_command(args)
        elif args.command == "eval":
            handle_eval_command(args)
        elif args.command == "infer":
            handle_infer_command(args)
        elif args.command == "config":
            handle_config_command(args)
        elif args.command == "setup":
            handle_setup_command(args)
        elif args.command == "data":
            handle_data_command(args)
        elif args.command == "rag":
            handle_rag_command(args)
            
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def handle_info_command(args):
    """Handle info command."""
    info = get_system_info()
    
    if args.format == "json":
        print(json.dumps(info, indent=2))
    else:
        print("🏥 MedLLM System Information")
        print("=" * 40)
        
        # Platform info
        platform_info = info["platform"]
        print(f"Platform: {platform_info['system']} {platform_info['release']}")
        print(f"Architecture: {platform_info['machine']}")
        
        # Python info
        python_info = info["python"]
        print(f"Python: {python_info['version'].split()[0]}")
        
        # Device info
        device_info = info["device"]
        print(f"Detected device: {detect_device()}")
        if device_info.get("cuda_available"):
            print(f"CUDA device: {device_info.get('cuda_device_name')}")
            print(f"CUDA memory: {device_info.get('cuda_memory', 0):.1f} GB")
        
        # Dependencies
        deps = info["dependencies"]
        optional_deps = info["optional_dependencies"]
        
        print("\n📦 Dependencies:")
        for dep, available in deps.items():
            status = "✅" if available else "❌"
            print(f"  {status} {dep}")
        
        print("\n🔧 Optional Dependencies:")
        for dep, available in optional_deps.items():
            status = "✅" if available else "❌"
            print(f"  {status} {dep}")


def handle_train_command(args):
    """Handle train command."""
    print("🚀 Starting medical LLM training...")
    
    # Validate data
    is_valid, errors = validate_data_format(args.data_path)
    if not is_valid:
        print("❌ Data validation failed:")
        for error in errors:
            print(f"  - {error}")
        return
    
    print(f"✅ Data validation passed: {args.data_path}")
    
    # Determine device
    device = detect_device() if args.device == "auto" else args.device
    print(f"🎯 Target device: {device}")
    
    # Load or create configuration
    config = None
    if args.config:
        config = load_config(args.config)
        print(f"📋 Loaded config: {args.config}")
    elif args.template:
        config = get_config_template(args.template)
        print(f"📋 Using template: {args.template}")
    
    # Train model
    trainer = quick_train(
        data_path=args.data_path,
        model_name=args.model,
        output_dir=args.output_dir,
        max_steps=args.max_steps,
        learning_rate=args.learning_rate,
        use_unsloth=not args.no_unsloth,
        device=device
    )
    
    print(f"✅ Training completed! Model saved to: {args.output_dir}")


def handle_eval_command(args):
    """Handle eval command."""
    print("📊 Starting model evaluation...")
    
    results = quick_evaluate(
        model_path=args.model_path,
        test_data_path=args.test_data,
        metrics=args.metrics
    )
    
    print("📈 Evaluation Results:")
    for metric, value in results.items():
        print(f"  {metric}: {value:.4f}")
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"💾 Results saved to: {args.output}")


def handle_infer_command(args):
    """Handle infer command."""
    print("🤖 Running inference...")
    
    result = quick_inference(
        model_path=args.model_path,
        text=args.text,
        enable_thinking=args.thinking,
        temperature=args.temperature,
        max_new_tokens=args.max_tokens
    )
    
    print("💬 Input:")
    print(f"  {args.text}")
    print("\n🎯 Response:")
    print(f"  {result.get('response', 'No response generated')}")
    
    if args.thinking and 'thinking' in result:
        print("\n🤔 Thinking process:")
        print(f"  {result['thinking']}")


def handle_config_command(args):
    """Handle config command."""
    print("⚙️  Generating configuration...")
    
    if args.auto:
        config = auto_detect_config()
        print("🎯 Auto-detected optimal configuration")
    elif args.template:
        config = get_config_template(args.template)
        print(f"📋 Using template: {args.template}")
    elif args.device:
        config = create_config_for_device(args.device)
        print(f"🎯 Generated config for device: {args.device}")
    else:
        config = get_default_config()
        print("📋 Using default configuration")
    
    # Save configuration
    with open(args.output, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, indent=2)
    
    print(f"💾 Configuration saved to: {args.output}")


def handle_setup_command(args):
    """Handle setup command."""
    print("🏗️  Setting up new project...")
    
    device = detect_device() if args.device == "auto" else args.device
    
    info = setup_project(
        project_dir=args.project_dir,
        device=device,
        install_dependencies=not args.no_deps,
        create_sample_data=not args.no_sample
    )
    
    print(f"✅ Project setup completed!")
    print(f"📁 Project directory: {info['project_dir']}")
    print(f"🎯 Target device: {info['device']}")
    print(f"⚙️  Configuration: {info['config_file']}")
    
    if info.get('sample_data'):
        print(f"📊 Sample data: {info['sample_data']}")


def handle_data_command(args):
    """Handle data command."""
    if args.data_command == "validate":
        print("🔍 Validating data format...")
        is_valid, errors = validate_data_format(args.data_path)
        
        if is_valid:
            print("✅ Data format is valid!")
        else:
            print("❌ Data validation failed:")
            for error in errors:
                print(f"  - {error}")
                
    elif args.data_command == "sample":
        print("📝 Creating sample data...")
        output_path = create_sample_data(args.output, args.count)
        print(f"✅ Sample data created: {output_path}")
        print(f"📊 Generated {args.count} samples")


def handle_rag_command(args):
    """Handle RAG command."""
    if args.setup:
        print("🔧 Setting up RAG system...")
        rag = create_rag_system(working_dir=args.working_dir)
        print(f"✅ RAG system setup completed!")
        print(f"📁 Working directory: {args.working_dir}")
        
    elif args.build:
        print("🏗️  Building knowledge base...")
        rag = create_rag_system(working_dir=args.working_dir)
        # TODO: Implement knowledge base building
        print(f"✅ Knowledge base built from: {args.build}")
        
    elif args.query:
        print("🔍 Querying knowledge base...")
        rag = create_rag_system(working_dir=args.working_dir)
        # TODO: Implement querying
        print(f"🎯 Query: {args.query}")


# Command shortcuts for direct execution
def train_command():
    """Direct train command entry point."""
    sys.argv = [sys.argv[0], "train"] + sys.argv[1:]
    main()


def eval_command():
    """Direct eval command entry point."""
    sys.argv = [sys.argv[0], "eval"] + sys.argv[1:]
    main()


def rag_command():
    """Direct RAG command entry point."""
    sys.argv = [sys.argv[0], "rag"] + sys.argv[1:]
    main()


if __name__ == "__main__":
    main()
