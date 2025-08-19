# Medical LLM Fine-tuning with RAG System

A comprehensive PyPI package for fine-tuning large language models on medical literature with entity relationship extraction capabilities, featuring Qwen3-4B-Thinking model integration and advanced RAG-Anything multimodal document processing.

## 📦 Quick Start

```bash
# Install the package
pip install medllm-finetune-rag[all]

# Manual Unsloth installation (for 2x faster training)
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

# Quick training
medllm train medical_data.json

# Or use Python API
python -c "from medllm import quick_train; quick_train('medical_data.json')"
```

## 🚀 Features

### 🤖 Advanced Model Support
- **Qwen3-4B-Thinking Integration**: State-of-the-art reasoning model with thinking capabilities
- **Unsloth Acceleration**: 2x faster training with reduced VRAM usage
- **Thinking Mode**: Support for reasoning-based inference with `<think></think>` tags
- **Multiple Training Formats**: Instruction fine-tuning and NER training formats

### 📄 RAG-Anything Integration
- **Multimodal Document Processing**: PDF, DOCX, images, tables, equations
- **Advanced Parsers**: MinerU and Docling for robust document extraction
- **LightRAG Knowledge Graph**: Graph-based retrieval for enhanced context
- **Multiple Search Modes**: Naive, local, global, and hybrid retrieval strategies

### 🏥 Medical Specialization
- **Medical Entity Extraction**: Specialized for Bacteria, Disease, Evidence entities
- **Relationship Extraction**: Complex medical relationship understanding
- **Domain-Specific Processing**: Optimized for medical literature analysis
- **Evaluation Metrics**: Built-in medical NER evaluation tools

### ⚡ Platform Optimization
- **Apple Silicon Support**: Optimized for Mac M2/M3 with MPS backend
- **CUDA Acceleration**: Full GPU acceleration for NVIDIA cards
- **CPU Fallback**: Reliable CPU-only training option
- **Universal Configuration**: Single config system for all platforms

## 🏗️ Project Structure

```
medllm-finetune-rag/
├── core/                           # Core training modules
│   ├── medical_llm_trainer.py     # Main training class with Unsloth integration
│   ├── data_processing.py         # Data preprocessing and format conversion
│   ├── medical_rag_system.py      # RAG-Anything system implementation
│   ├── evaluation_metrics.py      # Model evaluation tools
│   └── huggingface_uploader.py    # HuggingFace model upload utility
├── config/                        # Configuration files
│   ├── config_mac_m2.yaml        # Mac M2/M3 optimized configuration
│   ├── config_cuda.yaml          # CUDA GPU configuration
│   └── config_cpu.yaml           # CPU-only configuration
├── scripts/                       # Utility scripts
│   ├── setup_environment.py      # Environment setup and verification
│   ├── run_training_pipeline.py  # Legacy training pipeline runner
│   ├── quick_start.sh            # Quick setup script
│   └── setup_qwen3.sh           # Qwen3 specific environment setup
├── docs/                          # Documentation
│   ├── UNIVERSAL_TRAINER_GUIDE.md # Universal trainer documentation
│   ├── README_QWEN3.md          # Qwen3 integration guide
│   └── README_MAC_M2.md         # Mac M2 setup guide
├── examples/                      # Example scripts and demos
│   ├── medical_rag_demo.py       # Comprehensive RAG-Anything demo
│   ├── quick_rag_test.py         # Quick RAG functionality test
│   ├── qwen3_example.py          # Qwen3 model example
│   └── run_mac_m2.py            # Mac M2 optimized runner
├── universal_trainer.py          # Universal training script
├── run.py                        # Simple command wrapper
├── requirements.txt              # Python dependencies
├── .env                          # Environment variables (API keys)
└── README.md                     # This file
```

## 🔧 Installation

### Prerequisites

- Python 3.9-3.13
- PyTorch with appropriate backend (CUDA/MPS/CPU)
- Git and GitHub CLI (optional, for repository management)
- OpenAI API key (optional, for RAG-Anything functionality)

