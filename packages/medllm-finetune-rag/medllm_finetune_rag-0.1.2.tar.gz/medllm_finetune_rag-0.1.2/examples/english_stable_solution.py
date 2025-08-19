#!/usr/bin/env python3
"""
Mac M2 Stable Solution - Using local simulation and offline mode
English Version
"""

import torch
import json
import os
from pathlib import Path

class MockMedicalTrainer:
    """Mock Medical Trainer - for testing environment and functionality"""
    
    def __init__(self):
        self.model_name = "mock-qwen3-4b-thinking"
        self.device = self._detect_device()
        self.setup_mock_tokenizer()
        print(f"✓ Mock trainer initialized successfully (device: {self.device})")
    
    def _detect_device(self):
        """Detect available device"""
        if torch.backends.mps.is_available():
            return "mps"
        elif torch.cuda.is_available():
            return "cuda"
        else:
            return "cpu"
    
    def setup_mock_tokenizer(self):
        """Setup mock tokenizer"""
        # Create simple vocabulary
        self.vocab = {
            "<pad>": 0, "<unk>": 1, "<s>": 2, "</s>": 3,
            "medical": 4, "patient": 5, "disease": 6, "treatment": 7,
            "bacteria": 8, "virus": 9, "infection": 10, "diagnosis": 11,
            "symptom": 12, "therapy": 13, "medicine": 14, "hospital": 15,
            "doctor": 16, "nurse": 17, "health": 18, "care": 19,
            # Add common words
            "the": 20, "and": 21, "is": 22, "of": 23, "in": 24, "to": 25,
            "a": 26, "with": 27, "for": 28, "by": 29, "from": 30, "that": 31,
            "causes": 32, "associated": 33, "study": 34, "research": 35
        }
        self.reverse_vocab = {v: k for k, v in self.vocab.items()}
        print("✓ Mock tokenizer setup complete")
    
    def encode(self, text):
        """Simple encoding"""
        words = text.lower().split()
        tokens = []
        for word in words:
            if word in self.vocab:
                tokens.append(self.vocab[word])
            else:
                tokens.append(self.vocab["<unk>"])
        return tokens
    
    def decode(self, tokens):
        """Simple decoding"""
        words = []
        for token in tokens:
            if token in self.reverse_vocab:
                words.append(self.reverse_vocab[token])
            else:
                words.append("<unk>")
        return " ".join(words)
    
    def inference(self, text, enable_thinking=True):
        """Mock inference"""
        print(f"🧠 Mock inference (thinking mode: {enable_thinking})")
        print(f"Input: {text}")
        
        # Mock encoding
        tokens = self.encode(text)
        print(f"Encoding: {tokens}")
        
        # Mock medical entity recognition
        entities = []
        relations = []
        
        # Simple rule matching
        text_lower = text.lower()
        
        # Entity detection rules
        if "bacteria" in text_lower or "virus" in text_lower:
            if "hepatitis" in text_lower:
                entities.append({"text": "Hepatitis C virus", "type": "Bacteria", "start": 0, "end": 17})
            elif "pylori" in text_lower:
                entities.append({"text": "Helicobacter pylori", "type": "Bacteria", "start": 0, "end": 19})
            else:
                entities.append({"text": "pathogen", "type": "Bacteria", "start": 0, "end": 8})
        
        if "disease" in text_lower or "infection" in text_lower or "cirrhosis" in text_lower:
            if "liver" in text_lower:
                entities.append({"text": "liver disease", "type": "Disease", "start": 20, "end": 33})
            elif "pneumonia" in text_lower:
                entities.append({"text": "pneumonia", "type": "Disease", "start": 20, "end": 29})
            else:
                entities.append({"text": "infection", "type": "Disease", "start": 20, "end": 29})
        
        if "study" in text_lower or "research" in text_lower or "evidence" in text_lower:
            entities.append({"text": "clinical evidence", "type": "Evidence", "start": 40, "end": 57})
        
        # Mock relations
        if len(entities) >= 2:
            relations.append({
                "entity1": entities[0]["text"],
                "relation": "correlated_with",
                "entity2": entities[1]["text"]
            })
        
        # Build response
        if enable_thinking:
            response = f"""<think>
I need to analyze this medical text to identify entities and relationships.

From the text, I can identify:
- Potential pathogen-related terms
- Disease or infection-related content
- Research evidence-related information

Let me organize this into JSON format.
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
        
        print(f"Output: {response[:200]}...")
        return response
    
    def test_system(self):
        """Test system functionality"""
        print("\n=== System Functionality Test ===")
        
        # Test 1: Device detection
        print(f"1. Device detection: {self.device}")
        
        # Test 2: Encoding/decoding
        test_text = "medical bacteria infection"
        tokens = self.encode(test_text)
        decoded = self.decode(tokens)
        print(f"2. Encoding/decoding test:")
        print(f"   Original: {test_text}")
        print(f"   Encoded: {tokens}")
        print(f"   Decoded: {decoded}")
        
        # Test 3: Inference functionality
        print("3. Inference functionality test:")
        medical_text = "Helicobacter pylori bacteria causes gastric infection and disease"
        
        print("\n   --- Thinking Mode ---")
        result_thinking = self.inference(medical_text, enable_thinking=True)
        
        print("\n   --- Direct Mode ---")
        result_direct = self.inference(medical_text, enable_thinking=False)
        
        print("\n✓ All tests completed")
        return True

def create_sample_data():
    """Create sample data"""
    print("\n=== Creating Sample Data ===")
    
    sample_data = [
        {
            "instruction": "Extract entities and relationships from medical literature",
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
            "instruction": "Analyze medical research results",
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
    
    # Save sample data
    os.makedirs("mock_data", exist_ok=True)
    with open("mock_data/sample_training_data_english.json", "w", encoding="utf-8") as f:
        json.dump(sample_data, f, ensure_ascii=False, indent=2)
    
    print("✓ Sample data saved to mock_data/sample_training_data_english.json")
    return True

def main():
    """Main function"""
    print("🍎 Mac M2 Stable Solution (English Version)")
    print("=" * 60)
    
    print("This is a mock version that can be used while network issues are resolved")
    print("Features include:")
    print("- Device detection (MPS/CUDA/CPU)")
    print("- Mock tokenizer")
    print("- Mock inference functionality")
    print("- Thinking mode support")
    print("- Sample data generation")
    
    # Create mock trainer
    trainer = MockMedicalTrainer()
    
    # Run tests
    trainer.test_system()
    
    # Create sample data
    create_sample_data()
    
    print("\n=== Next Steps Recommendations ===")
    print("1. When network is stable, try downloading the real model")
    print("2. Use this mock version to develop and test code logic")
    print("3. Prepare training data and evaluation pipeline")
    print("4. Get familiar with Apple Silicon MPS usage")
    
    print("\n=== Network Issue Solutions ===")
    print("1. Check network connection stability")
    print("2. Try using mobile hotspot or different network")
    print("3. Download during off-peak hours")
    print("4. Use resume download functionality")
    print("5. Consider using domestic mirror sources")
    
    print("\n=== Mock Trainer Usage ===")
    print("The mock trainer can be used for:")
    print("- Developing training pipeline")
    print("- Testing data processing")
    print("- Validating system configuration")
    print("- Learning Qwen3 thinking mode format")
    
    print("\n=== Example Usage ===")
    print("trainer = MockMedicalTrainer()")
    print("result = trainer.inference('Your medical text here', enable_thinking=True)")
    print("print(result)")

if __name__ == "__main__":
    main()
