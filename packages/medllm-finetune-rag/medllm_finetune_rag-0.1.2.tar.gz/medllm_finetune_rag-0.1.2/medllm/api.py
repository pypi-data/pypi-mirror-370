"""
High-level API for MedLLM package

This module provides convenient functions for common tasks,
making the package easy to use for quick experiments and prototyping.
"""

import os
import yaml
from typing import Dict, Any, Optional, Union, List
from pathlib import Path

from .medical_llm_trainer import MedicalLLMTrainer
from .data_processing import MedicalDataProcessor
from .medical_rag_system import MedicalRAGSystem
from .evaluation_metrics import MedicalNERREEvaluator
from .universal_trainer import UniversalMedicalTrainer
from .config import get_default_config, create_config_for_device
from .utils import detect_device, setup_environment


def quick_train(
    data_path: str,
    model_name: str = "Qwen/Qwen3-4B-Thinking-2507",
    output_dir: str = "./medllm_output",
    max_steps: int = 100,
    learning_rate: float = 2e-4,
    use_unsloth: bool = True,
    device: Optional[str] = None,
    **kwargs
) -> MedicalLLMTrainer:
    """
    Quick training function for medical LLM fine-tuning.
    
    Args:
        data_path: Path to training data (JSON format)
        model_name: HuggingFace model name
        output_dir: Directory to save trained model
        max_steps: Maximum training steps
        learning_rate: Learning rate for training
        use_unsloth: Whether to use Unsloth acceleration
        device: Target device ('cuda', 'mps', 'cpu', or None for auto-detect)
        **kwargs: Additional training arguments
    
    Returns:
        Trained MedicalLLMTrainer instance
        
    Example:
        >>> trainer = quick_train("medical_data.json")
        >>> trainer.save_model("./my_medical_model")
    """
    if device is None:
        device = detect_device()
    
    # Initialize trainer
    trainer = MedicalLLMTrainer(
        model_name=model_name,
        output_dir=output_dir,
        use_unsloth=use_unsloth,
        device=device,
        max_steps=max_steps,
        learning_rate=learning_rate,
        **kwargs
    )
    
    # Train the model
    trainer.train(data_path)
    
    return trainer


def quick_evaluate(
    model_path: str,
    test_data_path: str,
    metrics: List[str] = ["entity_f1", "relation_f1", "overall_f1"]
) -> Dict[str, float]:
    """
    Quick evaluation of a trained medical model.
    
    Args:
        model_path: Path to trained model
        test_data_path: Path to test data
        metrics: List of metrics to compute
    
    Returns:
        Dictionary of evaluation metrics
        
    Example:
        >>> results = quick_evaluate("./my_model", "test_data.json")
        >>> print(f"Entity F1: {results['entity_f1']:.3f}")
    """
    # Load model for evaluation
    trainer = MedicalLLMTrainer.from_pretrained(model_path)
    
    # Initialize evaluator
    evaluator = MedicalNERREEvaluator()
    
    # Load test data
    processor = MedicalDataProcessor()
    test_data = processor.load_data(test_data_path)
    
    # Generate predictions
    predictions = []
    ground_truths = []
    
    for record in test_data:
        pred = trainer.inference(record['input'])
        predictions.append(pred)
        ground_truths.append(record['output'])
    
    # Evaluate
    results = evaluator.evaluate_predictions(predictions, ground_truths)
    
    # Filter requested metrics
    return {metric: results[metric] for metric in metrics if metric in results}


def quick_inference(
    model_path: str,
    text: str,
    enable_thinking: bool = True,
    temperature: float = 0.7,
    max_new_tokens: int = 512
) -> Dict[str, Any]:
    """
    Quick inference with a trained medical model.
    
    Args:
        model_path: Path to trained model
        text: Input medical text
        enable_thinking: Whether to enable chain-of-thought reasoning
        temperature: Sampling temperature
        max_new_tokens: Maximum tokens to generate
    
    Returns:
        Dictionary with inference results
        
    Example:
        >>> result = quick_inference("./my_model", "Patient has fever and cough")
        >>> print(result['response'])
    """
    # Load model
    trainer = MedicalLLMTrainer.from_pretrained(model_path)
    
    # Perform inference
    result = trainer.inference(
        text=text,
        enable_thinking=enable_thinking,
        temperature=temperature,
        max_new_tokens=max_new_tokens
    )
    
    return result