### Quick Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
cd medllm-finetune-rag
   ```

2. **Automated setup** (recommended):
   ```bash
   chmod +x scripts/setup_qwen3.sh
   ./scripts/setup_qwen3.sh
   ```
   
   This will automatically:
   - Create and activate a virtual environment
   - Install all required dependencies including RAG-Anything
   - Set up platform-specific optimizations (Mac M2/CUDA/CPU)
   - Verify the installation

3. **Configure API keys** (optional, for RAG functionality):
   ```bash
   # Create .env file with your API keys
   echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
   echo "HF_TOKEN=your_huggingface_token_here" >> .env
   ```

4. **Quick test**:
   ```bash
   # Test basic functionality
   python examples/quick_rag_test.py
   
   # Test model inference
   python run.py test
   ```

### Manual Installation

```bash
# Core dependencies
pip install torch torchvision torchaudio
pip install transformers>=4.36.0
pip install datasets>=2.14.0
pip install peft>=0.6.0
pip install bitsandbytes>=0.41.0

# Unsloth for efficient training (if compatible)
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
pip install unsloth_zoo
pip install trl>=0.7.0

# Additional utilities
pip install wandb
pip install scikit-learn
pip install numpy pandas
pip install tqdm
pip install PyYAML
```

## 🚀 Quick Start

### 1. Universal Trainer (Recommended)

The universal trainer provides a unified interface for all training operations:

```bash
# Quick inference test
python run.py test

# Training with different configurations
python run.py train          # Mac M2 optimized
python run.py cuda          # CUDA GPU training
python run.py cpu           # CPU-only training

# Training with HuggingFace upload
python run.py train-upload

# Interactive mode
python run.py interactive

# Full pipeline with upload
python run.py full-upload
```

### 2. RAG-Anything Demo

```bash
# Test RAG functionality
python examples/quick_rag_test.py

# Run comprehensive RAG demo
python examples/medical_rag_demo.py
```

### 3. Configuration-Based Training

```bash
# Use specific configuration files
python universal_trainer.py --config config/config_mac_m2.yaml --mode train
python universal_trainer.py --config config/config_cuda.yaml --mode inference
python universal_trainer.py --config config/config_cpu.yaml --mode eval
```

### 4. Medical Training Pipeline

For research and development with full control over each stage:

```bash
# Complete medical pipeline (all stages)
python scripts/run_training_pipeline.py --stage all

# Individual stages
python scripts/run_training_pipeline.py --stage 1    # Data preprocessing
python scripts/run_training_pipeline.py --stage 2    # Model training
python scripts/run_training_pipeline.py --stage 3    # RAG system building
python scripts/run_training_pipeline.py --stage 4    # Evaluation
python scripts/run_training_pipeline.py --stage 5    # Demo inference

# Custom parameters
python scripts/run_training_pipeline.py --stage 2 --model Qwen/Qwen3-4B-Thinking-2507 --epochs 5
```

### 5. Direct Training API

```python
from core.medical_llm_trainer import MedicalLLMTrainer

# Initialize trainer with Qwen3-4B-Thinking
trainer = MedicalLLMTrainer(
    model_name="Qwen/Qwen3-4B-Thinking-2507",
    use_unsloth=True,
    use_qlora=True,
    max_seq_length=2048
)

# Train on your data
trainer.train("path/to/your/training_data.json")

# Inference with thinking mode
result = trainer.inference(
    "Hepatitis C virus causes chronic liver infection.",
    enable_thinking=True
)
print(result)
```

## 🛠️ Training Tools Comparison

This project provides multiple ways to train and use medical LLMs, each optimized for different use cases:

### 📋 Tools Overview

| **Tool** | **Purpose** | **Best For** | **Complexity** |
|----------|-------------|--------------|----------------|
| `scripts/run.py` | Simple command wrapper | Quick tasks, daily use | ⭐ Low |
| `scripts/run_training_pipeline.py` | Complete medical pipeline | Research, development | ⭐⭐⭐ High |
| `universal_trainer.py` | Configuration-driven trainer | Production, customization | ⭐⭐ Medium |
| Direct API | Python integration | Custom applications | ⭐⭐ Medium |

### 🚀 run.py - Quick & Easy Commands

**Perfect for**: Daily use, quick testing, simple training

```bash
# Quick commands - just works!
python run.py test              # Quick inference test
python run.py train             # Full training (Mac M2 optimized)
python run.py train-upload      # Train + upload to HuggingFace
python run.py cuda              # CUDA optimized inference
python run.py interactive       # Interactive chat mode
python run.py full-upload       # Complete pipeline + upload
```

**How it works**: Simple wrapper that translates commands to `universal_trainer.py` calls
- 113 lines of code
- No dependencies beyond subprocess
- Instant gratification

### 🏥 run_training_pipeline.py - Medical Research Pipeline

**Perfect for**: Medical NLP research, stage-by-stage development, detailed analysis

```bash
# Stage-based execution with full control
python scripts/run_training_pipeline.py --stage all                    # Complete pipeline
python scripts/run_training_pipeline.py --stage 1                     # Data preprocessing only
python scripts/run_training_pipeline.py --stage 2 --epochs 10         # Custom training
python scripts/run_training_pipeline.py --stage 3                     # RAG system building
python scripts/run_training_pipeline.py --stage 4                     # Evaluation with metrics
python scripts/run_training_pipeline.py --stage 5                     # Demo inference

