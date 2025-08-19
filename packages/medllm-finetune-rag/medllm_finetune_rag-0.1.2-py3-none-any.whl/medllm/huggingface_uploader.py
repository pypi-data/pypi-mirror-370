#!/usr/bin/env python3
"""
HuggingFace Model Upload Utility

This module provides functionality to upload trained medical LLM models to HuggingFace Hub.
Supports both full models and LoRA adapters with proper metadata and model cards.
"""

import os
import json
import tempfile
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from dotenv import load_dotenv
from huggingface_hub import HfApi, Repository, create_repo, upload_folder
from huggingface_hub.utils import RepositoryNotFoundError
import torch

# Load environment variables
load_dotenv()

class HuggingFaceUploader:
    """HuggingFace model uploader with medical LLM specialization"""

    def __init__(self, token: Optional[str] = None, username: str = "xingqiang"):
        """Initialize uploader with HF token and username"""
        self.token = token or os.getenv('HF_TOKEN')
        if not self.token:
            raise ValueError("HuggingFace token not found. Set HF_TOKEN in .env file or pass as parameter.")

        self.username = username
        self.api = HfApi(token=self.token)

        # Verify token and get user info
        try:
            user_info = self.api.whoami()
            actual_username = user_info['name']
            print(f"✅ HuggingFace API initialized for user: {actual_username}")
            if actual_username != self.username:
                print(f"⚠️  Note: Using actual username '{actual_username}' instead of '{self.username}'")
                self.username = actual_username
        except Exception as e:
            print(f"⚠️  Could not verify user info: {e}")
            print(f"✅ HuggingFace API initialized (assuming username: {self.username})")

    def create_model_card(self,
                         model_name: str,
                         base_model: str,
                         config: Dict[str, Any],
                         metrics: Optional[Dict[str, float]] = None,
                         training_details: Optional[Dict[str, Any]] = None) -> str:
        """Create a comprehensive model card for the medical LLM"""

        # Extract training info
        training_info = training_details or {}
        dataset_size = training_info.get('dataset_size', 'Unknown')
        training_time = training_info.get('training_time', 'Unknown')
        epochs = config.get('training', {}).get('parameters', {}).get('num_train_epochs', 'Unknown')

        # Extract model config
        model_config = config.get('model', {})
        training_config = config.get('training', {})
        lora_config = training_config.get('lora', {})

        # Format metrics
        metrics_section = ""
        if metrics:
            metrics_section = f"""
## Evaluation Metrics

| Metric | Value |
|--------|-------|
"""
            for metric, value in metrics.items():
                metrics_section += f"| {metric} | {value:.4f} |\n"

        # Create model card
        model_card = f"""---
language: en
license: apache-2.0
base_model: {base_model}
tags:
- medical
- llm
- qwen3
- thinking-model
- entity-extraction
- relation-extraction
- lora
- peft
library_name: transformers
pipeline_tag: text-generation
---

# {model_name}

## Model Description

This is a fine-tuned medical LLM based on {base_model}, specialized for medical entity and relationship extraction. The model has been trained using LoRA (Low-Rank Adaptation) for efficient fine-tuning while maintaining the base model's capabilities.

## Model Details

- **Base Model**: {base_model}
- **Fine-tuning Method**: LoRA (Low-Rank Adaptation)
- **Domain**: Medical Literature Analysis
- **Tasks**: Entity Recognition, Relationship Extraction
- **Language**: English
- **License**: Apache 2.0

## Training Configuration

### LoRA Configuration
- **Rank (r)**: {lora_config.get('r', 'Unknown')}
- **Alpha**: {lora_config.get('alpha', 'Unknown')}
- **Dropout**: {lora_config.get('dropout', 'Unknown')}
- **Target Modules**: {', '.join(lora_config.get('target_modules', []))}

### Training Parameters
- **Epochs**: {epochs}
- **Dataset Size**: {dataset_size}
- **Training Time**: {training_time}
- **Max Sequence Length**: {training_config.get('parameters', {}).get('max_length', 'Unknown')}
- **Batch Size**: {training_config.get('parameters', {}).get('per_device_train_batch_size', 'Unknown')}
- **Learning Rate**: {training_config.get('parameters', {}).get('learning_rate', 'Unknown')}

{metrics_section}

## Supported Entity Types

- **Bacteria**: Bacteria, viruses, and other pathogens
- **Disease**: Diseases, symptoms, and pathological conditions
- **Evidence**: Research evidence, conclusions, and findings

## Supported Relationship Types

- **is_a**: Hierarchical relationship
- **biomarker_for**: Biomarker relationship
- **correlated_with**: Correlation relationship
- **has_relationship**: General relationship

## Usage

### Quick Start

```python
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel

# Load base model and tokenizer
base_model = AutoModelForCausalLM.from_pretrained("{base_model}")
tokenizer = AutoTokenizer.from_pretrained("{base_model}")

# Load LoRA adapter
model = PeftModel.from_pretrained(base_model, "{model_name}")

# Example inference
text = "Hepatitis C virus (HCV) causes chronic liver infection."
inputs = tokenizer(text, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=256)
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(result)
```

### Thinking Mode (if supported)

```python
# For models with thinking capabilities
messages = [
    {{"role": "system", "content": "You are a medical literature analysis expert."}},
    {{"role": "user", "content": "Extract entities and relationships from: Streptococcus pneumoniae causes pneumonia."}}
]

prompt = tokenizer.apply_chat_template(
    messages,
    tokenize=False,
    add_generation_prompt=True,
    enable_thinking=True
)

inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=512, temperature=0.6)
result = tokenizer.decode(outputs[0], skip_special_tokens=True)
```

## Training Data

The model was fine-tuned on medical literature data focusing on:
- Entity recognition in medical texts
- Relationship extraction between medical concepts
- Clinical reasoning and analysis

## Limitations

- Specialized for medical domain - may not perform well on general text
- LoRA adapter requires the base model for inference
- Performance may vary on medical subdomains not well-represented in training data
- Should not be used for actual medical diagnosis without expert validation

## Ethical Considerations

- This model is for research and educational purposes
- Medical predictions should always be validated by qualified healthcare professionals
- Ensure compliance with relevant medical data regulations (HIPAA, GDPR, etc.)
- Consider bias in medical literature and datasets

## Citation

If you use this model in your research, please cite:

```bibtex
@misc{{{model_name.replace('/', '_').replace('-', '_')},
  title={{Medical LLM Fine-tuned with LoRA for Entity and Relationship Extraction}},
  author={{Your Name}},
  year={{{datetime.now().year}}},
  url={{https://huggingface.co/{model_name}}}
}}
```

## Model Card Contact

For questions about this model, please open an issue in the associated repository or contact the model author.

---

*Generated automatically by Medical LLM Fine-tuning System*
*Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        return model_card

    def generate_repo_name(self, base_model: str, suffix: str = "medical-ner") -> str:
        """Generate repository name based on base model and task"""
        # Extract model name from full path
        model_short = base_model.split('/')[-1].lower()

        # Clean up model name
        model_clean = model_short.replace('_', '-').replace('.', '-')

        # Generate repo name
        repo_name = f"{self.username}/{model_clean}-{suffix}"

        return repo_name

    def upload_model(self,
                    model_path: str,
                    repo_name: str,
                    base_model: str,
                    config: Dict[str, Any],
                    private: bool = False,
                    metrics: Optional[Dict[str, float]] = None,
                    training_details: Optional[Dict[str, Any]] = None,
                    commit_message: Optional[str] = None) -> str:
        """Upload trained model to HuggingFace Hub"""

        try:
            print(f"🚀 Starting upload to HuggingFace Hub...")
            print(f"Repository: {repo_name}")
            print(f"Private: {private}")

            # Create repository if it doesn't exist
            try:
                repo_info = self.api.repo_info(repo_name)
                print(f"✅ Repository {repo_name} already exists")
            except RepositoryNotFoundError:
                print(f"📁 Creating new repository: {repo_name}")
                create_repo(
                    repo_id=repo_name,
                    token=self.token,
                    private=private,
                    exist_ok=True
                )

            # Create model card
            model_card_content = self.create_model_card(
                model_name=repo_name,
                base_model=base_model,
                config=config,
                metrics=metrics,
                training_details=training_details
            )

            # Create temporary directory for upload preparation
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # Copy model files
                model_source = Path(model_path)
                if model_source.is_file():
                    # Single file (e.g., adapter_model.safetensors)
                    import shutil
                    shutil.copy2(model_source, temp_path / model_source.name)
                else:
                    # Directory with multiple files
                    import shutil
                    shutil.copytree(model_source, temp_path, dirs_exist_ok=True)

                # Write model card
                with open(temp_path / "README.md", 'w', encoding='utf-8') as f:
                    f.write(model_card_content)

                # Write training config
                with open(temp_path / "training_config.json", 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)

                # Write metrics if available
                if metrics:
                    with open(temp_path / "evaluation_results.json", 'w', encoding='utf-8') as f:
                        json.dump(metrics, f, indent=2, ensure_ascii=False)

                # Upload to hub
                commit_msg = commit_message or f"Upload medical LLM fine-tuned model - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                print(f"📤 Uploading files to {repo_name}...")
                self.api.upload_folder(
                    folder_path=temp_path,
                    repo_id=repo_name,
                    token=self.token,
                    commit_message=commit_msg
                )

            repo_url = f"https://huggingface.co/{repo_name}"
            print(f"✅ Model uploaded successfully!")
            print(f"🔗 Repository URL: {repo_url}")

            return repo_url

        except Exception as e:
            print(f"❌ Error uploading model: {e}")
            raise

    def upload_lora_adapter(self,
                           adapter_path: str,
                           repo_name: str,
                           base_model: str,
                           config: Dict[str, Any],
                           private: bool = False,
                           metrics: Optional[Dict[str, float]] = None,
                           training_details: Optional[Dict[str, Any]] = None) -> str:
        """Upload LoRA adapter specifically"""

        print(f"📋 Uploading LoRA adapter...")
        print(f"Adapter path: {adapter_path}")

        # Verify LoRA files exist
        adapter_dir = Path(adapter_path)
        required_files = ['adapter_config.json']
        adapter_files = ['adapter_model.safetensors', 'adapter_model.bin']

        missing_files = []
        for file in required_files:
            if not (adapter_dir / file).exists():
                missing_files.append(file)

        # Check for at least one adapter model file
        if not any((adapter_dir / f).exists() for f in adapter_files):
            missing_files.extend(adapter_files)

        if missing_files:
            raise FileNotFoundError(f"Missing LoRA files: {missing_files}")

        return self.upload_model(
            model_path=adapter_path,
            repo_name=repo_name,
            base_model=base_model,
            config=config,
            private=private,
            metrics=metrics,
            training_details=training_details,
            commit_message=f"Upload LoRA adapter for {base_model}"
        )

    def list_user_models(self, filter_medical: bool = True) -> List[Dict[str, Any]]:
        """List user's models on HuggingFace Hub"""
        try:
            models = self.api.list_models(author=self.api.whoami()['name'])

            model_list = []
            for model in models:
                if filter_medical:
                    # Filter for medical models
                    if any(tag in model.tags for tag in ['medical', 'llm', 'qwen3']):
                        model_list.append({
                            'name': model.modelId,
                            'downloads': model.downloads,
                            'tags': model.tags,
                            'created': model.created_at,
                            'updated': model.last_modified
                        })
                else:
                    model_list.append({
                        'name': model.modelId,
                        'downloads': model.downloads,
                        'tags': model.tags,
                        'created': model.created_at,
                        'updated': model.last_modified
                    })

            return model_list

        except Exception as e:
            print(f"❌ Error listing models: {e}")
            return []

    def delete_model(self, repo_name: str) -> bool:
        """Delete model from HuggingFace Hub"""
        try:
            self.api.delete_repo(repo_name, token=self.token)
            print(f"✅ Model {repo_name} deleted successfully")
            return True
        except Exception as e:
            print(f"❌ Error deleting model: {e}")
            return False

