import json
from decimal import Decimal, ROUND_HALF_UP
from collections import defaultdict, Counter
from typing import Union, List, Dict, Any, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from iterstrat.ml_stratifiers import MultilabelStratifiedKFold
from datasets import Dataset, DatasetDict, load_dataset
from itertools import chain
from typing import Optional, Union, Dict, Any


def is_multilabel(df: pd.DataFrame, column: str) -> bool:
    """
    判断是否为多标签数据

    Args:
        df: 输入数据框
        column: 标签列名

    Returns:
        bool: 是否为多标签数据
    """
    try:
        if not len(df):
            return False
        first_valid_value = df[column].dropna().iloc[0]
        return isinstance(first_valid_value, (list, np.ndarray))
    except (KeyError, IndexError):
        return False


def get_label_matrix(labels: List, unique_labels: List) -> np.ndarray:
    """
    将标签列表转换为二值矩阵

    Args:
        labels: 标签列表
        unique_labels: 唯一标签列表

    Returns:
        np.ndarray: 二值矩阵
    """
    matrix = np.zeros(len(unique_labels))
    label_to_index = {label: idx for idx, label in enumerate(unique_labels)}
    for label in labels:
        if label in label_to_index:
            matrix[label_to_index[label]] = 1
    return matrix


def split_dataset(dataset: Union[Dataset, pd.DataFrame], test_size: float = 0.2, stratify: str = None) -> DatasetDict:
    """
    Split the given dataset into train and test sets.
    Support both single-label and multi-label stratification.

    Args:
        dataset: 输入数据集
        test_size: 测试集比例
        stratify: 分层抽样的列名

    Returns:
        DatasetDict: 包含训练集和测试集的数据集字典

    Raises:
        ValueError: 当输入参数无效时抛出
    """
    try:
        # 输入验证
        if not 0 < test_size < 1:
            raise ValueError("test_size must be between 0 and 1")

        # 转换为DataFrame
        if isinstance(dataset, Dataset):
            df = pd.DataFrame(dataset)
        elif isinstance(dataset, pd.DataFrame):
            df = dataset.copy()
        else:
            raise ValueError("dataset must be either a Dataset or DataFrame")

        # 检查是否存在分层列
        if stratify and stratify not in df.columns:
            raise ValueError(f"Column {stratify} not found in dataset")

        if stratify is None:
            train_df, val_df = train_test_split(df, test_size=test_size, random_state=42)
        else:
            if is_multilabel(df, stratify):
                # 处理空值
                df = df.dropna(subset=[stratify])

                # 获取所有唯一的标签
                unique_labels = list(
                    set(
                        [label for labels in df[stratify] if isinstance(labels, (list, np.ndarray)) for label in labels]
                    )
                )

                # 将标签列表转换为二值矩阵
                label_matrix = np.array([get_label_matrix(labels, unique_labels) for labels in df[stratify]])

                # 使用MultilabelStratifiedKFold进行划分
                mskf = MultilabelStratifiedKFold(n_splits=int(1 / test_size), shuffle=True, random_state=42)

                # 获取划分的索引
                try:
                    train_idx, test_idx = next(mskf.split(df, label_matrix))
                except StopIteration:
                    raise ValueError("Failed to split dataset with given parameters")

                # 使用索引划分数据
                train_df = df.iloc[train_idx]
                val_df = df.iloc[test_idx]

            else:
                train_df, val_df = train_test_split(df, test_size=test_size, stratify=df[stratify], random_state=42)

        # 重置索引并删除索引列
        train_df = train_df.reset_index(drop=True)
        val_df = val_df.reset_index(drop=True)

        # 转换为字典格式，避免产生额外的索引列
        train_dict = {col: train_df[col].tolist() for col in train_df.columns}
        val_dict = {col: val_df[col].tolist() for col in val_df.columns}

        # 创建Dataset
        train_dataset = Dataset.from_dict(train_dict)
        val_dataset = Dataset.from_dict(val_dict)

        # 构建DatasetDict
        train_val_dataset = DatasetDict(
            {
                "train": train_dataset,
                "test": val_dataset,
            }
        )

        return train_val_dataset

    except Exception as e:
        raise ValueError(f"Error splitting dataset: {str(e)}")


