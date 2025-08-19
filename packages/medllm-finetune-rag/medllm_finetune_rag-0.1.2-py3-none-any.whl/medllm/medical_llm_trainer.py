#!/usr/bin/env python3
"""
医学大语言模型微调训练器
支持LoRA/QLoRA高效微调和多任务学习
"""

import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer,
    BitsAndBytesConfig
)
from peft import (
    LoraConfig, get_peft_model,
    TaskType, prepare_model_for_kbit_training
)
from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.metrics import f1_score, classification_report
import wandb
from pathlib import Path

# Unsloth imports for faster training
try:
    from unsloth import FastModel  # Use FastModel instead of FastLanguageModel for Qwen3
    from unsloth.chat_templates import get_chat_template, train_on_responses_only
    from trl import SFTTrainer, SFTConfig
    from unsloth import is_bfloat16_supported
    UNSLOTH_AVAILABLE = True
except ImportError:
    UNSLOTH_AVAILABLE = False
    print("Warning: Unsloth not available. Falling back to standard training.")

class MedicalInstructionDataset(Dataset):
    """医学指令数据集"""

    def __init__(self, data_path: str, tokenizer, max_length: int = 2048):
        self.tokenizer = tokenizer
        self.max_length = max_length

        with open(data_path, 'r', encoding='utf-8') as f:
            self.data = json.load(f)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # 构建完整的对话格式
        system_msg = item.get('system', '')
        instruction = item['instruction']
        input_text = item.get('input', '')
        output = item['output']

        # 格式化为ChatML格式
        if input_text:
            prompt = f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{instruction}\n{input_text}<|im_end|>\n<|im_start|>assistant\n"
        else:
            prompt = f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n"

        full_text = prompt + output + "<|im_end|>"

        # 分词
        tokenized = self.tokenizer(
            full_text,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )

        # 计算labels（只对assistant部分计算损失）
        prompt_tokens = self.tokenizer(
            prompt,
            truncation=True,
            max_length=self.max_length,
            padding=False,
            return_tensors="pt"
        )

        labels = tokenized["input_ids"].clone()
        labels[0, :len(prompt_tokens["input_ids"][0])] = -100  # 忽略prompt部分的损失

        return {
            "input_ids": tokenized["input_ids"].flatten(),
            "attention_mask": tokenized["attention_mask"].flatten(),
            "labels": labels.flatten()
        }

