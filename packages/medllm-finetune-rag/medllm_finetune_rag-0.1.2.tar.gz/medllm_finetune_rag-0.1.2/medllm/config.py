"""
Configuration management for MedLLM package

This module handles configuration loading, validation, and device-specific
configuration generation for medical LLM fine-tuning.
"""

import os
import yaml
from typing import Dict, Any, Optional, Union
from pathlib import Path
import torch

from .utils import detect_device


def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid YAML
    """
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        try:
            config = yaml.safe_load(f)
            return config or {}
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in config file {config_path}: {e}")


def get_default_config() -> Dict[str, Any]:
    """
    Get default configuration for medical LLM training.
    
    Returns:
        Default configuration dictionary
    """
    return {
        "model": {
            "name": "Qwen/Qwen3-4B-Thinking-2507",
            "torch_dtype": "float16",
            "device_map": "auto",
            "load_in_4bit": False,
            "load_in_8bit": False,
            "trust_remote_code": True
        },
        "training": {
            "output_dir": "./medllm_output",
            "num_train_epochs": 3,
            "per_device_train_batch_size": 2,
            "per_device_eval_batch_size": 2,
            "gradient_accumulation_steps": 4,
            "learning_rate": 2e-4,
            "max_grad_norm": 1.0,
            "warmup_steps": 100,
            "logging_steps": 10,
            "save_steps": 500,
            "eval_steps": 500,
            "save_total_limit": 3,
            "load_best_model_at_end": True,
            "metric_for_best_model": "eval_loss",
            "greater_is_better": False,
            "dataloader_num_workers": 0,
            "remove_unused_columns": False,
            "optim": "adamw_torch",
            "report_to": ["wandb"],
            "run_name": "medllm_finetune",
            "max_seq_length": 2048
        },
        "lora": {
            "r": 32,
            "lora_alpha": 32,
            "target_modules": [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ],
            "lora_dropout": 0.0,
            "bias": "none",
            "task_type": "CAUSAL_LM"
        },
        "data": {
            "max_seq_length": 2048,
            "train_on_responses_only": True,
            "response_template": "<|im_start|>assistant",
            "instruction_template": "<|im_start|>user"
        },
        "rag": {
            "enabled": False,
            "working_dir": "./rag_workspace",
            "api_key_env": "OPENAI_API_KEY",
            "model_name": "gpt-4o-mini",
            "parser": "mineru",
            "parse_method": "auto",
            "chunk_size": 1200,
            "chunk_overlap": 100,
            "top_k": 5,
            "search_modes": ["naive", "local", "global", "hybrid"],
            "multimodal": {
                "image_enabled": True,
                "table_enabled": True,
                "equation_enabled": True
            }
        },
        "wandb": {
            "project": "medllm-finetune",
            "name": "qwen3-medical-training",
            "tags": ["medical", "qwen3", "thinking", "lora"],
            "notes": "Fine-tuning Qwen3-4B-Thinking model for medical applications"
        }
    }


def create_config_for_device(device: str) -> Dict[str, Any]:
    """
    Create device-specific configuration.
    
    Args:
        device: Target device ('cuda', 'mps', 'cpu')
        
    Returns:
        Device-optimized configuration
    """
    config = get_default_config()
    
    if device == "mps":
        # Mac M2/M3 optimizations
        config["model"].update({
            "torch_dtype": "float16",
            "device_map": None,  # Manual device placement for MPS
            "load_in_4bit": False,  # Not supported on MPS
            "load_in_8bit": False
        })
        config["training"].update({
            "per_device_train_batch_size": 1,
            "per_device_eval_batch_size": 1,
            "gradient_accumulation_steps": 8,
            "dataloader_num_workers": 0,
            "bf16": False,
            "fp16": True
        })
        
    elif device == "cuda":
        # CUDA GPU optimizations
        config["model"].update({
            "torch_dtype": "float16",
            "device_map": "auto",
            "load_in_4bit": True,  # Enable QLoRA
        })
        config["training"].update({
            "per_device_train_batch_size": 4,
            "per_device_eval_batch_size": 4,
            "gradient_accumulation_steps": 2,
            "dataloader_num_workers": 4,
            "bf16": True,
            "fp16": False
        })
        
    elif device == "cpu":
        # CPU-only configuration
        config["model"].update({
            "torch_dtype": "float32",
            "device_map": None,
            "load_in_4bit": False,
            "load_in_8bit": False
        })
        config["training"].update({
            "per_device_train_batch_size": 1,
            "per_device_eval_batch_size": 1,
            "gradient_accumulation_steps": 16,
            "dataloader_num_workers": 2,
            "bf16": False,
            "fp16": False,
            "max_seq_length": 1024  # Reduced for CPU
        })
        config["data"]["max_seq_length"] = 1024
    
    return config


def save_config(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to save configuration file
    """
    config_file = Path(config_path)
    config_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False, indent=2)


