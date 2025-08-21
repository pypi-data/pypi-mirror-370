from datasets import Dataset, DatasetDict
from pydantic import validate_call
import json
from typing import Any


def __parse_key_path(key_path: str) -> list[str | int]:
    """
    解析键路径为访问步骤列表

    Args:
        key_path: 键路径，如 "text" 或 "messages.[0].content" 或 "messages.[-1].role"

    Returns:
        解析后的访问步骤列表

    Examples:
        __parse_key_path("text") -> ["text"]
        __parse_key_path("messages.[0].content") -> ["messages", 0, "content"]
        __parse_key_path("messages.[-1].role") -> ["messages", -1, "role"]
    """
    parts = key_path.split(".")
    steps = []

    for part in parts:
        if part.startswith("[") and part.endswith("]"):
            # 处理数组索引，支持负数索引
            index_str = part[1:-1]
            try:
                index = int(index_str)
                steps.append(index)
            except ValueError:
                raise ValueError(f"无效的数组索引: {part}")
        else:
            steps.append(part)

    return steps


def __extract_value_by_path(data: dict, steps: list[str | int]) -> Any:
    """
    根据解析后的步骤从数据中提取值

    Args:
        data: 数据字典
        steps: 访问步骤列表

    Returns:
        提取的值

    Raises:
        KeyError: 当键不存在时
        IndexError: 当索引超出范围时
        TypeError: 当类型不匹配时
    """
    value = data

    for step in steps:
        if isinstance(step, str):
            if not isinstance(value, dict):
                raise TypeError(f"期望字典类型，但得到 {type(value)}")
            if step not in value:
                raise KeyError(f"键 '{step}' 不存在")
            value = value[step]
        elif isinstance(step, int):
            if not isinstance(value, (list, tuple)):
                raise TypeError(f"期望列表或元组类型，但得到 {type(value)}")
            try:
                value = value[step]
            except IndexError:
                raise IndexError(f"索引 {step} 超出范围，列表长度为 {len(value)}")

    return value


def __create_hash_key(value: Any) -> str:
    """
    为任意值创建稳定的哈希键

    Args:
        value: 需要哈希的值

    Returns:
        哈希键字符串
    """
    if isinstance(value, (str, int, float, bool, type(None))):
        return str(value)
    elif isinstance(value, (list, tuple)):
        # 对于列表和元组，递归处理每个元素
        return json.dumps([__create_hash_key(item) for item in value], sort_keys=True, ensure_ascii=False)
    elif isinstance(value, dict):
        # 对于字典，按键排序后序列化
        return json.dumps(
            {k: __create_hash_key(v) for k, v in sorted(value.items())}, sort_keys=True, ensure_ascii=False
        )
    else:
        # 对于其他类型，尝试转换为字符串
        try:
            return str(value)
        except Exception:
            # 如果无法转换，使用对象的 repr
            return repr(value)


@validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
def __deduplicate_single(dataset: Dataset, key_path: str, split_name: str | None = None) -> Dataset:
    """
    对单个数据集进行去重

    Args:
        dataset: 需要去重的数据集
        key_path: 用于去重的键路径
        split_name: 数据集分割名称，用于显示进度信息

    Returns:
        去重后的数据集
    """
    seen = set()
    # 预先解析路径，避免重复解析
    steps = __parse_key_path(key_path)

    def _filter(example: dict) -> bool:
        try:
            value = __extract_value_by_path(example, steps)
            hash_key = __create_hash_key(value)

            if hash_key not in seen:
                seen.add(hash_key)
                return True
            return False
        except (KeyError, IndexError, TypeError) as e:
            raise ValueError(f"无法从数据中提取键路径 '{key_path}' 的值: {e}") from e

    desc = f"去重中[{split_name}]" if split_name else "去重中"
    return dataset.filter(_filter, desc=desc)


@validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
def deduplicate(data: Dataset | DatasetDict, key_path: str) -> Dataset | DatasetDict:
    """
    对数据集进行去重

    Args:
        data: 需要去重的数据，可以是Dataset或DatasetDict
        key_path: 用于去重的键路径，支持嵌套结构和数组索引
                 如 "text" 或 "messages.[0].content" 或 "messages.[-1].role"

    Returns:
        去重后的数据集

    Examples:
        # 基础去重
        deduplicate(dataset, "text")

        # 嵌套结构去重（访问第一个消息的内容）
        deduplicate(dataset, "messages.[0].content")

        # 访问最后一个消息的角色
        deduplicate(dataset, "messages.[-1].role")

        # 访问倒数第二个消息的内容
        deduplicate(dataset, "messages.[-2].content")

    Raises:
        ValueError: 当data类型不正确或key_path格式无效时
    """
    if isinstance(data, DatasetDict):
        result = {}
        for split_name, split_data in data.items():
            result[split_name] = __deduplicate_single(split_data, key_path, split_name)
        return DatasetDict(result)
    elif isinstance(data, Dataset):
        return __deduplicate_single(data, key_path)
    else:
        raise ValueError("data 必须是 Dataset 或 DatasetDict 类型")