# Advanced options
python scripts/run_training_pipeline.py --stage 2 \
    --model Qwen/Qwen3-4B-Thinking-2507 \
    --device cuda \
    --batch_size 4 \
    --lr 3e-4
```

**Pipeline Stages**:
1. **Data Preprocessing**: Load, clean, augment medical data
2. **Model Training**: Fine-tune Qwen3-4B-Thinking for medical tasks
3. **RAG System Building**: Create RAG-Anything enhanced retrieval system
4. **Evaluation**: Comprehensive metrics and performance analysis
5. **Demo Inference**: Multi-mode RAG inference demonstration

**Features**:
- 673 lines of comprehensive functionality
- Async RAG-Anything integration
- Detailed error handling and recovery
- Medical-specific evaluation metrics
- Stage-by-stage execution control

### ⚙️ universal_trainer.py - Configuration-Driven

**Perfect for**: Production deployments, custom configurations, reproducible experiments

```bash
# Configuration-based training
python universal_trainer.py --config config/config_mac_m2.yaml --mode train
python universal_trainer.py --config config/config_cuda.yaml --mode inference
python universal_trainer.py --config config/config_cpu.yaml --mode eval

# Custom configurations
python universal_trainer.py --config my_custom_config.yaml --mode full --upload-to-hf
```

**Features**:
- YAML-based configuration
- Platform optimization (Mac M2/CUDA/CPU)
- HuggingFace integration
- RAG-Anything support

### 🎯 When to Use Which Tool?

| **Scenario** | **Recommended Tool** | **Command Example** |
|--------------|---------------------|---------------------|
| **Quick test** | `run.py` | `python run.py test` |
| **Daily training** | `run.py` | `python run.py train` |
| **Research experiment** | `run_training_pipeline.py` | `python scripts/run_training_pipeline.py --stage all` |
| **Custom evaluation** | `run_training_pipeline.py` | `python scripts/run_training_pipeline.py --stage 4` |
| **RAG development** | `run_training_pipeline.py` | `python scripts/run_training_pipeline.py --stage 3` |
| **Production deployment** | `universal_trainer.py` | `python universal_trainer.py --config prod_config.yaml` |
| **Custom integration** | Direct API | See Python examples below |

### 2. Data Processing

```python
from core.data_processing import MedicalDataProcessor

# Process raw medical data
processor = MedicalDataProcessor("raw_data.json")
processor.load_data()
processor.save_processed_data("processed_data/")
```

### 3. Using the Mock Trainer (for development)

```python
from examples.english_stable_solution import MockMedicalTrainer

# Use when network issues prevent model download
trainer = MockMedicalTrainer()
result = trainer.inference(
    "Streptococcus pneumoniae causes pneumonia.",
    enable_thinking=True
)
```

## 📊 Model Configuration

### Supported Models

- **Qwen3-4B-Thinking-2507** (Recommended): Advanced reasoning capabilities
- **Qwen2.5-7B-Instruct**: General instruction following
- **Custom models**: Compatible with HuggingFace transformers

### Training Parameters

```yaml
model:
  name: "Qwen/Qwen3-4B-Thinking-2507"
  use_unsloth: true
  use_qlora: true
  torch_dtype: "bfloat16"
  max_seq_length: 2048

training:
  batch_size: 4
  gradient_accumulation_steps: 4
  learning_rate: 2.0e-4
  num_train_epochs: 3
  warmup_steps: 10
  save_steps: 100
