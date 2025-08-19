# Changelog

All notable changes to the MedLLM Fine-tuning RAG project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2024-01-20

### Fixed
- Updated author email address to correct contact information
- Fixed PyPI package metadata for proper distribution

### Changed
- Updated package configuration with correct maintainer contact

## [0.1.0] - 2024-01-20

### Added
- Initial release of MedLLM Fine-tuning RAG toolkit
- Support for Qwen3-4B-Thinking model fine-tuning
- Unsloth integration for 2x faster training with 70% less VRAM
- RAG-Anything integration for multimodal retrieval-augmented generation
- Multi-platform support (Mac M2/MPS, CUDA, CPU)
- Comprehensive CLI interface with `medllm` command
- Configuration management with device-specific optimizations
- Medical data processing and evaluation metrics
- HuggingFace Hub integration for model sharing
- LoRA and QLoRA support for efficient fine-tuning
- Comprehensive documentation and examples

### Features
- **Core Training Classes:**
  - `MedicalLLMTrainer`: Main training class with Unsloth acceleration
  - `MedicalDataProcessor`: Medical data preprocessing and format conversion
  - `MedicalRAGSystem`: RAG system with RAG-Anything backend
  - `UniversalMedicalTrainer`: Configuration-driven universal trainer

- **Evaluation Tools:**
  - `EntityEvaluator`: Named entity recognition evaluation
  - `RelationEvaluator`: Relation extraction evaluation  
  - `MedicalNERREEvaluator`: Combined NER and RE evaluation

- **CLI Commands:**
  - `medllm train`: Quick training with automatic configuration
  - `medllm eval`: Model evaluation with multiple metrics
  - `medllm infer`: Interactive inference with thinking mode
  - `medllm config`: Configuration generation and management
  - `medllm setup`: Project setup and environment initialization
  - `medllm data`: Data validation and sample generation
  - `medllm rag`: RAG system management

- **High-level API:**
  - `quick_train()`: One-line training function
  - `quick_evaluate()`: Simple model evaluation
  - `quick_inference()`: Easy inference with thinking support
  - `create_trainer()`: Flexible trainer creation
  - `create_rag_system()`: RAG system initialization

- **Configuration Templates:**
  - Device-specific configs (CUDA, MPS, CPU)
  - Training templates (quick, full, research, production)
  - Auto-detection of optimal settings

- **Platform Optimizations:**
  - Mac M2/M3 with MPS acceleration
  - NVIDIA CUDA with QLoRA support
  - CPU-only fallback mode
  - Memory-efficient training configurations

### Dependencies
- Core: PyTorch, Transformers, Datasets, Accelerate, PEFT, TRL
- Optional: Unsloth, RAG-Anything, BitsAndBytes, Weights & Biases
- Development: Black, Flake8, Pytest
- Visualization: Matplotlib, Seaborn

### Installation
```bash
# Basic installation
pip install medllm-finetune-rag

# With all features
pip install medllm-finetune-rag[all]

# Specific features
pip install medllm-finetune-rag[unsloth,rag,gpu]
```

### Quick Start
```python
from medllm import quick_train, quick_evaluate

# Train a model
trainer = quick_train("medical_data.json")

# Evaluate the model  
results = quick_evaluate("./medllm_output", "test_data.json")
```

### CLI Usage
```bash
# Setup new project
medllm setup my_medical_project

# Train with auto-configuration
medllm train data.json --device auto

# Evaluate model
medllm eval ./medllm_output test_data.json

# Interactive inference
medllm infer ./medllm_output "Patient presents with chest pain"
```