class MedicalLLMTrainer:
    """医学大语言模型训练器"""

    def __init__(
        self,
        model_name: str = "Qwen/Qwen3-4B-Thinking-2507",
        output_dir: str = "./medical_llm_output",
        use_qlora: bool = True,
        max_seq_length: int = 2048,
        use_unsloth: bool = True
    ):
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.use_qlora = use_qlora
        self.max_seq_length = max_seq_length
        self.use_unsloth = use_unsloth and UNSLOTH_AVAILABLE

        # 使用Unsloth加载模型（如果可用）
        if self.use_unsloth:
            print("Loading model with Unsloth for faster training...")
            # Use the correct model name format for Unsloth
            unsloth_model_name = model_name
            if "Qwen3-4B-Thinking-2507" in model_name:
                unsloth_model_name = "unsloth/Qwen3-4B-Thinking-2507"

            self.model, self.tokenizer = FastModel.from_pretrained(
                model_name=unsloth_model_name,
                max_seq_length=max_seq_length,
                load_in_4bit=use_qlora,
                load_in_8bit=False,
                full_finetuning=False,
                dtype=None,  # Auto detection
                trust_remote_code=True
            )

            # Apply the official qwen3-thinking chat template
            self.tokenizer = get_chat_template(
                self.tokenizer,
                chat_template="qwen3-thinking",
            )

            # 配置LoRA with Unsloth - using official settings
            self.model = FastModel.get_peft_model(
                self.model,
                r=32,  # Official notebook uses r=32
                lora_alpha=32,
                lora_dropout=0,  # Official uses 0 for optimization
                target_modules=[
                    "q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"
                ],
                bias="none",
                use_gradient_checkpointing="unsloth",  # 30% less VRAM
                random_state=3407,
                use_rslora=False,
                loftq_config=None
            )

        else:
            # 传统方式加载模型
            print("Loading model with standard transformers...")
            # 初始化tokenizer - Qwen3专用配置
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # 配置量化（如果使用QLoRA）
            if use_qlora:
                self.bnb_config = BitsAndBytesConfig(
                    load_in_4bit=True,
                    bnb_4bit_use_double_quant=True,
                    bnb_4bit_quant_type="nf4",
                    bnb_4bit_compute_dtype=torch.bfloat16
                )
            else:
                self.bnb_config = None

            # 检测设备并优化加载
            if torch.backends.mps.is_available():
                # Mac M2/M3 优化
                device_map = None  # MPS不支持device_map="auto"
                torch_dtype = torch.float16  # MPS更稳定
                print("   使用Apple Silicon MPS加速")
            else:
                device_map = "auto"
                torch_dtype = torch.bfloat16 if use_qlora else torch.float16

            # 加载模型
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                quantization_config=self.bnb_config,
                device_map=device_map,
                torch_dtype=torch_dtype,
                trust_remote_code=True
            )

            # 手动移动到MPS设备（如果可用）
            if torch.backends.mps.is_available() and device_map is None:
                self.model = self.model.to('mps')

            if use_qlora:
                self.model = prepare_model_for_kbit_training(self.model)

            # 配置LoRA - Qwen3优化配置
            self.lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                inference_mode=False,
                r=16,  # LoRA rank
                lora_alpha=32,  # LoRA scaling
                lora_dropout=0.1,
                # Qwen3的attention和MLP层名称
                target_modules=[
                    "q_proj", "k_proj", "v_proj", "o_proj",
                    "gate_proj", "up_proj", "down_proj"
                ],
                bias="none"
            )

            # 应用LoRA
            self.model = get_peft_model(self.model, self.lora_config)

        # Qwen3 Thinking模型特殊token设置
        if "qwen3" in model_name.lower() and "thinking" in model_name.lower():
            # Qwen3 Thinking模型的chat template支持<think></think>标签
            self.tokenizer.chat_template = "{% for message in messages %}{% if loop.first and messages[0]['role'] != 'system' %}{{ '<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n' }}{% endif %}{{'<|im_start|>' + message['role'] + '\n' + message['content'] + '<|im_end|>' + '\n'}}{% endfor %}{% if add_generation_prompt %}{{ '<|im_start|>assistant\n' }}{% endif %}"

        # 打印可训练参数
        if hasattr(self.model, 'print_trainable_parameters'):
            self.model.print_trainable_parameters()

    def format_data_for_unsloth(self, data_path: str) -> List[Dict[str, str]]:
        """将数据格式化为Unsloth SFTTrainer所需的格式"""
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        formatted_data = []
        for item in data:
            system_msg = item.get('system', '')
            instruction = item['instruction']
            input_text = item.get('input', '')
            output = item['output']

            # 构建完整的对话
            if input_text:
                conversation = f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{instruction}\n{input_text}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"
            else:
                conversation = f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n{output}<|im_end|>"

            formatted_data.append({"text": conversation})

        return formatted_data

    def train(
        self,
        train_data_path: str,
        val_data_path: str,
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-4,
        warmup_steps: int = 100,
        logging_steps: int = 10,
        save_steps: int = 500,
        eval_steps: int = 500
    ):
        """训练模型"""

        if self.use_unsloth:
            # 使用Unsloth的SFTTrainer with SFTConfig
            print("Using Unsloth SFTTrainer for faster training...")

            # 格式化数据为Unsloth格式
            train_data = self.format_data_for_unsloth(train_data_path)

            # 创建SFTTrainer with SFTConfig (official pattern)
            trainer = SFTTrainer(
                model=self.model,
                tokenizer=self.tokenizer,
                train_dataset=train_data,
                eval_dataset=None,  # Can add validation later
                args=SFTConfig(
                    dataset_text_field="text",
                    per_device_train_batch_size=batch_size,
                    gradient_accumulation_steps=4,
                    warmup_steps=warmup_steps,
                    num_train_epochs=num_epochs,
                    learning_rate=learning_rate,
                    logging_steps=logging_steps,
                    optim="adamw_8bit",  # Official uses this
                    weight_decay=0.01,
                    lr_scheduler_type="linear",
                    seed=3407,
                    output_dir=str(self.output_dir),
                    report_to="wandb",
                    run_name="medical-llm-finetune-qwen3",
                ),
            )

            # Apply train_on_responses_only for better training (official pattern)
            trainer = train_on_responses_only(
                trainer,
                instruction_part="<|im_start|>user\n",
                response_part="<|im_start|>assistant\n",
            )

        else:
            # 使用传统的Trainer
            print("Using standard transformers Trainer...")

            # 创建数据集
            train_dataset = MedicalInstructionDataset(train_data_path, self.tokenizer)
            val_dataset = MedicalInstructionDataset(val_data_path, self.tokenizer)

            # 训练参数
            training_args = TrainingArguments(
                output_dir=str(self.output_dir),
                num_train_epochs=num_epochs,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                gradient_accumulation_steps=4,
                gradient_checkpointing=True,
                warmup_steps=warmup_steps,
                learning_rate=learning_rate,
                fp16=not self.use_qlora,
                bf16=self.use_qlora,
                logging_steps=logging_steps,
                save_steps=save_steps,
                eval_steps=eval_steps,
                evaluation_strategy="steps",
                save_strategy="steps",
                load_best_model_at_end=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                report_to="wandb",
                run_name="medical-llm-finetune",
                remove_unused_columns=False,
                dataloader_pin_memory=False,
            )

            # 创建训练器
            trainer = Trainer(
                model=self.model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=self.tokenizer,
            )

        # 开始训练
        print("开始训练...")
        trainer.train()

        # 保存模型
        trainer.save_model()
        self.tokenizer.save_pretrained(str(self.output_dir))

        print(f"训练完成，模型已保存到 {self.output_dir}")

    def evaluate_on_test(self, test_data_path: str) -> Dict[str, float]:
        """在测试集上评估模型"""
        with open(test_data_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)

        predictions = []
        ground_truths = []

        self.model.eval()

        for item in test_data:
            # 构建输入
            system_msg = item.get('system', '')
            instruction = item['instruction']
            input_text = item.get('input', '')

            if input_text:
                prompt = f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{instruction}\n{input_text}<|im_end|>\n<|im_start|>assistant\n"
            else:
                prompt = f"<|im_start|>system\n{system_msg}<|im_end|>\n<|im_start|>user\n{instruction}<|im_end|>\n<|im_start|>assistant\n"

            # 生成预测
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

            with torch.no_grad():
                # Qwen3 Thinking模型的推荐参数
                generation_kwargs = {
                    "max_new_tokens": 512,
                    "pad_token_id": self.tokenizer.eos_token_id,
                    "do_sample": True
                }

                # 根据模型类型设置不同的生成参数
                if "thinking" in self.model_name.lower():
                    # Thinking模型参数
                    generation_kwargs.update({
                        "temperature": 0.6,
                        "top_p": 0.95,
                        "top_k": 20,
                        "min_p": 0.0
                    })
                else:
                    # Instruct模型参数
                    generation_kwargs.update({
                        "temperature": 0.7,
                        "top_p": 0.8,
                        "top_k": 20,
                        "min_p": 0.0
                    })

                outputs = self.model.generate(**inputs, **generation_kwargs)

            # 解码预测结果
            prediction = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:],
                skip_special_tokens=True
            )

            predictions.append(prediction)
            ground_truths.append(item['output'])

        # 计算评估指标（这里需要根据具体任务定制）
        # 简化的评估：计算完全匹配的比例
        exact_matches = sum(1 for p, g in zip(predictions, ground_truths) if p.strip() == g.strip())
        accuracy = exact_matches / len(predictions)

        results = {
            "accuracy": accuracy,
            "exact_matches": exact_matches,
            "total_samples": len(predictions)
        }

        print(f"测试结果: {results}")
        return results

    def inference(self, text: str, max_length: int = 512, enable_thinking: bool = True) -> str:
        """推理接口"""
        system_prompt = """You are a professional medical literature analysis expert. Please extract entities and relationships from the given medical literature.

Entity Types:
- Bacteria: Bacteria, viruses, and other pathogens
- Disease: Diseases, symptoms, and pathological conditions
- Evidence: Research evidence, conclusions, and findings

Relationship Types:
- is_a: Hierarchical relationship
- biomarker_for: Biomarker relationship
- correlated_with: Correlation relationship
- has_relationship: General relationship

For complex analysis tasks, you can use <think></think> tags to show your reasoning process, then provide the final result in JSON format."""

        # Use the official chat template for better formatting
        if self.use_unsloth and hasattr(self.tokenizer, 'apply_chat_template'):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please extract entities and relationships from the following medical literature:\n\n{text}"}
            ]
            prompt = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=enable_thinking  # Official parameter
            )
        else:
            # Fallback to manual formatting
            prompt = f"<|im_start|>system\n{system_prompt}<|im_end|>\n<|im_start|>user\nPlease extract entities and relationships from the following medical literature:\n\n{text}<|im_end|>\n<|im_start|>assistant\n"

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            # Qwen3 Thinking模型的推荐参数
            generation_kwargs = {
                "max_new_tokens": max_length,
                "pad_token_id": self.tokenizer.eos_token_id,
                "do_sample": True
            }

            # 根据模型类型和thinking mode设置不同的生成参数
            if "thinking" in self.model_name.lower():
                if enable_thinking:
                    # Thinking模型参数 (for reasoning)
                    generation_kwargs.update({
                        "temperature": 0.6,
                        "top_p": 0.95,
                        "top_k": 20,
                    })
                else:
                    # Non-thinking mode parameters
                    generation_kwargs.update({
                        "temperature": 0.7,
                        "top_p": 0.8,
                        "top_k": 20,
                    })
            else:
                # Instruct模型参数
                generation_kwargs.update({
                    "temperature": 0.7,
                    "top_p": 0.8,
                    "top_k": 20,
                })

            outputs = self.model.generate(**inputs, **generation_kwargs)

        response = self.tokenizer.decode(
            outputs[0][inputs['input_ids'].shape[1]:],
            skip_special_tokens=True
        )

        return response