def create_trainer(
    model_name: str = "Qwen/Qwen3-4B-Thinking-2507",
    config: Optional[Union[str, Dict[str, Any]]] = None,
    device: Optional[str] = None,
    **kwargs
) -> MedicalLLMTrainer:
    """
    Create a medical LLM trainer with configuration.
    
    Args:
        model_name: HuggingFace model name
        config: Configuration file path or dictionary
        device: Target device
        **kwargs: Additional configuration options
    
    Returns:
        Configured MedicalLLMTrainer instance
        
    Example:
        >>> trainer = create_trainer(config="config.yaml")
        >>> trainer = create_trainer(model_name="custom/model", device="cuda")
    """
    if device is None:
        device = detect_device()
    
    if isinstance(config, str):
        # Load config from file
        with open(config, 'r') as f:
            config_dict = yaml.safe_load(f)
    elif isinstance(config, dict):
        config_dict = config
    else:
        # Use default config for device
        config_dict = create_config_for_device(device)
    
    # Override with kwargs
    config_dict.update(kwargs)
    
    # Extract model config
    model_config = config_dict.get('model', {})
    training_config = config_dict.get('training', {})
    lora_config = config_dict.get('lora', {})
    
    # Create trainer
    trainer = MedicalLLMTrainer(
        model_name=model_name,
        **model_config,
        **training_config,
        lora_config=lora_config
    )
    
    return trainer


def create_rag_system(
    api_key: Optional[str] = None,
    working_dir: str = "./rag_workspace",
    model_name: str = "gpt-4o-mini",
    **kwargs
) -> MedicalRAGSystem:
    """
    Create a medical RAG system.
    
    Args:
        api_key: OpenAI API key (or from environment)
        working_dir: Working directory for RAG system
        model_name: LLM model name for RAG
        **kwargs: Additional RAG configuration
    
    Returns:
        Configured MedicalRAGSystem instance
        
    Example:
        >>> rag = create_rag_system()
        >>> await rag.build_knowledge_base_from_json("medical_docs.json")
    """
    if api_key is None:
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key is None:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
    
    rag_system = MedicalRAGSystem(
        api_key=api_key,
        working_dir=working_dir,
        model_name=model_name,
        **kwargs
    )
    
    return rag_system


def setup_project(
    project_dir: str = ".",
    device: Optional[str] = None,
    install_dependencies: bool = True,
    create_sample_data: bool = True
) -> Dict[str, Any]:
    """
    Setup a new medical LLM project.
    
    Args:
        project_dir: Project directory path
        device: Target device for configuration
        install_dependencies: Whether to install dependencies
        create_sample_data: Whether to create sample training data
    
    Returns:
        Setup information dictionary
        
    Example:
        >>> info = setup_project("./my_medical_project")
        >>> print(f"Device detected: {info['device']}")
    """
    project_path = Path(project_dir)
    project_path.mkdir(exist_ok=True)
    
    if device is None:
        device = detect_device()
    
    # Setup environment
    if install_dependencies:
        setup_environment(mode="setup", device=device)
    
    # Create config directory and files
    config_dir = project_path / "config"
    config_dir.mkdir(exist_ok=True)
    
    config = create_config_for_device(device)
    config_file = config_dir / f"config_{device}.yaml"
    
    with open(config_file, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    # Create data directory
    data_dir = project_path / "data"
    data_dir.mkdir(exist_ok=True)
    
    if create_sample_data:
        # Create sample training data
        sample_data = [
            {
                "instruction": "Extract medical entities and relationships from the text.",
                "input": "The patient was diagnosed with hypertension and prescribed lisinopril.",
                "output": "Entities:\n- Disease: hypertension\n- Medication: lisinopril\n\nRelationships:\n- patient -> diagnosed with -> hypertension\n- patient -> prescribed -> lisinopril"
            }
        ]
        
        sample_file = data_dir / "sample_data.json"
        import json
        with open(sample_file, 'w') as f:
            json.dump(sample_data, f, indent=2)
    
    # Create output directories
    (project_path / "output").mkdir(exist_ok=True)
    (project_path / "logs").mkdir(exist_ok=True)
    
    return {
        "project_dir": str(project_path),
        "device": device,
        "config_file": str(config_file),
        "sample_data": str(sample_file) if create_sample_data else None,
        "status": "success"
    }