def main():
    """CLI interface for HuggingFace uploads"""
    import argparse

    parser = argparse.ArgumentParser(description="Upload medical LLM to HuggingFace Hub")
    parser.add_argument('--model-path', required=True, help='Path to model/adapter files')
    parser.add_argument('--repo-name', required=True, help='HuggingFace repository name (username/model-name)')
    parser.add_argument('--base-model', required=True, help='Base model name')
    parser.add_argument('--config', required=True, help='Training configuration file')
    parser.add_argument('--private', action='store_true', help='Make repository private')
    parser.add_argument('--metrics', help='Path to evaluation metrics JSON file')

    args = parser.parse_args()

    # Load config
    import yaml
    with open(args.config, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # Load metrics if provided
    metrics = None
    if args.metrics and os.path.exists(args.metrics):
        with open(args.metrics, 'r', encoding='utf-8') as f:
            metrics = json.load(f)

    # Initialize uploader
    uploader = HuggingFaceUploader()

    # Upload model
    repo_url = uploader.upload_lora_adapter(
        adapter_path=args.model_path,
        repo_name=args.repo_name,
        base_model=args.base_model,
        config=config,
        private=args.private,
        metrics=metrics
    )

    print(f"🎉 Upload completed: {repo_url}")

if __name__ == "__main__":
    main()
