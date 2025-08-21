import json
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
    jaccard_score,
)
import numpy as np
from typing import Dict, Union, List, Optional, Mapping
from sklearn.metrics import precision_recall_fscore_support


def calculate_classification_metrics(
    data: Dict[str, List[Union[int, str]]],
    id2label: Optional[Mapping[Union[int, str], str]] = None,
) -> Dict[str, Union[Dict[str, float], List[Dict[str, Union[str, float]]]]]:
    """
    优化后的分类指标计算函数，通过以下改进提升效率：
    1. 使用单一函数调用获取所有基础指标
    2. 手动计算宏观和加权平均值
    3. 修正类别处理逻辑错误
    4. 优化数据结构生成过程
    """

    # 输入验证保持不变
    if not isinstance(data, dict):
        raise TypeError("输入必须是字典类型")

    required_keys = {"label", "predict"}
    if not required_keys.issubset(data.keys()):
        raise KeyError(f"输入字典必须包含以下键: {required_keys}")

    true_labels = np.array(data["label"])
    pred_labels = np.array(data["predict"])

    if len(true_labels) != len(pred_labels):
        raise ValueError("真实标签和预测标签长度不一致")

    if len(true_labels) == 0:
        raise ValueError("输入数据不能为空")

    # 修正后的标签有效性检查
    all_labels = np.concatenate([true_labels, pred_labels])
    if not all_labels.size:
        raise ValueError("检测到无效的标签值")

    # 获取所有唯一标签并按序排列
    labels = np.unique(all_labels)

    # 一次性获取所有基础指标
    precision, recall, f1, support = precision_recall_fscore_support(
        true_labels, pred_labels, labels=labels, average=None, zero_division=0
    )  # 显式指定所有需要处理的标签

    # 计算宏观平均
    macro_precision = np.mean(precision)
    macro_recall = np.mean(recall)
    macro_f1 = np.mean(f1)

    # 计算加权平均
    total_samples = np.sum(support)
    weighted_precision = np.sum(precision * support) / total_samples
    weighted_recall = np.sum(recall * support) / total_samples
    weighted_f1 = np.sum(f1 * support) / total_samples

    # 生成分类指标（提前构建显示名称映射）
    label_names = {}
    for label in labels:
        if id2label and (label in id2label):
            label_names[label] = str(id2label[label])
        else:
            label_names[label] = str(label)

    # 使用列表推导式优化结果生成
    class_metrics = [
        {
            "label_id": str(label),
            "label_name": label_names[label],
            "precision": float(precision[i]),
            "recall": float(recall[i]),
            "f1": float(f1[i]),
        }
        for i, label in enumerate(labels)
    ]

    # 按precision降序排序（使用稳定排序）
    class_metrics.sort(key=lambda x: (-x["precision"], x["label_id"]))

    return {
        "explanation": [
            "Precision(精确率): 在所有预测为该类的样本中，真实为该类的比例",
            "Recall(召回率): 在所有真实为该类的样本中，被正确预测的比例",
            "F1 Score: 精确率和召回率的调和平均数，综合评估指标",
            "Macro Average: 所有类别的平均值，每个类别权重相同",
            "Weighted Average: 考虑每个类别样本数量的加权平均值",
        ],
        "overall": {
            "macro_precision": float(macro_precision),
            "macro_recall": float(macro_recall),
            "macro_f1": float(macro_f1),
            "weighted_precision": float(weighted_precision),
            "weighted_recall": float(weighted_recall),
            "weighted_f1": float(weighted_f1),
        },
        "classes": class_metrics,
    }