def analyze_label_distribution(
    dataset: Dataset,
    label_column: str,
    top_k: Optional[int] = None,
    min_freq: Optional[Union[int, float]] = None,
) -> Dict[str, Any]:
    """
    分析数据集中标签的分布情况，支持单标签和多标签情况

    Args:
        dataset: Huggingface Dataset 对象
        label_column: 标签列的名称
        top_k: 只返回前k个最常见的标签
        min_freq: 最小频率阈值，低于该阈值的标签将被过滤

    Returns:
        Dict[str, Any]: 包含标签分布信息和统计摘要的字典

    Raises:
        TypeError: 当输入参数类型错误时
        ValueError: 当输入参数无效时
    """
    # 输入验证
    if not isinstance(dataset, Dataset):
        raise TypeError("Dataset must be a Huggingface Dataset")

    if not isinstance(label_column, str):
        raise TypeError("label_column must be a string")

    if top_k is not None and (not isinstance(top_k, int) or top_k <= 0):
        raise ValueError("top_k must be a positive integer")

    if min_freq is not None and (not isinstance(min_freq, (int, float)) or min_freq < 0):
        raise ValueError("min_freq must be a non-negative number")

    if not dataset:
        raise ValueError("Dataset is empty")

    if label_column not in dataset.features:
        raise ValueError(f"Label column '{label_column}' not found in dataset")

    try:
        label_data = dataset[label_column]
        first_label = label_data[0]
    except Exception as e:
        raise ValueError(f"Error accessing dataset: {str(e)}")

    is_multi_label = isinstance(first_label, (list, tuple, set))
    total_samples = len(dataset)

    # 批量统计标签分布
    if is_multi_label:
        # 总出现次数统计
        total_counts = Counter(chain.from_iterable(label_data))
        # 样本数统计（每个标签在每个样本中只计一次）
        sample_counts = Counter()
        for sublist in label_data:
            sample_counts.update(set(sublist))
    else:
        total_counts = Counter(label_data)
        sample_counts = total_counts.copy()

    # 应用频率过滤
    if min_freq is not None:
        total_counts = {k: v for k, v in total_counts.items() if v >= min_freq}
        if not total_counts:
            raise ValueError(f"No labels remain after applying min_freq={min_freq}")
        sample_counts = {k: sample_counts[k] for k in total_counts}

    # 准备排序后的标签列表
    sorted_labels = sorted(total_counts.keys(), key=lambda x: (-total_counts[x], x))

    # 应用top_k过滤
    if top_k is not None:
        sorted_labels = sorted_labels[:top_k]

    # 格式化百分比
    def format_percentage(value: float) -> str:
        return f"{Decimal(value).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}%"

    # 构建分布结果
    label_dist = {}
    for label in sorted_labels:
        count = total_counts[label]
        percentage = count / total_samples * 100
        label_dist[label] = {
            "count": count,
            "percentage": format_percentage(percentage),
            "samples_count": sample_counts[label],
        }

    # 计算统计摘要
    total_label_occurrences = sum(total_counts.values())

    # 标签长度统计（仅多标签需要）
    if is_multi_label:
        label_lengths = [len(sublist) for sublist in label_data]
    else:
        label_lengths = [1] * total_samples

    # 计算分布统计
    percentages = [total_counts[k] / total_samples * 100 for k in sorted_labels]
    max_percent = max(percentages) if percentages else 0
    min_percent = min(percentages) if percentages else 0
    imbalance_ratio = max_percent / min_percent if min_percent != 0 else float("inf")

    # 构建摘要信息
    summary = {
        "basic_stats": {
            "total_samples": total_samples,
            "unique_labels": len(label_dist),
            "avg_labels_per_sample": round(total_label_occurrences / total_samples, 2),
            "is_multi_label": is_multi_label,
            "total_label_occurrences": total_label_occurrences,
        },
        "label_frequency": {
            "most_frequent": [{"label": k, "count": label_dist[k]["count"]} for k in list(sorted_labels)[:5]],
            "least_frequent": (
                [{"label": k, "count": label_dist[k]["count"]} for k in list(sorted_labels)[-5:]]
                if len(sorted_labels) >= 5
                else []
            ),
        },
        "distribution_stats": {
            "max_percentage": format_percentage(max_percent),
            "min_percentage": format_percentage(min_percent),
            "imbalance_ratio": f"{imbalance_ratio:.2f}",
        },
    }

    # 多标签特有统计
    if is_multi_label:
        sorted_lengths = sorted(label_lengths)
        summary["multi_label_stats"] = {
            "max_labels_per_sample": max(label_lengths),
            "min_labels_per_sample": min(label_lengths),
            "median_labels_per_sample": sorted_lengths[len(sorted_lengths) // 2],
            "samples_with_multiple_labels": sum(1 for x in label_lengths if x > 1),
            "samples_with_single_label": sum(1 for x in label_lengths if x == 1),
            "samples_with_no_labels": sum(1 for x in label_lengths if x == 0),
        }

    return {"distribution": label_dist, "summary": summary}


if __name__ == "__main__":
    # 测试单标签数据
    data = load_dataset("json", data_files="./../../../testdata/data.jsonl", split="train")
    split = split_dataset(data, test_size=0.2, stratify="label")

    print("Single-label split result:", split)
    for split_type in ["train", "test"]:
        print(f"\nLabel distribution in {split_type} set:")
        print(
            json.dumps(
                analyze_label_distribution(split[split_type], "label"),
                indent=4,
                ensure_ascii=False,
            )
        )

    # 测试多标签数据
    multi_data = load_dataset("json", data_files="./../../../testdata/multilabel_data.jsonl", split="train")
    split = split_dataset(multi_data, test_size=0.2, stratify="labels")

    print("\nMulti-label split result:", split)
    for split_type in ["train", "test"]:
        print(f"\nMulti-label distribution in {split_type} set:")
        print(
            json.dumps(
                analyze_label_distribution(split[split_type], "labels"),
                indent=4,
                ensure_ascii=False,
            )
        )
