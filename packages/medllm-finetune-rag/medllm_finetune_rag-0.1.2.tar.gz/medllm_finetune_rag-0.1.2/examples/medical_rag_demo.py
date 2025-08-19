#!/usr/bin/env python3
"""
Medical RAG-Anything Demo

This example demonstrates how to use the integrated RAG-Anything system
for processing medical documents and performing retrieval-augmented generation.
"""

import os
import sys
import asyncio
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from core.medical_rag_system import MedicalRAGSystem
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MedicalRAGDemo:
    """Demonstration of Medical RAG-Anything capabilities"""
    
    def __init__(self):
        """Initialize the demo"""
        self.rag_system = None
        
    async def setup_rag_system(self):
        """Setup the RAG system"""
        print("🚀 Setting up Medical RAG-Anything System")
        print("=" * 50)
        
        # Initialize with environment variables
        api_key = os.getenv('OPENAI_API_KEY')
        base_url = os.getenv('OPENAI_BASE_URL')
        
        if not api_key:
            print("⚠️  No OpenAI API key found. Some features will be limited.")
            print("   Set OPENAI_API_KEY in your .env file for full functionality.")
        
        self.rag_system = MedicalRAGSystem(
            working_dir="./demo_rag_workspace",
            api_key=api_key,
            base_url=base_url,
            model_name="gpt-4o-mini",
            parser="mineru",
            parse_method="auto",
            chunk_size=1200,
            chunk_overlap=100,
            top_k=5
        )
        
        # Display system stats
        stats = self.rag_system.get_stats()
        print(f"✅ RAG System initialized")
        print(f"   - Parser: {stats['parser']}")
        print(f"   - Parse method: {stats['parse_method']}")
        print(f"   - Components: {stats['components']}")
        print()
    
    async def demo_json_knowledge_base(self):
        """Demonstrate building knowledge base from JSON data"""
        print("📚 Demo: Building Knowledge Base from JSON Data")
        print("-" * 40)
        
        # Create sample medical data
        sample_data = [
            {
                "id": 1,
                "text": "Hepatitis C virus (HCV) is a major cause of chronic liver disease worldwide. It is transmitted through blood contact and can lead to liver cirrhosis and hepatocellular carcinoma.",
                "entities": [
                    {"text": "Hepatitis C virus", "label": "Bacteria", "start": 0, "end": 17},
                    {"text": "HCV", "label": "Bacteria", "start": 19, "end": 22},
                    {"text": "chronic liver disease", "label": "Disease", "start": 42, "end": 63},
                    {"text": "liver cirrhosis", "label": "Disease", "start": 130, "end": 145},
                    {"text": "hepatocellular carcinoma", "label": "Disease", "start": 150, "end": 174}
                ],
                "relations": [
                    {"subject": "Hepatitis C virus", "relation": "causes", "object": "chronic liver disease"},
                    {"subject": "HCV", "relation": "is_a", "object": "Hepatitis C virus"},
                    {"subject": "HCV", "relation": "causes", "object": "liver cirrhosis"},
                    {"subject": "HCV", "relation": "causes", "object": "hepatocellular carcinoma"}
                ]
            },
            {
                "id": 2,
                "text": "Streptococcus pneumoniae is a gram-positive bacterial pathogen that commonly causes pneumonia, meningitis, and sepsis in children and elderly patients.",
                "entities": [
                    {"text": "Streptococcus pneumoniae", "label": "Bacteria", "start": 0, "end": 24},
                    {"text": "pneumonia", "label": "Disease", "start": 85, "end": 94},
                    {"text": "meningitis", "label": "Disease", "start": 96, "end": 106},
                    {"text": "sepsis", "label": "Disease", "start": 112, "end": 118}
                ],
                "relations": [
                    {"subject": "Streptococcus pneumoniae", "relation": "causes", "object": "pneumonia"},
                    {"subject": "Streptococcus pneumoniae", "relation": "causes", "object": "meningitis"},
                    {"subject": "Streptococcus pneumoniae", "relation": "causes", "object": "sepsis"}
                ]
            },
            {
                "id": 3,
                "text": "Clinical studies demonstrate that elevated C-reactive protein (CRP) levels serve as a biomarker for systemic inflammation and are correlated with increased risk of cardiovascular disease.",
                "entities": [
                    {"text": "C-reactive protein", "label": "Evidence", "start": 43, "end": 61},
                    {"text": "CRP", "label": "Evidence", "start": 63, "end": 66},
                    {"text": "systemic inflammation", "label": "Disease", "start": 101, "end": 122},
                    {"text": "cardiovascular disease", "label": "Disease", "start": 162, "end": 184}
                ],
                "relations": [
                    {"subject": "C-reactive protein", "relation": "biomarker_for", "object": "systemic inflammation"},
                    {"subject": "CRP", "relation": "is_a", "object": "C-reactive protein"},
                    {"subject": "CRP", "relation": "correlated_with", "object": "cardiovascular disease"}
                ]
            }
        ]
        
        # Save sample data to file
        sample_file = "demo_medical_data.json"
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        print(f"📄 Created sample data file: {sample_file}")
        
        # Build knowledge base from JSON
        try:
            self.rag_system.build_knowledge_base_from_json(sample_file)
            print("✅ Knowledge base built successfully from JSON data")
        except Exception as e:
            print(f"❌ Error building knowledge base: {e}")
        
        # Clean up
        if os.path.exists(sample_file):
            os.remove(sample_file)
        
        print()
    
    async def demo_document_processing(self):
        """Demonstrate document processing (requires actual documents)"""
        print("📄 Demo: Document Processing")
        print("-" * 30)
        
        # This would process actual documents if they exist
        sample_documents = [
            "medical_paper.pdf",
            "clinical_report.docx", 
            "research_data.xlsx"
        ]
        
        existing_docs = [doc for doc in sample_documents if os.path.exists(doc)]
        
        if not existing_docs:
            print("ℹ️  No sample documents found. To test document processing:")
            print("   1. Place PDF, DOCX, or other medical documents in the current directory")
            print("   2. Run this demo again")
            print("   3. The system will automatically parse and index the documents")
            print()
            return
        
        print(f"📚 Found {len(existing_docs)} documents to process:")
        for doc in existing_docs:
            print(f"   - {doc}")
        
        try:
            results = await self.rag_system.add_documents_batch(existing_docs)
            
            print("✅ Document processing results:")
            for result in results:
                if 'error' in result:
                    print(f"   ❌ {result['file_path']}: {result['error']}")
                else:
                    print(f"   ✅ {result.get('file_path', 'Unknown')}: Processed successfully")
        
        except Exception as e:
            print(f"❌ Error processing documents: {e}")
        
        print()
    
    async def demo_multimodal_content(self):
        """Demonstrate multimodal content processing"""
        print("🖼️  Demo: Multimodal Content Processing")
        print("-" * 40)
        
        # Sample multimodal content
        multimodal_content = [
            {
                "type": "text",
                "content": "This table shows the correlation between HbA1c levels and diabetic complications."
            },
            {
                "type": "table",
                "content": {
                    "data": [
                        ["HbA1c Level", "Complication Risk", "Patient Count"],
                        ["< 7%", "Low", "150"],
                        ["7-8%", "Moderate", "200"],
                        ["> 8%", "High", "100"]
                    ]
                }
            },
            {
                "type": "equation",
                "content": "HbA1c = (Average Blood Glucose + 46.7) / 28.7"
            },
            {
                "type": "image",
                "content": "chest_xray_001.jpg",
                "description": "Chest X-ray showing bilateral pneumonia"
            }
        ]
        
        try:
            processed_content = await self.rag_system.process_multimodal_content(multimodal_content)
            
            print("✅ Multimodal content processed:")
            for i, item in enumerate(processed_content):
                content_type = item.get('type', 'unknown')
                print(f"   {i+1}. Type: {content_type}")
                if content_type == 'error':
                    print(f"      Error: {item.get('content', 'Unknown error')}")
                else:
                    content_preview = str(item.get('content', ''))[:100]
                    if len(content_preview) == 100:
                        content_preview += "..."
                    print(f"      Content: {content_preview}")
        
        except Exception as e:
            print(f"❌ Error processing multimodal content: {e}")
        
        print()
    
    async def demo_rag_queries(self):
        """Demonstrate RAG-based queries"""
        print("🔍 Demo: RAG-based Queries")
        print("-" * 25)
        
        # Sample medical queries
        queries = [
            "What are the causes of liver cirrhosis?",
            "Which bacteria commonly cause pneumonia?",
            "What biomarkers are associated with inflammation?",
            "How is HCV related to liver disease?",
            "What are the complications of Streptococcus pneumoniae infection?"
        ]
        
        for i, query in enumerate(queries, 1):
            print(f"\n📝 Query {i}: {query}")
            print("-" * (len(query) + 12))
            
            try:
                # Try different search modes
                modes = ["local", "global", "hybrid"]
                
                for mode in modes:
                    print(f"\n🔎 Search mode: {mode}")
                    response = await self.rag_system.generate_response(query, mode=mode)
                    
                    # Truncate response for demo
                    if len(response) > 200:
                        response = response[:200] + "..."
                    
                    print(f"💬 Response: {response}")
                    
                    # Only show first mode for demo brevity
                    break
            
            except Exception as e:
                print(f"❌ Error generating response: {e}")
            
            # Only show first few queries for demo
            if i >= 2:
                print(f"\n... (showing {i} of {len(queries)} queries for demo)")
                break
        
        print()
    
    async def demo_system_stats(self):
        """Display system statistics"""
        print("📊 System Statistics")
        print("-" * 20)
        
        stats = self.rag_system.get_stats()
        
        print("🔧 Configuration:")
        print(f"   - Working Directory: {stats['working_dir']}")
        print(f"   - Parser: {stats['parser']}")
        print(f"   - Parse Method: {stats['parse_method']}")
        print(f"   - Model: {stats['model_name']}")
        print(f"   - Chunk Size: {stats['chunk_size']}")
        print(f"   - Top K: {stats['top_k']}")
        
        print("\n🧩 Components:")
        for component, available in stats['components'].items():
            status = "✅" if available else "❌"
            print(f"   - {component}: {status}")
        
        if stats.get('lightrag_stats'):
            print("\n🧠 Knowledge Graph:")
            kg_stats = stats['lightrag_stats']
            for key, value in kg_stats.items():
                status = "✅" if value else "❌"
                print(f"   - {key.replace('_', ' ').title()}: {status}")
        
        print()
    
    async def run_demo(self):
        """Run the complete demo"""
        print("🏥 Medical RAG-Anything Demo")
        print("=" * 60)
        print("This demo showcases the integrated RAG-Anything system")
        print("for medical document processing and knowledge retrieval.")
        print("=" * 60)
        print()
        
        try:
            # Setup
            await self.setup_rag_system()
            
            # Run demo sections
            await self.demo_json_knowledge_base()
            await self.demo_document_processing()
            await self.demo_multimodal_content()
            await self.demo_rag_queries()
            await self.demo_system_stats()
            
            print("✅ Demo completed successfully!")
            print("\n💡 Next Steps:")
            print("   1. Add your own medical documents to test document processing")
            print("   2. Set OPENAI_API_KEY for full RAG functionality")
            print("   3. Experiment with different parsers and search modes")
            print("   4. Integrate with your existing medical LLM training pipeline")
            
        except Exception as e:
            print(f"❌ Demo failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            # Cleanup demo workspace
            try:
                if self.rag_system:
                    await self.rag_system.clear_knowledge_base()
                    print("\n🧹 Demo workspace cleaned up")
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up workspace: {e}")

async def main():
    """Main demo function"""
    demo = MedicalRAGDemo()
    await demo.run_demo()

if __name__ == "__main__":
    # Run the demo
    asyncio.run(main())
