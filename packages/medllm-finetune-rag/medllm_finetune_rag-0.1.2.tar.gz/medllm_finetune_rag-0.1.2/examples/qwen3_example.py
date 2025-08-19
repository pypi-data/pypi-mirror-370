#!/usr/bin/env python3
"""
Qwen3-4B-Thinking-2507 医学LLM微调示例
基于官方Unsloth实现模式
"""

from medical_llm_trainer import MedicalLLMTrainer
import json

def create_sample_medical_data():
    """创建示例医学数据"""
    sample_data = [
        {
            "system": "你是一个专业的医学文献分析专家。",
            "instruction": "从以下医学文献中抽取实体和关系",
            "input": "Helicobacter pylori infection is strongly associated with gastric cancer development. Studies show that H. pylori acts as a biomarker for gastric adenocarcinoma risk assessment.",
            "output": """<think>
我需要分析这段医学文献，识别出其中的实体和关系。

实体识别：
1. Helicobacter pylori - 这是一种细菌，属于Bacteria类型
2. gastric cancer - 这是一种疾病，属于Disease类型  
3. gastric adenocarcinoma - 这也是一种疾病，属于Disease类型
4. Studies - 这是研究证据，属于Evidence类型

关系识别：
1. Helicobacter pylori infection is strongly associated with gastric cancer - 这表明细菌与疾病之间存在相关关系
2. H. pylori acts as a biomarker for gastric adenocarcinoma - 这表明细菌作为疾病的生物标志物

让我整理成JSON格式。
</think>

{
  "entities": [
    {"text": "Helicobacter pylori", "type": "Bacteria", "start": 0, "end": 18},
    {"text": "gastric cancer", "type": "Disease", "start": 58, "end": 72},
    {"text": "gastric adenocarcinoma", "type": "Disease", "start": 140, "end": 162},
    {"text": "Studies", "type": "Evidence", "start": 85, "end": 92}
  ],
  "relations": [
    {"entity1": "Helicobacter pylori", "relation": "correlated_with", "entity2": "gastric cancer"},
    {"entity1": "Helicobacter pylori", "relation": "biomarker_for", "entity2": "gastric adenocarcinoma"}
  ]
}"""
        },
        {
            "system": "你是一个专业的医学文献分析专家。",
            "instruction": "从以下医学文献中抽取实体和关系",
            "input": "COVID-19 patients show elevated levels of inflammatory biomarkers. IL-6 and CRP are commonly used as prognostic indicators.",
            "output": """<think>
这段文本涉及COVID-19和相关的生物标志物。

实体识别：
1. COVID-19 - 疾病，Disease类型
2. inflammatory biomarkers - 这是一般性的证据/发现，Evidence类型
3. IL-6 - 这是一个生物标志物，可以归类为Evidence
4. CRP - 也是生物标志物，Evidence类型
5. prognostic indicators - 预后指标，Evidence类型

关系识别：
1. COVID-19 patients show elevated levels of inflammatory biomarkers - COVID-19与炎症标志物相关
2. IL-6 and CRP are commonly used as prognostic indicators - IL-6和CRP用作预后指标
</think>

{
  "entities": [
    {"text": "COVID-19", "type": "Disease", "start": 0, "end": 8},
    {"text": "inflammatory biomarkers", "type": "Evidence", "start": 44, "end": 67},
    {"text": "IL-6", "type": "Evidence", "start": 69, "end": 73},
    {"text": "CRP", "type": "Evidence", "start": 78, "end": 81},
    {"text": "prognostic indicators", "type": "Evidence", "start": 102, "end": 123}
  ],
  "relations": [
    {"entity1": "COVID-19", "relation": "correlated_with", "entity2": "inflammatory biomarkers"},
    {"entity1": "IL-6", "relation": "biomarker_for", "entity2": "COVID-19"},
    {"entity1": "CRP", "relation": "biomarker_for", "entity2": "COVID-19"}
  ]
}"""
        }
    ]
    
    return sample_data

def main():
    """主函数演示"""
    print("=== Qwen3-4B-Thinking-2507 医学LLM微调示例 ===\n")
    
    # 创建示例数据
    print("1. 创建示例医学数据...")
    sample_data = create_sample_medical_data()
    
    # 保存示例数据
    with open("sample_medical_data.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    print("   ✓ 示例数据已保存到 sample_medical_data.json")
    
    # 初始化训练器
    print("\n2. 初始化Qwen3-4B-Thinking-2507训练器...")
    trainer = MedicalLLMTrainer(
        model_name="Qwen/Qwen3-4B-Thinking-2507",
        output_dir="./qwen3_medical_output",
        use_qlora=True,
        max_seq_length=2048,
        use_unsloth=True  # 使用Unsloth加速
    )
    print("   ✓ 模型加载完成")
    
    # 测试推理能力
    print("\n3. 测试模型推理能力...")
    test_text = "Streptococcus pneumoniae is a major cause of pneumonia and meningitis in children."
    
    print("\n   --- Thinking模式推理 ---")
    result_thinking = trainer.inference(test_text, max_length=1024, enable_thinking=True)
    print(f"   结果: {result_thinking}")
    
    print("\n   --- 直接推理模式 ---")
    result_direct = trainer.inference(test_text, max_length=512, enable_thinking=False)
    print(f"   结果: {result_direct}")
    
    print("\n=== 示例完成 ===")
    print("\n要开始完整训练，请运行:")
    print("python medical_llm_trainer.py")
    print("\n训练特性:")
    print("✓ 使用Unsloth加速，2x更快训练，70%更少VRAM")
    print("✓ 支持Qwen3-4B-Thinking-2507思考模式")
    print("✓ 优化的医学实体关系抽取")
    print("✓ 自动应用官方chat template")
    print("✓ train_on_responses_only优化")

if __name__ == "__main__":
    main()
