#!/usr/bin/env python3
"""
医学实体关系抽取评估指标
提供NER和RE任务的专业评估方法
"""

import json
import re
from typing import List, Dict, Any, Tuple, Set
from collections import defaultdict
import numpy as np
from sklearn.metrics import precision_recall_fscore_support, classification_report

class EntityEvaluator:
    """实体抽取评估器"""

    def __init__(self):
        self.entity_types = {"Bacteria", "Disease", "Evidence"}

    def extract_entities_from_json(self, json_str: str) -> List[Dict[str, Any]]:
        """从JSON字符串中提取实体"""
        try:
            data = json.loads(json_str)
            return data.get("entities", [])
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试正则表达式提取
            return self._extract_entities_with_regex(json_str)

    def _extract_entities_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """使用正则表达式提取实体（备用方法）"""
        entities = []

        # 匹配实体模式
        patterns = [
            r'"text":\s*"([^"]+)".*?"label":\s*"(Bacteria|Disease|Evidence)"',
            r'"label":\s*"(Bacteria|Disease|Evidence)".*?"text":\s*"([^"]+)"'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) == 2:
                    if match[1] in self.entity_types:
                        entities.append({"text": match[0], "label": match[1]})
                    else:
                        entities.append({"text": match[1], "label": match[0]})

        return entities

    def normalize_entity(self, entity: Dict[str, Any]) -> Tuple[str, str]:
        """标准化实体（文本清理和标签统一）"""
        text = entity["text"].strip().lower()
        label = entity["label"]

        # 移除标点符号
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return (text, label)

    def evaluate_entities(
        self,
        predictions: List[str],
        ground_truths: List[str]
    ) -> Dict[str, Any]:
        """评估实体抽取性能"""

        all_pred_entities = []
        all_true_entities = []

        for pred_str, true_str in zip(predictions, ground_truths):
            # 提取预测实体
            pred_entities = self.extract_entities_from_json(pred_str)
            true_entities = self.extract_entities_from_json(true_str)

            # 标准化实体
            pred_normalized = [self.normalize_entity(e) for e in pred_entities]
            true_normalized = [self.normalize_entity(e) for e in true_entities]

            all_pred_entities.extend(pred_normalized)
            all_true_entities.extend(true_normalized)

        # 计算整体指标
        pred_set = set(all_pred_entities)
        true_set = set(all_true_entities)

        tp = len(pred_set & true_set)
        fp = len(pred_set - true_set)
        fn = len(true_set - pred_set)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        # 按实体类型计算指标
        type_metrics = {}
        for entity_type in self.entity_types:
            pred_type = set([e for e in all_pred_entities if e[1] == entity_type])
            true_type = set([e for e in all_true_entities if e[1] == entity_type])

            tp_type = len(pred_type & true_type)
            fp_type = len(pred_type - true_type)
            fn_type = len(true_type - pred_type)

            prec_type = tp_type / (tp_type + fp_type) if (tp_type + fp_type) > 0 else 0
            rec_type = tp_type / (tp_type + fn_type) if (tp_type + fn_type) > 0 else 0
            f1_type = 2 * prec_type * rec_type / (prec_type + rec_type) if (prec_type + rec_type) > 0 else 0

            type_metrics[entity_type] = {
                "precision": prec_type,
                "recall": rec_type,
                "f1": f1_type,
                "support": len(true_type)
            }

        return {
            "overall": {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": len(true_set)
            },
            "by_type": type_metrics,
            "confusion_matrix": {
                "tp": tp,
                "fp": fp,
                "fn": fn
            }
        }

