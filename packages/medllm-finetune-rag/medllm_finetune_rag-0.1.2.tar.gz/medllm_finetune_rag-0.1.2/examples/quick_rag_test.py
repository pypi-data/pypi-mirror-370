#!/usr/bin/env python3
"""
Quick RAG-Anything Test

A simple test to verify RAG-Anything integration works correctly.
This test can run without API keys for basic functionality testing.
"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.medical_rag_system import MedicalRAGSystem
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def quick_test():
    """Quick test of RAG system initialization and basic functionality"""
    print("🧪 Quick RAG-Anything Test")
    print("=" * 30)
    
    # Test 1: System Initialization
    print("1️⃣  Testing system initialization...")
    try:
        rag_system = MedicalRAGSystem(
            working_dir="./test_rag_workspace",
            api_key=os.getenv('OPENAI_API_KEY'),  # Can be None for basic testing
            model_name="gpt-4o-mini",
            parser="mineru",
            parse_method="auto"
        )
        
        stats = rag_system.get_stats()
        print("   ✅ RAG system initialized successfully")
        print(f"   📊 Parser: {stats['parser']}")
        print(f"   📊 Components: {stats['components']}")
        
    except Exception as e:
        print(f"   ❌ Initialization failed: {e}")
        return False
    
    # Test 2: Configuration Loading
    print("\n2️⃣  Testing configuration compatibility...")
    try:
        import yaml
        
        # Test loading Mac M2 config
        with open("config/config_mac_m2.yaml", 'r') as f:
            config = yaml.safe_load(f)
        
        rag_config = config.get('rag', {})
        if rag_config:
            print("   ✅ RAG configuration found in config file")
            print(f"   📊 Working dir: {rag_config.get('working_dir', 'default')}")
            print(f"   📊 Parser: {rag_config.get('parser', 'default')}")
        else:
            print("   ❌ No RAG configuration found")
            
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
    
    # Test 3: Component Import Test
    print("\n3️⃣  Testing component imports...")
    try:
        from raganything import RAGAnything
        print("   ✅ RAGAnything import successful")
    except ImportError as e:
        print(f"   ❌ RAGAnything import failed: {e}")
        return False
    
    try:
        from lightrag import LightRAG
        print("   ✅ LightRAG import successful")
    except ImportError as e:
        print(f"   ⚠️  LightRAG import failed: {e}")
    
    try:
        from raganything.modal_processors import ModalProcessors
        print("   ✅ ModalProcessors import successful")
    except ImportError as e:
        print(f"   ⚠️  ModalProcessors import failed: {e}")
    
    # Test 4: Basic Functionality (without API)
    print("\n4️⃣  Testing basic functionality...")
    try:
        # Test multimodal content processing structure
        sample_content = [
            {"type": "text", "content": "Sample medical text"},
            {"type": "table", "content": {"data": [["Header1", "Header2"], ["Data1", "Data2"]]}},
            {"type": "equation", "content": "E = mc²"}
        ]
        
        # Test text extraction
        extracted = rag_system._extract_text_from_content(sample_content)
        if extracted:
            print("   ✅ Text extraction working")
            print(f"   📝 Sample extracted: {extracted[:100]}...")
        else:
            print("   ⚠️  Text extraction returned empty")
            
    except Exception as e:
        print(f"   ❌ Basic functionality test failed: {e}")
    
    # Test 5: API Key Check
    print("\n5️⃣  Checking API configuration...")
    api_key = os.getenv('OPENAI_API_KEY')
    if api_key:
        print(f"   ✅ API key found (length: {len(api_key)})")
        print("   💡 Full RAG functionality available")
    else:
        print("   ⚠️  No API key found")
        print("   💡 Set OPENAI_API_KEY in .env for full functionality")
    
    # Test 6: Cleanup Test
    print("\n6️⃣  Testing cleanup...")
    try:
        await rag_system.clear_knowledge_base()
        print("   ✅ Cleanup successful")
    except Exception as e:
        print(f"   ⚠️  Cleanup warning: {e}")
    
    print("\n" + "=" * 30)
    print("🎉 Quick test completed!")
    print("\n💡 Next steps:")
    print("   - Run examples/medical_rag_demo.py for full demo")
    print("   - Set OPENAI_API_KEY for complete functionality")
    print("   - Try processing medical documents")
    
    return True

if __name__ == "__main__":
    asyncio.run(quick_test())
