"""
Medical LLM Fine-tuning Core Modules

This package contains the core components for medical LLM fine-tuning:
- MedicalLLMTrainer: Main training class with Unsloth integration
- MedicalDataProcessor: Data preprocessing and format conversion
- MedicalRAGSystem: RAG system implementation
- MedicalEvaluator: Model evaluation tools
"""

from .medical_llm_trainer import MedicalLLMTrainer
from .data_processing import MedicalDataProcessor
from .medical_rag_system import MedicalRAGSystem
from .evaluation_metrics import EntityEvaluator, RelationEvaluator, MedicalNERREEvaluator

__all__ = [
    'MedicalLLMTrainer',
    'MedicalDataProcessor',
    'MedicalRAGSystem',
    'EntityEvaluator',
    'RelationEvaluator',
    'MedicalNERREEvaluator'
]

__version__ = '1.0.0'
