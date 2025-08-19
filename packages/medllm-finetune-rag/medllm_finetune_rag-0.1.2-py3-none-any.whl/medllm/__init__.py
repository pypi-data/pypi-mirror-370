"""
MedLLM: Medical Large Language Model Fine-tuning Toolkit
========================================================

A comprehensive toolkit for fine-tuning medical large language models 
with RAG (Retrieval-Augmented Generation) capabilities.

Key Features:
- Support for Qwen3-4B-Thinking and other medical LLMs
- Efficient fine-tuning with LoRA and Unsloth acceleration
- RAG-Anything integration for enhanced knowledge retrieval
- Multi-platform support (Mac M2, CUDA, CPU)
- Comprehensive evaluation metrics for medical NLP tasks

Quick Start:
    >>> from medllm import MedicalLLMTrainer, MedicalDataProcessor
    >>> 
    >>> # Initialize trainer
    >>> trainer = MedicalLLMTrainer(
    ...     model_name="Qwen/Qwen3-4B-Thinking-2507",
    ...     use_unsloth=True
    ... )
    >>> 
    >>> # Process data
    >>> processor = MedicalDataProcessor()
    >>> processed_data = processor.load_and_process("data.json")
    >>> 
    >>> # Train model
    >>> trainer.train(processed_data)

For more information, visit: https://github.com/chenxingqiang/medllm-finetune-rag
"""

from .medical_llm_trainer import MedicalLLMTrainer
from .data_processing import MedicalDataProcessor, MedicalRecord, Entity, Relation
from .medical_rag_system import MedicalRAGSystem
from .evaluation_metrics import (
    EntityEvaluator, 
    RelationEvaluator, 
    MedicalNERREEvaluator
)
from .huggingface_uploader import HuggingFaceUploader
from .universal_trainer import UniversalMedicalTrainer

# High-level API
from .api import (
    quick_train,
    quick_evaluate,
    quick_inference,
    create_trainer,
    create_rag_system
)

# Configuration and utilities
from .config import (
    load_config,
    get_default_config,
    create_config_for_device
)

from .utils import (
    setup_environment,
    detect_device,
    download_model,
    check_dependencies
)

__version__ = "0.1.2"
__author__ = "Xingqiang Chen"
__email__ = "joy66777@gmail.com"
__license__ = "MIT"

# Main API classes - what users will primarily interact with
__all__ = [
    # Core training and processing classes
    "MedicalLLMTrainer",
    "MedicalDataProcessor", 
    "MedicalRAGSystem",
    "UniversalMedicalTrainer",
    
    # Data structures
    "MedicalRecord",
    "Entity", 
    "Relation",
    
    # Evaluation tools
    "EntityEvaluator",
    "RelationEvaluator", 
    "MedicalNERREEvaluator",
    
    # Deployment and sharing
    "HuggingFaceUploader",
    
    # High-level convenience functions
    "quick_train",
    "quick_evaluate", 
    "quick_inference",
    "create_trainer",
    "create_rag_system",
    
    # Configuration and utilities
    "load_config",
    "get_default_config", 
    "create_config_for_device",
    "setup_environment",
    "detect_device",
    "download_model",
    "check_dependencies",
    
    # Version info
    "__version__",
]

# Package metadata
__package_info__ = {
    "name": "medllm-finetune-rag",
    "version": __version__,
    "description": "A comprehensive toolkit for fine-tuning medical large language models with RAG capabilities",
    "author": __author__,
    "author_email": __email__,
    "license": __license__,
    "url": "https://github.com/chenxingqiang/medllm-finetune-rag",
    "keywords": ["medical", "llm", "fine-tuning", "rag", "qwen", "healthcare", "nlp", "ai"],
    "python_requires": ">=3.8",
}

# Compatibility and feature flags
FEATURES = {
    "unsloth": False,  # Will be set to True if unsloth is available
    "rag": False,      # Will be set to True if RAG dependencies are available
    "gpu": False,      # Will be set to True if GPU libraries are available
}

# Try to detect available features
try:
    import unsloth
    FEATURES["unsloth"] = True
except ImportError:
    pass

try:
    import raganything
    import lightrag
    FEATURES["rag"] = True
except ImportError:
    pass

try:
    import bitsandbytes
    import torch
    if torch.cuda.is_available():
        FEATURES["gpu"] = True
except ImportError:
    pass

# Export feature flags
__all__.extend(["FEATURES"])