def calculate_multilabel_metrics(
    data: Dict[str, List[List[Union[int, float]]]],
    id2label: Optional[Dict[int, str]] = None,
) -> Dict[str, Union[Dict[str, float], List[Dict[str, Union[str, float]]]]]:
    """
    计算多标签分类模型的评估指标并返回结构化数据

    Args:
        data: 包含'label'和'predict'键的字典，值为二维列表，每个样本的标签为二进制列表
        id2label: 可选的标签ID到文本的映射字典，使结果更易读

    Returns:
        包含以下结构的字典:
        {
            "explanation": Dict[str, List[str]],      # 各维度指标说明
            "overall": Dict[str, float],              # 宏观指标
            "classes": List[Dict[str, Union[str, float]]],  # 分类维度指标（按precision降序）
            "samples": Dict[str, float],              # 样本维度指标
            "labels": Dict[str, Dict[str, int]]       # 标签维度统计
        }

    Raises:
        TypeError: 输入数据类型错误
        KeyError: 输入字典缺少必要键
        ValueError: 数据验证失败
    """
    # 输入验证
    if not isinstance(data, dict):
        raise TypeError("输入必须是字典类型")

    required_keys = {"label", "predict"}
    if not required_keys.issubset(data.keys()):
        raise KeyError(f"输入字典必须包含以下键: {required_keys}")

    true_labels = np.array(data["label"])
    pred_labels = np.array(data["predict"])

    if true_labels.ndim != 2 or pred_labels.ndim != 2:
        raise ValueError("标签和预测必须是二维数组（多标签格式）")

    if true_labels.shape != pred_labels.shape:
        raise ValueError("真实标签和预测标签的形状不一致")

    if len(true_labels) == 0:
        raise ValueError("输入数据不能为空")

    if not (np.isin(true_labels, [0, 1]).all() and np.isin(pred_labels, [0, 1]).all()):
        raise ValueError("标签必须是0或1的二进制值")

    # 验证id2label映射（如果提供）
    n_samples, n_classes = true_labels.shape

    if id2label is not None:
        if not isinstance(id2label, dict):
            raise TypeError("id2label必须是字典类型")

        # 检查id2label是否包含所有标签索引
        expected_keys = set(range(n_classes))
        actual_keys = set(id2label.keys())
        missing_keys = expected_keys - actual_keys

        if missing_keys:
            raise ValueError(f"id2label字典缺少以下标签索引: {missing_keys}")

    # 创建标签索引到显示名称的映射函数
    def get_label_name(idx: int) -> str:
        if id2label is not None:
            return id2label[idx]
        return str(idx)

    # ===== 1. 类别维度指标 =====
    precision_per_class = precision_score(true_labels, pred_labels, average=None, zero_division=0)
    recall_per_class = recall_score(true_labels, pred_labels, average=None, zero_division=0)
    f1_per_class = f1_score(true_labels, pred_labels, average=None, zero_division=0)
    support_per_class = np.sum(true_labels, axis=0)

    # 分类别结果
    class_metrics = [
        {
            "label_id": i,
            "label_name": get_label_name(i),
            "precision": float(precision_per_class[i]),
            "recall": float(recall_per_class[i]),
            "f1": float(f1_per_class[i]),
            "support": int(support_per_class[i]),
        }
        for i in range(n_classes)
    ]

    # 按precision降序排序
    sorted_class_metrics = sorted(class_metrics, key=lambda x: x["precision"], reverse=True)

    # ===== 2. 总体指标 =====
    hamming = hamming_loss(true_labels, pred_labels)
    micro_precision = precision_score(true_labels, pred_labels, average="micro", zero_division=0)
    micro_recall = recall_score(true_labels, pred_labels, average="micro", zero_division=0)
    micro_f1 = f1_score(true_labels, pred_labels, average="micro", zero_division=0)

    macro_precision = precision_score(true_labels, pred_labels, average="macro", zero_division=0)
    macro_recall = recall_score(true_labels, pred_labels, average="macro", zero_division=0)
    macro_f1 = f1_score(true_labels, pred_labels, average="macro", zero_division=0)

    weighted_precision = precision_score(true_labels, pred_labels, average="weighted", zero_division=0)
    weighted_recall = recall_score(true_labels, pred_labels, average="weighted", zero_division=0)
    weighted_f1 = f1_score(true_labels, pred_labels, average="weighted", zero_division=0)

    jaccard_macro = jaccard_score(true_labels, pred_labels, average="macro", zero_division=0)
    jaccard_micro = jaccard_score(true_labels, pred_labels, average="micro", zero_division=0)

    # ===== 3. 样本维度指标 =====
    # 每个样本的真实标签和预测标签数量
    true_labels_per_sample = np.sum(true_labels, axis=1)
    pred_labels_per_sample = np.sum(pred_labels, axis=1)

    # 每个样本的准确预测标签数量
    correct_labels_per_sample = np.sum(true_labels & pred_labels, axis=1)

    # 每个样本的全部预测结果是否完全正确
    exact_match_ratio = np.mean(np.all(true_labels == pred_labels, axis=1))

    # 样本的完全预测率：预测的标签集合完全匹配真实标签集合的样本比例
    exact_match_samples = np.sum(np.all(true_labels == pred_labels, axis=1))

    # 样本级别的精确率、召回率和F1
    sample_precision = np.mean(
        np.divide(
            correct_labels_per_sample,
            pred_labels_per_sample,
            out=np.zeros_like(correct_labels_per_sample, dtype=float),
            where=pred_labels_per_sample > 0,
        )
    )

    sample_recall = np.mean(
        np.divide(
            correct_labels_per_sample,
            true_labels_per_sample,
            out=np.zeros_like(correct_labels_per_sample, dtype=float),
            where=true_labels_per_sample > 0,
        )
    )

    # 计算样本级别的F1，避免除零错误
    sample_f1 = np.zeros_like(correct_labels_per_sample, dtype=float)
    valid_samples = (true_labels_per_sample + pred_labels_per_sample) > 0
    if np.any(valid_samples):
        sample_f1[valid_samples] = (
            2
            * correct_labels_per_sample[valid_samples]
            / (true_labels_per_sample[valid_samples] + pred_labels_per_sample[valid_samples])
        )
    sample_f1_avg = np.mean(sample_f1)

    # ===== 4. 标签维度统计 =====
    # 计算各种标签组合情况
    true_bool = true_labels.astype(bool)
    pred_bool = pred_labels.astype(bool)

    true_positives = np.sum(true_bool & pred_bool, axis=0)
    false_positives = np.sum(~true_bool & pred_bool, axis=0)
    false_negatives = np.sum(true_bool & ~pred_bool, axis=0)
    true_negatives = np.sum(~true_bool & ~pred_bool, axis=0)

    # 标签分布统计
    total_true_labels = np.sum(true_labels)
    total_pred_labels = np.sum(pred_labels)
    avg_labels_per_sample = total_true_labels / n_samples
    label_cardinality = np.mean(true_labels_per_sample)  # 平均每个样本的标签数
    label_density = label_cardinality / n_classes  # 标签密度

    # 计算每个类别的出现频率
    label_frequencies = np.sum(true_labels, axis=0) / n_samples

    # 使用友好的标签名称创建标签统计字典
    label_stats = {
        "true_positives": {get_label_name(i): int(true_positives[i]) for i in range(n_classes)},
        "false_positives": {get_label_name(i): int(false_positives[i]) for i in range(n_classes)},
        "false_negatives": {get_label_name(i): int(false_negatives[i]) for i in range(n_classes)},
        "true_negatives": {get_label_name(i): int(true_negatives[i]) for i in range(n_classes)},
        "frequencies": {get_label_name(i): float(label_frequencies[i]) for i in range(n_classes)},
    }

    # 返回结构化指标
    return {
        "explanation": {
            "overall": [
                "Hamming Loss: 错误预测的标签比例，值越小越好",
                "Micro Precision/Recall/F1: 全局计算所有标签的指标",
                "Macro Precision/Recall/F1: 每个类别的指标的平均值",
                "Weighted Precision/Recall/F1: 按每个类别的样本数加权的指标",
                "Jaccard Similarity: 预测集合与真实集合的交集与并集的比值",
            ],
            "samples": [
                "Exact Match Ratio: 完全正确预测的样本比例",
                "Sample Precision: 每个样本的准确率平均值",
                "Sample Recall: 每个样本的召回率平均值",
                "Sample F1: 每个样本的F1分数平均值",
                "Label Cardinality: 每个样本的平均标签数",
                "Label Density: 标签密度（cardinality/可能标签总数）",
            ],
            "classes": [
                "每个标签类别的单独指标，按precision降序排列",
                "Support: 具有该标签的样本数量",
            ],
            "labels": [
                "TP: 真阳性 - 预测有标签且确实有",
                "FP: 假阳性 - 预测有标签但实际没有",
                "FN: 假阴性 - 预测没有标签但实际有",
                "TN: 真阴性 - 预测没有标签且确实没有",
            ],
        },
        "overall": {
            "hamming_loss": float(hamming),
            "micro_precision": float(micro_precision),
            "micro_recall": float(micro_recall),
            "micro_f1": float(micro_f1),
            "macro_precision": float(macro_precision),
            "macro_recall": float(macro_recall),
            "macro_f1": float(macro_f1),
            "weighted_precision": float(weighted_precision),
            "weighted_recall": float(weighted_recall),
            "weighted_f1": float(weighted_f1),
            "jaccard_macro": float(jaccard_macro),
            "jaccard_micro": float(jaccard_micro),
        },
        "samples": {
            "exact_match_ratio": float(exact_match_ratio),
            "exact_match_count": int(exact_match_samples),
            "sample_precision": float(sample_precision),
            "sample_recall": float(sample_recall),
            "sample_f1": float(sample_f1_avg),
            "label_cardinality": float(label_cardinality),
            "label_density": float(label_density),
            "avg_labels_per_sample": float(avg_labels_per_sample),
            "total_samples": int(n_samples),
            "total_true_labels": int(total_true_labels),
            "total_predicted_labels": int(total_pred_labels),
        },
        "classes": sorted_class_metrics,
        "labels": label_stats,
        "metadata": {
            "has_label_mapping": id2label is not None,
            "num_classes": n_classes,
            "label_mapping": id2label if id2label is not None else None,
        },
    }


# 使用示例
if __name__ == "__main__":
    print(
        json.dumps(
            calculate_classification_metrics(
                data={
                    "label": [0, 1, 0, 1, 2],
                    "predict": [0, 1, 0, 0, 2],
                },
                id2label={0: "豌豆", 1: "茄子", 2: "猪肉"},
            ),
            indent=4,
            ensure_ascii=False,
        )
    )
    print(
        json.dumps(
            calculate_multilabel_metrics(
                data={
                    "label": [[1, 0, 1], [0, 1, 1], [1, 1, 0]],
                    "predict": [[1, 1, 1], [0, 0, 1], [1, 1, 0]],
                },
                id2label={0: "豌豆", 1: "茄子", 2: "猪肉"},
            ),
            indent=4,
            ensure_ascii=False,
        )
    )
