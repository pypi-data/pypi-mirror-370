"""
Utility functions for MedLLM package

This module provides utility functions for environment setup, device detection,
dependency checking, and other common operations.
"""

import os
import sys
import json
import subprocess
import platform
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import importlib.util

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False


def detect_device() -> str:
    """
    Automatically detect the best available device for training.
    
    Returns:
        Device string: 'cuda', 'mps', or 'cpu'
    """
    if TORCH_AVAILABLE:
        if torch.cuda.is_available():
            return "cuda"
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            return "mps"
    
    return "cpu"


def get_device_info() -> Dict[str, Any]:
    """
    Get detailed information about available devices.
    
    Returns:
        Dictionary with device information
    """
    info = {
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_version": sys.version,
        "torch_available": TORCH_AVAILABLE
    }
    
    if TORCH_AVAILABLE:
        info["torch_version"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        info["mps_available"] = hasattr(torch.backends, 'mps') and torch.backends.mps.is_available()
        
        if torch.cuda.is_available():
            info["cuda_device_count"] = torch.cuda.device_count()
            info["cuda_device_name"] = torch.cuda.get_device_name(0)
            info["cuda_memory"] = torch.cuda.get_device_properties(0).total_memory / 1e9
    
    return info


def check_dependencies(required_packages: Optional[List[str]] = None) -> Dict[str, bool]:
    """
    Check if required packages are installed.
    
    Args:
        required_packages: List of package names to check
        
    Returns:
        Dictionary mapping package names to availability status
    """
    if required_packages is None:
        required_packages = [
            "torch", "transformers", "datasets", "accelerate", 
            "peft", "trl", "sklearn", "numpy", "pandas"
        ]
    
    availability = {}
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            availability[package] = True
        except ImportError:
            availability[package] = False
    
    return availability


def check_optional_dependencies() -> Dict[str, bool]:
    """
    Check availability of optional dependencies.
    
    Returns:
        Dictionary with optional dependency status
    """
    optional_deps = {
        "unsloth": False,
        "raganything": False,
        "lightrag": False,
        "bitsandbytes": False,
        "wandb": False,
        "chromadb": False
    }
    
    for dep in optional_deps:
        try:
            importlib.import_module(dep)
            optional_deps[dep] = True
        except ImportError:
            pass
    
    return optional_deps


def setup_environment(
    mode: str = "check",
    device: Optional[str] = None,
    install_extras: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Setup the development environment.
    
    Args:
        mode: Setup mode ('check', 'install', 'setup')
        device: Target device for optimization
        install_extras: List of extra dependencies to install
        
    Returns:
        Setup status information
    """
    if device is None:
        device = detect_device()
    
    setup_info = {
        "device": device,
        "mode": mode,
        "status": "success",
        "messages": []
    }
    
    if mode == "check":
        # Just check current status
        deps = check_dependencies()
        optional_deps = check_optional_dependencies()
        device_info = get_device_info()
        
        setup_info.update({
            "dependencies": deps,
            "optional_dependencies": optional_deps,
            "device_info": device_info
        })
        
        missing_deps = [dep for dep, available in deps.items() if not available]
        if missing_deps:
            setup_info["status"] = "missing_dependencies"
            setup_info["messages"].append(f"Missing required dependencies: {missing_deps}")
    
    elif mode in ["install", "setup"]:
        # Install dependencies
        try:
            # Basic installation
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-e", "."
            ], check=True, capture_output=True)
            
            # Install extras if specified
            if install_extras:
                for extra in install_extras:
                    subprocess.run([
                        sys.executable, "-m", "pip", "install", f"medllm-finetune-rag[{extra}]"
                    ], check=True, capture_output=True)
            
            setup_info["messages"].append("Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            setup_info["status"] = "error"
            setup_info["messages"].append(f"Installation failed: {e}")
    
    return setup_info


def download_model(
    model_name: str,
    cache_dir: Optional[str] = None,
    use_hf_transfer: bool = True
) -> str:
    """
    Download a model from HuggingFace Hub.
    
    Args:
        model_name: HuggingFace model name
        cache_dir: Directory to cache the model
        use_hf_transfer: Whether to use hf_transfer for faster downloads
        
    Returns:
        Path to downloaded model
    """
    if use_hf_transfer:
        os.environ["HF_HUB_ENABLE_HF_TRANSFER"] = "1"
    
    try:
        from transformers import AutoTokenizer, AutoModelForCausalLM
        
        # Download tokenizer and model
        tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True
        )
        
        model = AutoModelForCausalLM.from_pretrained(
            model_name,
            cache_dir=cache_dir,
            trust_remote_code=True,
            torch_dtype=torch.float16 if TORCH_AVAILABLE else None
        )
        
        # Return cache directory path
        if cache_dir:
            return cache_dir
        else:
            from transformers.utils import TRANSFORMERS_CACHE
            return TRANSFORMERS_CACHE
            
    except Exception as e:
        raise RuntimeError(f"Failed to download model {model_name}: {e}")


def create_sample_data(
    output_path: str = "sample_data.json",
    num_samples: int = 10
) -> str:
    """
    Create sample training data for medical LLM.
    
    Args:
        output_path: Path to save sample data
        num_samples: Number of sample records to generate
        
    Returns:
        Path to created sample data file
    """
    sample_templates = [
        {
            "instruction": "Extract medical entities from the following clinical text.",
            "input": "Patient presents with acute chest pain and shortness of breath. ECG shows ST elevation.",
            "output": "Medical entities:\n- Symptom: acute chest pain\n- Symptom: shortness of breath\n- Test: ECG\n- Finding: ST elevation"
        },
        {
            "instruction": "Identify the relationship between medical concepts in this text.",
            "input": "Hypertension is a risk factor for cardiovascular disease.",
            "output": "Relationship: hypertension -> risk_factor_for -> cardiovascular disease"
        },
        {
            "instruction": "Summarize the patient's condition and treatment plan.",
            "input": "45-year-old male with diabetes mellitus type 2, prescribed metformin 500mg twice daily.",
            "output": "Patient: 45-year-old male\nCondition: Diabetes mellitus type 2\nTreatment: Metformin 500mg twice daily"
        }
    ]
    
    # Generate samples by repeating and varying templates
    samples = []
    for i in range(num_samples):
        template = sample_templates[i % len(sample_templates)]
        sample = template.copy()
        sample["id"] = f"sample_{i+1}"
        samples.append(sample)
    
    # Save to file
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    
    return str(output_file)


def validate_data_format(data_path: str) -> Tuple[bool, List[str]]:
    """
    Validate training data format.
    
    Args:
        data_path: Path to data file
        
    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []
    
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return False, [f"Invalid JSON format: {e}"]
    except FileNotFoundError:
        return False, [f"Data file not found: {data_path}"]
    
    if not isinstance(data, list):
        errors.append("Data should be a list of records")
        return False, errors
    
    required_fields = ["instruction", "input", "output"]
    
    for i, record in enumerate(data):
        if not isinstance(record, dict):
            errors.append(f"Record {i} should be a dictionary")
            continue
        
        for field in required_fields:
            if field not in record:
                errors.append(f"Record {i} missing required field: {field}")
            elif not isinstance(record[field], str):
                errors.append(f"Record {i} field '{field}' should be a string")
    
    is_valid = len(errors) == 0
    return is_valid, errors


def get_model_size(model_name: str) -> Optional[str]:
    """
    Estimate model size from model name.
    
    Args:
        model_name: HuggingFace model name
        
    Returns:
        Estimated size string or None if unknown
    """
    name_lower = model_name.lower()
    
    size_indicators = {
        "7b": "~7B parameters",
        "4b": "~4B parameters", 
        "3b": "~3B parameters",
        "1.5b": "~1.5B parameters",
        "0.5b": "~0.5B parameters",
        "small": "Small (~100M-1B parameters)",
        "base": "Base (~1B-7B parameters)",
        "large": "Large (~7B+ parameters)"
    }
    
    for indicator, size in size_indicators.items():
        if indicator in name_lower:
            return size
    
    return None


def format_memory_size(bytes_size: int) -> str:
    """
    Format memory size in human-readable format.
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def get_system_info() -> Dict[str, Any]:
    """
    Get comprehensive system information.
    
    Returns:
        System information dictionary
    """
    info = {
        "platform": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "processor": platform.processor()
        },
        "python": {
            "version": sys.version,
            "executable": sys.executable
        },
        "environment": dict(os.environ)
    }
    
    # Add device information
    info["device"] = get_device_info()
    
    # Add dependency information
    info["dependencies"] = check_dependencies()
    info["optional_dependencies"] = check_optional_dependencies()
    
    return info