```

## 🧠 Entity Types and Relations

### Entity Types
- **Bacteria**: Bacteria, viruses, and other pathogens
- **Disease**: Diseases, symptoms, and pathological conditions
- **Evidence**: Research evidence, conclusions, and findings

### Relationship Types
- **is_a**: Hierarchical relationship
- **biomarker_for**: Biomarker relationship
- **correlated_with**: Correlation relationship
- **has_relationship**: General relationship

## 🍎 Mac M2/M3 Support

Special optimizations for Apple Silicon:

- **MPS Backend**: Automatic detection and usage of Metal Performance Shaders
- **Virtual Environment**: Automatic setup to avoid system conflicts
- **Fallback Mechanisms**: Graceful degradation when Unsloth is incompatible
- **Memory Optimization**: Efficient memory usage for limited RAM

See [README_MAC_M2.md](docs/README_MAC_M2.md) for detailed setup instructions.

## 🔄 Thinking Mode

The Qwen3-4B-Thinking model supports reasoning mode with `<think></think>` tags:

```python
# Enable thinking mode for complex reasoning
result = trainer.inference(
    "Analyze the relationship between H. pylori and gastric cancer.",
    enable_thinking=True
)

# Output includes reasoning process:
# <think>
# I need to analyze the relationship between H. pylori and gastric cancer...
# </think>
# 
# Final analysis in JSON format...
```

## 📈 Evaluation

Built-in evaluation metrics:

- **Entity Recognition**: Precision, Recall, F1-score
- **Relation Extraction**: Accuracy and relationship-specific metrics
- **Medical Accuracy**: Domain-specific evaluation criteria

```python
from core.evaluation_metrics import MedicalEvaluator

evaluator = MedicalEvaluator()
results = evaluator.evaluate_model(trainer, test_data)
print(f"F1 Score: {results['f1_score']:.4f}")
```

## 🛠️ Troubleshooting

### Common Issues

1. **Network Download Errors**:
   - Use the mock trainer for development: `examples/english_stable_solution.py`
   - Try different networks or download during off-peak hours
   - Use `examples/download_step_by_step.py` for manual downloads

2. **Mac M2 Compatibility**:
   - Use virtual environment to avoid system conflicts
   - Fallback to standard transformers if Unsloth fails
   - Check `docs/README_MAC_M2.md` for specific solutions

3. **Memory Issues**:
   - Reduce batch size and max sequence length
   - Enable gradient checkpointing
   - Use QLoRA for memory-efficient fine-tuning

### Environment Issues

```bash
# Reset virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 📚 Quick Reference

### 🚀 Most Common Commands

```bash
# For everyday use (recommended)
python run.py test                    # Quick test
python run.py train                   # Train model
python run.py interactive            # Chat mode

# For research and development
python scripts/run_training_pipeline.py --stage all    # Full pipeline
python scripts/run_training_pipeline.py --stage 4      # Evaluation only

# For RAG functionality
python examples/quick_rag_test.py                      # Test RAG
python examples/medical_rag_demo.py                    # Full RAG demo

# For setup and configuration
python scripts/setup_environment.py                    # Auto setup
python scripts/setup_environment.py --mode install     # Install deps only
```

### 🔧 File Structure Quick Guide

```
medllm-finetune-rag/
├── scripts/run.py                    # 👈 Start here - simple commands
├── scripts/run_training_pipeline.py # 👈 Research pipeline
├── universal_trainer.py             # Configuration-driven trainer
├── examples/                        # Demo scripts and examples
├── config/                          # Platform-specific configs
└── core/                            # Core modules (advanced use)
```

### 💡 Troubleshooting Quick Fixes

```bash
# Dependencies missing?
python scripts/setup_environment.py --mode install

# Import errors?
pip install -r requirements.txt

# Mac M2 issues?
python scripts/setup_qwen3.sh

# Want to start fresh?
rm -rf venv && python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Unsloth](https://github.com/unslothai/unsloth) for efficient LLM training
- [Qwen Team](https://github.com/QwenLM/Qwen) for the Qwen3-4B-Thinking model
- [HuggingFace](https://huggingface.co/) for the transformers ecosystem
- Medical research community for domain expertise

## 📞 Support

- 📧 Issues: Use GitHub Issues for bug reports and feature requests
- 📚 Documentation: Check the `docs/` directory for detailed guides
- 💬 Discussions: Use GitHub Discussions for questions and community support

---

**Note**: This project is designed for research and educational purposes. Ensure compliance with relevant medical data regulations and ethical guidelines when working with medical literature and patient data.