class RelationEvaluator:
    """关系抽取评估器"""

    def __init__(self):
        self.relation_types = {"is_a", "biomarker_for", "correlated_with", "has_relationship"}

    def extract_relations_from_json(self, json_str: str) -> List[Dict[str, Any]]:
        """从JSON字符串中提取关系"""
        try:
            data = json.loads(json_str)
            return data.get("relations", [])
        except json.JSONDecodeError:
            return self._extract_relations_with_regex(json_str)

    def _extract_relations_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """使用正则表达式提取关系"""
        relations = []

        # 匹配关系模式
        pattern = r'"subject":\s*"([^"]+)".*?"relation":\s*"([^"]+)".*?"object":\s*"([^"]+)"'
        matches = re.findall(pattern, text, re.DOTALL)

        for match in matches:
            relations.append({
                "subject": match[0],
                "relation": match[1],
                "object": match[2]
            })

        return relations

    def normalize_relation(self, relation: Dict[str, Any]) -> Tuple[str, str, str]:
        """标准化关系"""
        subject = relation["subject"].strip().lower()
        relation_type = relation["relation"].strip()
        object_text = relation["object"].strip().lower()

        # 清理文本
        subject = re.sub(r'[^\w\s-]', '', subject).strip()
        object_text = re.sub(r'[^\w\s-]', '', object_text).strip()

        return (subject, relation_type, object_text)

    def evaluate_relations(
        self,
        predictions: List[str],
        ground_truths: List[str]
    ) -> Dict[str, Any]:
        """评估关系抽取性能"""

        all_pred_relations = []
        all_true_relations = []

        for pred_str, true_str in zip(predictions, ground_truths):
            pred_relations = self.extract_relations_from_json(pred_str)
            true_relations = self.extract_relations_from_json(true_str)

            pred_normalized = [self.normalize_relation(r) for r in pred_relations]
            true_normalized = [self.normalize_relation(r) for r in true_relations]

            all_pred_relations.extend(pred_normalized)
            all_true_relations.extend(true_normalized)

        # 计算整体指标
        pred_set = set(all_pred_relations)
        true_set = set(all_true_relations)

        tp = len(pred_set & true_set)
        fp = len(pred_set - true_set)
        fn = len(true_set - pred_set)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        # 按关系类型计算指标
        type_metrics = {}
        for rel_type in self.relation_types:
            pred_type = set([r for r in all_pred_relations if r[1] == rel_type])
            true_type = set([r for r in all_true_relations if r[1] == rel_type])

            tp_type = len(pred_type & true_type)
            fp_type = len(pred_type - true_type)
            fn_type = len(true_type - pred_type)

            prec_type = tp_type / (tp_type + fp_type) if (tp_type + fp_type) > 0 else 0
            rec_type = tp_type / (tp_type + fn_type) if (tp_type + fn_type) > 0 else 0
            f1_type = 2 * prec_type * rec_type / (prec_type + rec_type) if (prec_type + rec_type) > 0 else 0

            type_metrics[rel_type] = {
                "precision": prec_type,
                "recall": rec_type,
                "f1": f1_type,
                "support": len(true_type)
            }

        return {
            "overall": {
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "support": len(true_set)
            },
            "by_type": type_metrics,
            "confusion_matrix": {
                "tp": tp,
                "fp": fp,
                "fn": fn
            }
        }

