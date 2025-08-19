#!/usr/bin/env python3
"""
Mac M2 稳定解决方案 - 使用本地模拟和离线模式
"""

import torch
import json
import os
from pathlib import Path

class MockMedicalTrainer:
    """模拟医学训练器 - 用于测试环境和功能"""
    
    def __init__(self):
        self.model_name = "mock-qwen3-4b-thinking"
        self.device = self._detect_device()
        self.setup_mock_tokenizer()
        print(f"✓ 模拟训练器初始化成功 (设备: {self.device})")
    
    def _detect_device(self):
        """检测可用设备"""
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"
    
    def setup_mock_tokenizer(self):
        """设置模拟tokenizer"""
        # 创建简单的词汇表
        self.vocab = {
            "<pad>": 0, "<unk>": 1, "<s>": 2, "</s>": 3,
            "medical": 4, "patient": 5, "disease": 6, "treatment": 7,
            "bacteria": 8, "virus": 9, "infection": 10, "diagnosis": 11,
            "symptom": 12, "therapy": 13, "medicine": 14, "hospital": 15,
            "doctor": 16, "nurse": 17, "health": 18, "care": 19,
            # 添加一些常用词
            "the": 20, "and": 21, "is": 22, "of": 23, "in": 24, "to": 25,
            "a": 26, "with": 27, "for": 28, "by": 29, "from": 30, "that": 31
        }
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}
        print("✓ 模拟tokenizer设置完成")
    
    def encode(self, text):
        """简单编码"""
        words = text.lower().split()
        tokens = []
        for word in words:
            if word in self.vocab:
                tokens.append(self.vocab[word])
            else:
                tokens.append(self.vocab["<unk>"])
        return tokens
    
    def decode(self, tokens):
        """简单解码"""
        words = []
        for token in tokens:
            if token in self.reverse_vocab:
                words.append(self.reverse_vocab[token])
            else:
                words.append("<unk>")
        return " ".join(words)
    
    def inference(self, text, enable_thinking=True):
        """模拟推理"""
        print(f"🧠 模拟推理 (思考模式: {enable_thinking})")
        print(f"输入: {text}")
        
        # 模拟编码
        tokens = self.encode(text)
        print(f"编码: {tokens}")
        
        # 模拟医学实体识别
        entities = []
        relations = []
        
        # 简单的规则匹配
        text_lower = text.lower()
        
        if "bacteria" in text_lower or "virus" in text_lower:
            entities.append({"text": "pathogen", "type": "Bacteria", "start": 0, "end": 10})
        
        if "disease" in text_lower or "infection" in text_lower:
            entities.append({"text": "condition", "type": "Disease", "start": 20, "end": 30})
        
        if "study" in text_lower or "research" in text_lower:
            entities.append({"text": "evidence", "type": "Evidence", "start": 40, "end": 50})
        
        # 模拟关系
        if len(entities) >= 2:
            relations.append({
                "entity1": entities[0]["text"],
                "relation": "correlated_with",
                "entity2": entities[1]["text"]
            })
        
        # 构建响应
        if enable_thinking:
            response = f"""<think>
我需要分析这段医学文本，识别其中的实体和关系。

从文本中我可以识别到：
- 可能的病原体相关词汇
- 疾病或感染相关内容
- 研究证据相关信息

让我整理成JSON格式。
</think>

{{
  "entities": {json.dumps(entities, ensure_ascii=False, indent=2)},
  "relations": {json.dumps(relations, ensure_ascii=False, indent=2)}
}}"""
        else:
            response = json.dumps({
                "entities": entities,
                "relations": relations
            }, ensure_ascii=False, indent=2)
        
        print(f"输出: {response[:200]}...")
        return response
    
    def test_system(self):
        """测试系统功能"""
        print("\n=== 系统功能测试 ===")
        
        # 测试1: 设备检测
        print(f"1. 设备检测: {self.device}")
        
        # 测试2: 编码解码
        test_text = "medical bacteria infection"
        tokens = self.encode(test_text)
        decoded = self.decode(tokens)
        print(f"2. 编码解码测试:")
        print(f"   原文: {test_text}")
        print(f"   编码: {tokens}")
        print(f"   解码: {decoded}")
        
        # 测试3: 推理功能
        print("3. 推理功能测试:")
        medical_text = "Helicobacter pylori bacteria causes gastric infection and disease"
        
        print("\n   --- 思考模式 ---")
        result_thinking = self.inference(medical_text, enable_thinking=True)
        
        print("\n   --- 直接模式 ---")
        result_direct = self.inference(medical_text, enable_thinking=False)
        
        print("\n✓ 所有测试完成")
        return True

def create_sample_data():
    """创建示例数据"""
    print("\n=== 创建示例数据 ===")
    
    sample_data = [
        {
            "instruction": "从医学文献中抽取实体和关系",
            "input": "Streptococcus pneumoniae is a major bacterial pathogen causing pneumonia.",
            "output": {
                "entities": [
                    {"text": "Streptococcus pneumoniae", "type": "Bacteria", "start": 0, "end": 24},
                    {"text": "pneumonia", "type": "Disease", "start": 65, "end": 74}
                ],
                "relations": [
                    {"entity1": "Streptococcus pneumoniae", "relation": "causes", "entity2": "pneumonia"}
                ]
            }
        },
        {
            "instruction": "分析医学研究结果",
            "input": "Clinical studies show that early antibiotic treatment reduces mortality.",
            "output": {
                "entities": [
                    {"text": "Clinical studies", "type": "Evidence", "start": 0, "end": 16},
                    {"text": "antibiotic treatment", "type": "Treatment", "start": 33, "end": 53}
                ],
                "relations": [
                    {"entity1": "antibiotic treatment", "relation": "reduces", "entity2": "mortality"}
                ]
            }
        }
    ]
    
    # 保存示例数据
    os.makedirs("mock_data", exist_ok=True)
    with open("mock_data/sample_training_data.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print("✓ 示例数据已保存到 mock_data/sample_training_data.json")
    return True

def main():
    """主函数"""
    print("🍎 Mac M2 稳定解决方案")
    print("=" * 50)
    
    print("这是一个模拟版本，可以在网络问题解决前使用")
    print("功能包括:")
    print("- 设备检测 (MPS/CUDA/CPU)")
    print("- 模拟tokenizer")
    print("- 模拟推理功能")
    print("- 思考模式支持")
    print("- 示例数据生成")
    
    # 创建模拟训练器
    trainer = MockMedicalTrainer()
    
    # 运行测试
    trainer.test_system()
    
    # 创建示例数据
    create_sample_data()
    
    print("\n=== 下一步建议 ===")
    print("1. 当网络稳定时，可以尝试下载真实模型")
    print("2. 使用这个模拟版本开发和测试代码逻辑")
    print("3. 准备训练数据和评估流程")
    print("4. 熟悉Apple Silicon MPS的使用")
    
    print("\n=== 网络问题解决方案 ===")
    print("1. 检查网络连接稳定性")
    print("2. 尝试使用手机热点或其他网络")
    print("3. 分时段下载（避开网络高峰期）")
    print("4. 使用断点续传功能")
    print("5. 考虑使用国内镜像源")
    
    print("\n模拟训练器可用于:")
    print("- 开发训练流程")
    print("- 测试数据处理")
    print("- 验证系统配置")
    print("- 学习Qwen3思考模式格式")

if __name__ == "__main__":
    main()
