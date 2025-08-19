#!/usr/bin/env python3
"""
Medical Entity Relationship Extraction Data Processing Module
Supports multiple fine-tuning format conversions and data augmentation
"""

import json
import random
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import re

@dataclass
class Entity:
    """Entity data class"""
    id: str
    start: int
    end: int
    text: str
    label: str
    from_name: str = "ner_label"

@dataclass
class Relation:
    """Relation data class"""
    subject: Entity
    relation: str
    object: Entity
    evidence: Entity = None

@dataclass
class MedicalRecord:
    """Medical record data class"""
    id: int
    text: str
    entities: List[Entity]
    relations: List[Relation]

class MedicalDataProcessor:
    """Medical data processor"""

    def __init__(self, data_path: str):
        self.data_path = Path(data_path)
        self.records: List[MedicalRecord] = []
        self.entity_labels = set()
        self.relation_types = set()

    def load_data(self) -> None:
        """Load raw JSON data"""
        with open(self.data_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)

        for item in raw_data:
            # Parse entities
            entities = []
            for ent_data in item.get('entities', []):
                entity = Entity(
                    id=ent_data['id'],
                    start=ent_data['start'],
                    end=ent_data['end'],
                    text=ent_data['text'],
                    label=ent_data['label'],
                    from_name=ent_data.get('from_name', 'ner_label')
                )
                entities.append(entity)
                self.entity_labels.add(entity.label)

            # Parse relations
            relations = []
            for rel_data in item.get('relations', []):
                # Build subject and object entities
                subj_data = rel_data['subject']
                obj_data = rel_data['object']

                subject = Entity(
                    id=subj_data['id'],
                    start=subj_data['start'],
                    end=subj_data['end'],
                    text=subj_data['text'],
                    label=subj_data['label']
                )

                object_ent = Entity(
                    id=obj_data['id'],
                    start=obj_data['start'],
                    end=obj_data['end'],
                    text=obj_data['text'],
                    label=obj_data['label']
                )

                # Evidence entity (if exists)
                evidence = None
                if 'evidence' in rel_data:
                    evid_data = rel_data['evidence']
                    evidence = Entity(
                        id=evid_data['id'],
                        start=evid_data['start'],
                        end=evid_data['end'],
                        text=evid_data['text'],
                        label=evid_data['label']
                    )

                relation = Relation(
                    subject=subject,
                    relation=rel_data['relation'],
                    object=object_ent,
                    evidence=evidence
                )
                relations.append(relation)
                self.relation_types.add(relation.relation)

            # Create medical record
            record = MedicalRecord(
                id=item['id'],
                text=item['text'],
                entities=entities,
                relations=relations
            )
            self.records.append(record)

        print(f"Loaded {len(self.records)} records")
        print(f"Entity types: {self.entity_labels}")
        print(f"Relation types: {self.relation_types}")

    def convert_to_instruction_format(self) -> List[Dict[str, str]]:
        """Convert to instruction fine-tuning format"""
        instruction_data = []

        # System prompt
        system_prompt = """
                            You are a professional medical literature analysis expert. Please extract entities and relationships from the given medical literature.

                            Entity Types:
                            - Bacteria: Bacteria, viruses, and other pathogens
                            - Disease: Diseases, symptoms, and pathological conditions
                            - Evidence: Research evidence, conclusions, and findings

                            Relationship Types:
                            - is_a: Hierarchical relationship (e.g., HCV is_a hepatitis C virus)
                            - biomarker_for: Biomarker relationship
                            - correlated_with: Correlation relationship
                            - has_relationship: General relationship

                            Please return results in JSON format:
                            {
                            "entities": [{"text": "entity text", "label": "entity type", "start": start_position, "end": end_position}],
                            "relations": [{"subject": "subject entity", "relation": "relation type", "object": "object entity", "evidence": "supporting evidence (optional)"}]
                            }
                        """

        for record in self.records:
            if not record.entities:  # Skip unannotated data
                continue

            # Build expected output
            expected_entities = []
            for ent in record.entities:
                expected_entities.append({
                    "text": ent.text,
                    "label": ent.label,
                    "start": ent.start,
                    "end": ent.end
                })

            expected_relations = []
            for rel in record.relations:
                rel_dict = {
                    "subject": rel.subject.text,
                    "relation": rel.relation,
                    "object": rel.object.text
                }
                if rel.evidence:
                    rel_dict["evidence"] = rel.evidence.text
                expected_relations.append(rel_dict)

            expected_output = {
                "entities": expected_entities,
                "relations": expected_relations
            }

            instruction_data.append({
                "instruction": f"Please extract entities and relationships from the following medical literature:\n\n{record.text}",
                "input": "",
                "output": json.dumps(expected_output, ensure_ascii=False, indent=2),
                "system": system_prompt
            })

        return instruction_data

    def convert_to_ner_format(self) -> List[Dict[str, Any]]:
        """Convert to NER training format (BIO tagging)"""
        ner_data = []

        for record in self.records:
            if not record.entities:
                continue

            # Tokenize text by spaces (simplified processing)
            tokens = record.text.split()
            labels = ['O'] * len(tokens)

            # Assign BIO labels to entities
            for entity in record.entities:
                entity_tokens = entity.text.split()
                # Simplified token matching (real applications need more precise alignment)
                for i, token in enumerate(tokens):
                    if token in entity_tokens:
                        if labels[i] == 'O':
                            labels[i] = f'B-{entity.label}'
                        elif labels[i].startswith('B-'):
                            labels[i] = f'I-{entity.label}'

            ner_data.append({
                "id": record.id,
                "tokens": tokens,
                "labels": labels
            })

        return ner_data

    def augment_data(self, augment_ratio: float = 0.3) -> List[MedicalRecord]:
        """Data augmentation: synonym replacement, sentence restructuring, etc."""
        augmented_records = []

        # Medical terminology synonym dictionary (example)
        synonyms = {
            "hepatitis C virus": ["HCV", "hepatitis C"],
            "multiple sclerosis": ["MS", "sclerosis multiplex"],
            "chronic infection": ["persistent infection", "long-term infection"],
            "antibody": ["immunoglobulin", "Ab"]
        }

        for record in self.records[:int(len(self.records) * augment_ratio)]:
            if not record.entities:
                continue

            # Synonym replacement augmentation
            augmented_text = record.text
            for original, syns in synonyms.items():
                if original in augmented_text:
                    replacement = random.choice(syns)
                    augmented_text = augmented_text.replace(original, replacement, 1)

            # Create augmented record (entity positions need updating)
            if augmented_text != record.text:
                # Simplified processing: keep original entities and relations
                augmented_record = MedicalRecord(
                    id=f"{record.id}_aug",
                    text=augmented_text,
                    entities=record.entities,  # In real applications, positions need recalculation
                    relations=record.relations
                )
                augmented_records.append(augmented_record)

        return augmented_records

    def split_dataset(self, train_ratio: float = 0.7, val_ratio: float = 0.15) -> Tuple[List[MedicalRecord], List[MedicalRecord], List[MedicalRecord]]:
        """Split dataset"""
        # Only use annotated data
        annotated_records = [r for r in self.records if r.entities]

        random.shuffle(annotated_records)

        n_train = int(len(annotated_records) * train_ratio)
        n_val = int(len(annotated_records) * val_ratio)

        train_data = annotated_records[:n_train]
        val_data = annotated_records[n_train:n_train + n_val]
        test_data = annotated_records[n_train + n_val:]

        return train_data, val_data, test_data

    def save_processed_data(self, output_dir: str) -> None:
        """Save processed data"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Split data
        train_data, val_data, test_data = self.split_dataset()

        # Save instruction fine-tuning format
        instruction_data = self.convert_to_instruction_format()
        with open(output_path / "instruction_data.json", 'w', encoding='utf-8') as f:
            json.dump(instruction_data, f, ensure_ascii=False, indent=2)

        # Save NER format
        ner_data = self.convert_to_ner_format()
        with open(output_path / "ner_data.json", 'w', encoding='utf-8') as f:
            json.dump(ner_data, f, ensure_ascii=False, indent=2)

        # Save dataset splits
        datasets = {
            "train": [{"id": r.id, "text": r.text, "entities": [{"text": e.text, "label": e.label, "start": e.start, "end": e.end} for e in r.entities], "relations": [{"subject": rel.subject.text, "relation": rel.relation, "object": rel.object.text} for rel in r.relations]} for r in train_data],
            "validation": [{"id": r.id, "text": r.text, "entities": [{"text": e.text, "label": e.label, "start": e.start, "end": e.end} for e in r.entities], "relations": [{"subject": rel.subject.text, "relation": rel.relation, "object": rel.object.text} for rel in r.relations]} for r in val_data],
            "test": [{"id": r.id, "text": r.text, "entities": [{"text": e.text, "label": e.label, "start": e.start, "end": e.end} for e in r.entities], "relations": [{"subject": rel.subject.text, "relation": rel.relation, "object": rel.object.text} for rel in r.relations]} for r in test_data]
        }

        for split, data in datasets.items():
            with open(output_path / f"{split}_data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"Data saved to {output_path}")
        print(f"Training set: {len(train_data)} records")
        print(f"Validation set: {len(val_data)} records")
        print(f"Test set: {len(test_data)} records")

def main():
    """Main function"""
    processor = MedicalDataProcessor("output.json")
    processor.load_data()
    processor.save_processed_data("processed_data")

if __name__ == "__main__":
    main()