class MedicalNERREEvaluator:
    """医学NER+RE联合评估器"""

    def __init__(self):
        self.entity_evaluator = EntityEvaluator()
        self.relation_evaluator = RelationEvaluator()

    def evaluate_full_pipeline(
        self,
        predictions: List[str],
        ground_truths: List[str]
    ) -> Dict[str, Any]:
        """评估完整的NER+RE流水线"""

        # 分别评估实体和关系
        entity_results = self.entity_evaluator.evaluate_entities(predictions, ground_truths)
        relation_results = self.relation_evaluator.evaluate_relations(predictions, ground_truths)

        # 计算综合指标
        entity_f1 = entity_results["overall"]["f1"]
        relation_f1 = relation_results["overall"]["f1"]

        # 加权平均F1（可以根据任务重要性调整权重）
        weighted_f1 = 0.6 * entity_f1 + 0.4 * relation_f1

        return {
            "entities": entity_results,
            "relations": relation_results,
            "overall": {
                "entity_f1": entity_f1,
                "relation_f1": relation_f1,
                "weighted_f1": weighted_f1
            }
        }

    def generate_report(self, results: Dict[str, Any]) -> str:
        """生成评估报告"""
        report = []
        report.append("=" * 60)
        report.append("医学实体关系抽取评估报告")
        report.append("=" * 60)

        # 整体指标
        overall = results["overall"]
        report.append(f"\n整体性能:")
        report.append(f"  实体抽取F1: {overall['entity_f1']:.4f}")
        report.append(f"  关系抽取F1: {overall['relation_f1']:.4f}")
        report.append(f"  加权平均F1: {overall['weighted_f1']:.4f}")

        # 实体抽取详细指标
        entity_results = results["entities"]
        report.append(f"\n实体抽取详细指标:")
        report.append(f"  精确率: {entity_results['overall']['precision']:.4f}")
        report.append(f"  召回率: {entity_results['overall']['recall']:.4f}")
        report.append(f"  F1分数: {entity_results['overall']['f1']:.4f}")

        report.append(f"\n各实体类型指标:")
        for entity_type, metrics in entity_results["by_type"].items():
            report.append(f"  {entity_type}:")
            report.append(f"    精确率: {metrics['precision']:.4f}")
            report.append(f"    召回率: {metrics['recall']:.4f}")
            report.append(f"    F1分数: {metrics['f1']:.4f}")
            report.append(f"    支持数: {metrics['support']}")

        # 关系抽取详细指标
        relation_results = results["relations"]
        report.append(f"\n关系抽取详细指标:")
        report.append(f"  精确率: {relation_results['overall']['precision']:.4f}")
        report.append(f"  召回率: {relation_results['overall']['recall']:.4f}")
        report.append(f"  F1分数: {relation_results['overall']['f1']:.4f}")

        report.append(f"\n各关系类型指标:")
        for rel_type, metrics in relation_results["by_type"].items():
            if metrics['support'] > 0:  # 只显示有数据的关系类型
                report.append(f"  {rel_type}:")
                report.append(f"    精确率: {metrics['precision']:.4f}")
                report.append(f"    召回率: {metrics['recall']:.4f}")
                report.append(f"    F1分数: {metrics['f1']:.4f}")
                report.append(f"    支持数: {metrics['support']}")

        return "\n".join(report)

def evaluate_model_predictions(predictions_file: str, ground_truth_file: str) -> None:
    """评估模型预测结果"""

    # 加载预测结果和真实标签
    with open(predictions_file, 'r', encoding='utf-8') as f:
        predictions = json.load(f)

    with open(ground_truth_file, 'r', encoding='utf-8') as f:
        ground_truths = json.load(f)

    # 提取预测文本和真实标签文本
    pred_texts = [json.dumps(p.get("response", p)) for p in predictions]
    true_texts = [json.dumps({"entities": gt.get("entities", []), "relations": gt.get("relations", [])}) for gt in ground_truths]

    # 创建评估器并评估
    evaluator = MedicalNERREEvaluator()
    results = evaluator.evaluate_full_pipeline(pred_texts, true_texts)

    # 生成并打印报告
    report = evaluator.generate_report(results)
    print(report)

    # 保存详细结果
    with open("evaluation_results.json", 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n详细评估结果已保存到 evaluation_results.json")

def main():
    """主函数示例"""
    # 示例数据
    predictions = [
        '{"entities": [{"text": "hepatitis C virus", "label": "Bacteria"}], "relations": [{"subject": "HCV", "relation": "is_a", "object": "hepatitis C virus"}]}',
        '{"entities": [{"text": "multiple sclerosis", "label": "Disease"}, {"text": "EBV", "label": "Bacteria"}], "relations": []}'
    ]

    ground_truths = [
        '{"entities": [{"text": "hepatitis C virus", "label": "Bacteria"}, {"text": "HCV", "label": "Bacteria"}], "relations": [{"subject": "HCV", "relation": "is_a", "object": "hepatitis C virus"}]}',
        '{"entities": [{"text": "multiple sclerosis", "label": "Disease"}, {"text": "Epstein-Barr virus", "label": "Bacteria"}], "relations": [{"subject": "Epstein-Barr virus", "relation": "biomarker_for", "object": "multiple sclerosis"}]}'
    ]

    evaluator = MedicalNERREEvaluator()
    results = evaluator.evaluate_full_pipeline(predictions, ground_truths)

    report = evaluator.generate_report(results)
    print(report)

if __name__ == "__main__":
    main()