def main():
    """主函数"""
    # 初始化W&B
    wandb.init(project="medical-llm-finetune")

    # 创建训练器 - 使用Qwen3-4B-Thinking-2507
    trainer = MedicalLLMTrainer(
        model_name="Qwen/Qwen3-4B-Thinking-2507",
        output_dir="./medical_llm_output",
        use_qlora=True,
        max_seq_length=2048,
        use_unsloth=True
    )

    # 训练模型
    trainer.train(
        train_data_path="processed_data/instruction_data.json",
        val_data_path="processed_data/validation_data.json",
        num_epochs=3,
        batch_size=2,  # 根据GPU内存调整
        learning_rate=2e-4
    )

    # 评估模型
    results = trainer.evaluate_on_test("processed_data/test_data.json")

    # 测试推理 - 展示Thinking模式
    test_text = "Hepatitis C virus (HCV) causes chronic liver infection and is associated with liver cirrhosis."

    print("\n=== Testing with Thinking Mode ===")
    prediction_thinking = trainer.inference(test_text, enable_thinking=True)
    print(f"Thinking mode inference result: {prediction_thinking}")

    print("\n=== Testing without Thinking Mode ===")
    prediction_direct = trainer.inference(test_text, enable_thinking=False)
    print(f"Direct inference result: {prediction_direct}")

if __name__ == "__main__":
    main()
