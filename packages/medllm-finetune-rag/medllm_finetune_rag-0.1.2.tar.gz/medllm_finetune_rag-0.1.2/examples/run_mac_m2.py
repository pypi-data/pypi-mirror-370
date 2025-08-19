#!/usr/bin/env python3
"""
Mac M2/M3 Apple Silicon 专用启动脚本
Qwen3-4B-Thinking-2507 医学LLM微调
"""

import os
import sys
import torch
import psutil
from pathlib import Path
from medical_llm_trainer import MedicalLLMTrainer
import warnings

# 抑制MPS相关警告
warnings.filterwarnings("ignore", category=UserWarning, module="torch")

def check_system_requirements():
    """检查系统要求"""
    print("=== 系统环境检查 ===")
    
    # 检查Python版本
    python_version = sys.version_info
    print(f"Python版本: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # 检查内存
    memory = psutil.virtual_memory()
    print(f"系统内存: {memory.total // (1024**3)} GB (可用: {memory.available // (1024**3)} GB)")
    
    # 检查PyTorch和MPS
    print(f"PyTorch版本: {torch.__version__}")
    
    if torch.backends.mps.is_available():
        print("✓ Apple Silicon MPS 可用")
        device = "mps"
    elif torch.cuda.is_available():
        print(f"✓ CUDA 可用: {torch.cuda.get_device_name(0)}")
        device = "cuda"
    else:
        print("⚠️ 仅CPU可用")
        device = "cpu"
    
    print(f"推荐训练设备: {device}")
    
    # 内存建议
    if memory.total < 16 * (1024**3):  # 小于16GB
        print("⚠️ 内存较小，建议使用更小的batch_size和max_length")
    
    return device

def optimize_for_mac_m2():
    """Mac M2优化设置"""
    print("\n=== Mac M2 优化设置 ===")
    
    # 设置MPS环境变量
    os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
    os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
    
    # 检查虚拟环境
    if os.environ.get('VIRTUAL_ENV'):
        print(f"✓ 虚拟环境已激活: {os.environ['VIRTUAL_ENV']}")
    else:
        print("⚠️ 建议使用虚拟环境")
        print("请运行: source venv/bin/activate")
    
    print("✓ MPS优化设置已应用")

def main():
    """主函数"""
    print("🍎 Mac M2/M3 Qwen3-4B-Thinking-2507 医学LLM微调")
    print("=" * 50)
    
    # 系统检查
    device = check_system_requirements()
    
    # Mac M2优化
    optimize_for_mac_m2()
    
    # 检查Unsloth可用性
    print("\n=== 检查加速库 ===")
    try:
        from unsloth import FastModel
        unsloth_available = True
        print("✓ Unsloth可用 - 将使用加速训练")
    except ImportError:
        unsloth_available = False
        print("⚠️ Unsloth不可用 - 使用标准训练")
    
    # 配置训练参数
    print("\n=== 配置训练参数 ===")
    
    # Mac M2优化配置
    config = {
        "model_name": "Qwen/Qwen3-4B-Thinking-2507",
        "output_dir": "./medical_llm_output_mac_m2",
        "use_qlora": False,  # Mac M2建议关闭量化
        "max_seq_length": 1024,  # 降低以节省内存
        "use_unsloth": unsloth_available
    }
    
    # 根据内存调整配置
    memory_gb = psutil.virtual_memory().total // (1024**3)
    if memory_gb < 16:
        config["max_seq_length"] = 512
        print("⚠️ 内存较小，降低max_seq_length到512")
    
    print(f"模型: {config['model_name']}")
    print(f"量化: {'关闭' if not config['use_qlora'] else '开启'}")
    print(f"序列长度: {config['max_seq_length']}")
    print(f"Unsloth加速: {'开启' if config['use_unsloth'] else '关闭'}")
    
    # 初始化训练器
    print("\n=== 初始化训练器 ===")
    try:
        trainer = MedicalLLMTrainer(**config)
        print("✓ 训练器初始化成功")
    except Exception as e:
        print(f"✗ 训练器初始化失败: {e}")
        print("\n建议:")
        print("1. 检查是否在虚拟环境中: source venv/bin/activate")
        print("2. 重新运行安装脚本: ./setup_qwen3.sh")
        print("3. 如果内存不足，尝试关闭其他应用程序")
        return
    
    # 测试推理
    print("\n=== 测试推理能力 ===")
    test_text = "Helicobacter pylori infection causes gastric inflammation and is linked to peptic ulcers."
    
    try:
        print("测试思考模式推理...")
        result = trainer.inference(test_text, max_length=256, enable_thinking=True)
        print(f"✓ 推理成功")
        print(f"结果预览: {result[:100]}...")
    except Exception as e:
        print(f"⚠️ 推理测试失败: {e}")
        print("这可能是内存不足或模型加载问题")
    
    # 训练建议
    print("\n=== 训练建议 ===")
    print("Mac M2/M3 训练配置建议:")
    print("- batch_size: 1")
    print("- gradient_accumulation_steps: 8")
    print("- max_seq_length: 1024 (或更小)")
    print("- use_qlora: False (避免量化问题)")
    print("- 定期保存检查点")
    print("- 监控内存使用情况")
    
    print("\n开始完整训练请运行:")
    print("python medical_llm_trainer.py")
    print("\n或使用Mac M2优化配置:")
    print("python medical_llm_trainer.py --config config_mac_m2.yaml")

if __name__ == "__main__":
    main()
