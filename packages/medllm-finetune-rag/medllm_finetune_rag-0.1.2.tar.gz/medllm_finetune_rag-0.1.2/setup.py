#!/usr/bin/env python3
"""
Setup script for medllm-finetune-rag package
"""

from setuptools import setup, find_packages
import os
import re

# Read version from __init__.py
def get_version():
    init_file = os.path.join("medllm", "__init__.py")
    if os.path.exists(init_file):
        with open(init_file, "r", encoding="utf-8") as f:
            content = f.read()
            version_match = re.search(r"__version__\s*=\s*['\"]([^'\"]*)['\"]", content)
            if version_match:
                return version_match.group(1)
    return "0.1.0"

# Read long description from README
def get_long_description():
    readme_file = "README.md"
    if os.path.exists(readme_file):
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return ""

# Read requirements
def get_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        with open("requirements.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Handle git dependencies
                    if line.startswith("unsloth"):
                        continue  # Skip unsloth for now, will be optional
                    requirements.append(line)
    return requirements

setup(
    name="medllm-finetune-rag",
    version=get_version(),
    author="Xingqiang Chen",
    author_email="joy66777@gmail.com",
    description="A comprehensive toolkit for fine-tuning medical large language models with RAG capabilities",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/chenxingqiang/medllm-finetune-rag",
    packages=find_packages(exclude=["tests*", "scripts*", "examples*", "docs*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Healthcare Industry", 
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.35.0", 
        "tokenizers>=0.14.0",
        "datasets>=2.14.0",
        "accelerate>=0.24.0",
        "peft>=0.6.0",
        "trl>=0.7.0",
        "scikit-learn>=1.3.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "sentence-transformers>=2.2.0",
        "raganything[all]",
        "lightrag",
        "chromadb>=0.4.0",
        "tqdm>=4.65.0",
        "python-dotenv>=1.0.0",
        "huggingface-hub>=0.20.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "unsloth": [
            # Note: unsloth requires manual installation from GitHub
            # pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"
            "unsloth_zoo",
        ],
        "rag": [
            # Core RAG dependencies are now included in base installation
        ],
        "gpu": [
            "bitsandbytes>=0.41.0",
        ],
        "dev": [
            "black>=23.0.0",
            "flake8>=6.0.0", 
            "pytest>=7.0.0",
            "jupyter>=1.0.0",
        ],
        "viz": [
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "wandb>=0.16.0",
        ],
        "all": [
            # Note: unsloth requires manual installation from GitHub
            "unsloth_zoo",
            # Core RAG dependencies (raganything, lightrag, chromadb) are now included in base installation
            "bitsandbytes>=0.41.0",
            "matplotlib>=3.7.0",
            "seaborn>=0.12.0",
            "wandb>=0.16.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "pytest>=7.0.0",
            "jupyter>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "medllm=medllm.cli:main",
            "medllm-train=medllm.cli:train_command",
            "medllm-eval=medllm.cli:eval_command",
            "medllm-rag=medllm.cli:rag_command",
        ],
    },
    include_package_data=True,
    package_data={
        "medllm": [
            "configs/*.yaml",
            "templates/*.txt",
            "data/*.json",
        ],
    },
    zip_safe=False,
    keywords="medical, llm, fine-tuning, rag, qwen, healthcare, nlp, ai",
    project_urls={
        "Bug Reports": "https://github.com/chenxingqiang/medllm-finetune-rag/issues",
        "Documentation": "https://github.com/chenxingqiang/medllm-finetune-rag/blob/main/README.md", 
        "Source": "https://github.com/chenxingqiang/medllm-finetune-rag",
    },
)