def validate_config(config: Dict[str, Any]) -> bool:
    """
    Validate configuration dictionary.
    
    Args:
        config: Configuration to validate
        
    Returns:
        True if configuration is valid
        
    Raises:
        ValueError: If configuration is invalid
    """
    required_sections = ["model", "training", "lora"]
    
    for section in required_sections:
        if section not in config:
            raise ValueError(f"Missing required configuration section: {section}")
    
    # Validate model section
    model_config = config["model"]
    if "name" not in model_config:
        raise ValueError("Model name is required in model configuration")
    
    # Validate training section
    training_config = config["training"]
    required_training_keys = ["output_dir", "learning_rate", "num_train_epochs"]
    for key in required_training_keys:
        if key not in training_config:
            raise ValueError(f"Missing required training parameter: {key}")
    
    # Validate LoRA section
    lora_config = config["lora"]
    if "r" not in lora_config or "lora_alpha" not in lora_config:
        raise ValueError("LoRA rank (r) and alpha are required")
    
    return True


def merge_configs(*configs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple configuration dictionaries.
    Later configs override earlier ones.
    
    Args:
        *configs: Configuration dictionaries to merge
        
    Returns:
        Merged configuration dictionary
    """
    merged = {}
    
    for config in configs:
        for key, value in config.items():
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                # Recursively merge nested dictionaries
                merged[key] = merge_configs(merged[key], value)
            else:
                merged[key] = value
    
    return merged


def get_config_template(template_name: str) -> Dict[str, Any]:
    """
    Get predefined configuration templates.
    
    Args:
        template_name: Name of the template
        
    Returns:
        Configuration template
        
    Available templates:
        - quick: Fast training for testing
        - full: Full training configuration
        - research: Research-oriented configuration
        - production: Production deployment configuration
    """
    base_config = get_default_config()
    
    templates = {
        "quick": {
            "training": {
                "num_train_epochs": 1,
                "max_steps": 100,
                "per_device_train_batch_size": 1,
                "gradient_accumulation_steps": 8,
                "save_steps": 50,
                "eval_steps": 50,
                "logging_steps": 5
            }
        },
        "full": {
            "training": {
                "num_train_epochs": 5,
                "per_device_train_batch_size": 4,
                "gradient_accumulation_steps": 2,
                "save_steps": 200,
                "eval_steps": 200,
                "logging_steps": 10
            }
        },
        "research": {
            "training": {
                "num_train_epochs": 10,
                "per_device_train_batch_size": 2,
                "gradient_accumulation_steps": 4,
                "save_steps": 100,
                "eval_steps": 100,
                "logging_steps": 5,
                "load_best_model_at_end": True,
                "evaluation_strategy": "steps",
                "save_strategy": "steps"
            },
            "wandb": {
                "project": "medllm-research",
                "tags": ["research", "medical", "qwen3"]
            }
        },
        "production": {
            "training": {
                "num_train_epochs": 3,
                "per_device_train_batch_size": 8,
                "gradient_accumulation_steps": 1,
                "save_steps": 500,
                "eval_steps": 500,
                "logging_steps": 20,
                "save_total_limit": 1,
                "report_to": []  # Disable wandb for production
            }
        }
    }
    
    if template_name not in templates:
        available = ", ".join(templates.keys())
        raise ValueError(f"Unknown template '{template_name}'. Available: {available}")
    
    return merge_configs(base_config, templates[template_name])


def auto_detect_config() -> Dict[str, Any]:
    """
    Automatically detect and create optimal configuration based on system.
    
    Returns:
        Auto-detected configuration
    """
    device = detect_device()
    config = create_config_for_device(device)
    
    # Detect available memory and adjust batch sizes
    if device == "cuda" and torch.cuda.is_available():
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1e9  # GB
        if gpu_memory < 8:
            config["training"]["per_device_train_batch_size"] = 1
            config["training"]["gradient_accumulation_steps"] = 8
        elif gpu_memory < 16:
            config["training"]["per_device_train_batch_size"] = 2
            config["training"]["gradient_accumulation_steps"] = 4
    
    elif device == "mps":
        # Conservative settings for Apple Silicon
        config["training"]["per_device_train_batch_size"] = 1
        config["training"]["gradient_accumulation_steps"] = 8
    
    return config
