import pytest
from datasets import Dataset, DatasetDict
from wujing.utils.deduplicate import deduplicate


class TestDeduplicate:
    """去重功能测试类"""

    def test_basic_deduplicate_dataset(self):
        """测试基础去重功能"""
        # 创建测试数据
        data = [
            {"id": 1, "text": "hello"},
            {"id": 2, "text": "world"},
            {"id": 3, "text": "hello"},  # 重复
            {"id": 4, "text": "python"},
        ]
        dataset = Dataset.from_list(data)
        
        # 执行去重
        result = deduplicate(dataset, "text")
        
        # 验证结果
        assert len(result) == 3
        texts = [item["text"] for item in result]
        assert "hello" in texts
        assert "world" in texts
        assert "python" in texts
        assert texts.count("hello") == 1

    def test_deduplicate_with_nested_path(self):
        """测试使用嵌套路径进行去重"""
        # 创建测试数据（模拟messages格式）
        data = [
            {"id": 1, "messages": [{"role": "user", "content": "question1"}, {"role": "assistant", "content": "answer1"}]},
            {"id": 2, "messages": [{"role": "user", "content": "question2"}, {"role": "assistant", "content": "answer2"}]},
            {"id": 3, "messages": [{"role": "user", "content": "question1"}, {"role": "assistant", "content": "answer3"}]},  # 重复的问题
            {"id": 4, "messages": [{"role": "user", "content": "question3"}, {"role": "assistant", "content": "answer4"}]},
        ]
        dataset = Dataset.from_list(data)
        
        # 按照用户问题（第一个消息的内容）去重
        result = deduplicate(dataset, "messages.[0].content")
        
        # 验证结果
        assert len(result) == 3
        questions = [item["messages"][0]["content"] for item in result]
        assert "question1" in questions
        assert "question2" in questions
        assert "question3" in questions
        assert questions.count("question1") == 1

    def test_deduplicate_with_negative_index(self):
        """测试使用负索引的路径"""
        # 创建测试数据
        data = [
            {"id": 1, "messages": [{"role": "user", "content": "q1"}, {"role": "assistant", "content": "a1"}]},
            {"id": 2, "messages": [{"role": "user", "content": "q2"}, {"role": "assistant", "content": "a2"}]},
            {"id": 3, "messages": [{"role": "user", "content": "q3"}, {"role": "assistant", "content": "a1"}]},  # 重复的回答
        ]
        dataset = Dataset.from_list(data)
        
        # 按照助手回答（最后一个消息的内容）去重
        result = deduplicate(dataset, "messages.[-1].content")
        
        # 验证结果
        assert len(result) == 2
        answers = [item["messages"][-1]["content"] for item in result]
        assert "a1" in answers
        assert "a2" in answers
        assert answers.count("a1") == 1

    def test_deduplicate_complex_data(self):
        """测试复杂数据结构去重"""
        # 创建包含复杂数据结构的测试数据
        data = [
            {"id": 1, "metadata": {"tags": ["python", "ml"], "config": {"version": 1}}},
            {"id": 2, "metadata": {"tags": ["java", "web"], "config": {"version": 2}}},
            {"id": 3, "metadata": {"tags": ["python", "ml"], "config": {"version": 1}}},  # 完全重复的metadata
            {"id": 4, "metadata": {"tags": ["python", "ml"], "config": {"version": 2}}},  # tags相同但config不同
        ]
        dataset = Dataset.from_list(data)
        
        # 按照tags去重
        result = deduplicate(dataset, "metadata.tags")
        
        # 验证结果
        assert len(result) == 2  # 只保留python,ml和java,web两种tags
        tags_list = [item["metadata"]["tags"] for item in result]
        assert ["python", "ml"] in tags_list
        assert ["java", "web"] in tags_list

    def test_deduplicate_with_none_values(self):
        """测试包含None值的去重"""
        data = [
            {"id": 1, "value": None},
            {"id": 2, "value": "test"},
            {"id": 3, "value": None},  # 重复的None
            {"id": 4, "value": "test2"},
        ]
        dataset = Dataset.from_list(data)
        
        result = deduplicate(dataset, "value")
        
        # 验证结果
        assert len(result) == 3
        values = [item["value"] for item in result]
        assert None in values
        assert "test" in values
        assert "test2" in values
        assert values.count(None) == 1

    def test_deduplicate_dataset_dict(self):
        """测试DatasetDict去重"""
        # 创建测试数据
        train_data = [
            {"text": "hello"},
            {"text": "world"},
            {"text": "hello"},  # 重复
        ]
        test_data = [
            {"text": "python"},
            {"text": "code"},
            {"text": "python"},  # 重复
        ]
        
        dataset_dict = DatasetDict({
            "train": Dataset.from_list(train_data),
            "test": Dataset.from_list(test_data)
        })
        
        # 执行去重
        result = deduplicate(dataset_dict, "text")
        
        # 验证结果
        assert isinstance(result, DatasetDict)
        assert len(result["train"]) == 2
        assert len(result["test"]) == 2

    def test_deduplicate_invalid_key_path(self):
        """测试无效的key_path"""
        data = [
            {"id": 1, "text": "hello"},
            {"id": 2, "text": "world"},
        ]
        dataset = Dataset.from_list(data)
        
        # 使用不存在的key_path应该抛出异常
        with pytest.raises(ValueError, match="无法从数据中提取键路径 'nonexistent' 的值"):
            deduplicate(dataset, "nonexistent")

    def test_deduplicate_invalid_nested_path(self):
        """测试无效的嵌套路径"""
        data = [
            {"id": 1, "messages": [{"role": "user"}]},
            {"id": 2, "messages": [{"role": "assistant"}]},
        ]
        dataset = Dataset.from_list(data)
        
        # 使用不存在的嵌套路径应该抛出异常
        with pytest.raises(ValueError, match="无法从数据中提取键路径 'messages.\\[0\\].nonexistent' 的值"):
            deduplicate(dataset, "messages.[0].nonexistent")

    def test_deduplicate_invalid_index_out_of_range(self):
        """测试索引超出范围的情况"""
        data = [
            {"id": 1, "messages": [{"role": "user"}]},
            {"id": 2, "messages": [{"role": "assistant"}]},
        ]
        dataset = Dataset.from_list(data)
        
        # 使用超出范围的索引应该抛出异常
        with pytest.raises(ValueError, match="无法从数据中提取键路径 'messages.\\[5\\].role' 的值"):
            deduplicate(dataset, "messages.[5].role")

    def test_deduplicate_invalid_type_mismatch(self):
        """测试类型不匹配的情况"""
        data = [
            {"id": 1, "value": "not_a_list"},
            {"id": 2, "value": "also_not_a_list"},
        ]
        dataset = Dataset.from_list(data)
        
        # 尝试对字符串使用数组索引应该抛出异常
        with pytest.raises(ValueError, match="无法从数据中提取键路径 'value.\\[0\\]' 的值"):
            deduplicate(dataset, "value.[0]")

    def test_deduplicate_invalid_data_type(self):
        """测试无效的数据类型"""
        from pydantic_core import ValidationError
        
        # 传入既不是Dataset也不是DatasetDict的对象
        with pytest.raises(ValidationError):
            deduplicate([], "text")

    def test_deduplicate_list_values(self):
        """测试列表值的去重"""
        data = [
            {"id": 1, "tags": ["python", "ml"]},
            {"id": 2, "tags": ["java", "web"]},
            {"id": 3, "tags": ["python", "ml"]},  # 重复的列表
            {"id": 4, "tags": ["ml", "python"]},  # 相同元素但顺序不同，应该被视为不同
        ]
        dataset = Dataset.from_list(data)
        
        result = deduplicate(dataset, "tags")
        
        # 验证结果：应该保留3条（因为顺序不同被视为不同）
        assert len(result) == 3

    def test_empty_dataset(self):
        """测试空数据集"""
        dataset = Dataset.from_list([])
        result = deduplicate(dataset, "text")
        assert len(result) == 0

    def test_single_item_dataset(self):
        """测试单条数据的数据集"""
        data = [{"id": 1, "text": "hello"}]
        dataset = Dataset.from_list(data)
        result = deduplicate(dataset, "text")
        assert len(result) == 1
        assert result[0]["text"] == "hello"

    def test_deduplicate_with_mixed_types(self):
        """测试混合类型值的去重"""
        # 将所有值转为字符串，避免PyArrow的混合类型问题
        data = [
            {"id": 1, "value": "string"},
            {"id": 2, "value": "42"},
            {"id": 3, "value": "string"},  # 重复的字符串
            {"id": 4, "value": "42.0"},  # 数字字符串，但值不同
            {"id": 5, "value": "True"},
        ]
        dataset = Dataset.from_list(data)
        
        result = deduplicate(dataset, "value")
        
        # 验证结果
        assert len(result) == 4  # string重复被去掉
        values = [item["value"] for item in result]
        assert "string" in values
        assert "42" in values
        assert "42.0" in values
        assert "True" in values

    def test_performance_with_large_dataset(self):
        """测试大数据集的性能（简单验证）"""
        # 创建较大的测试数据集
        data = [{"id": i, "text": f"text_{i % 100}"} for i in range(1000)]
        dataset = Dataset.from_list(data)
        
        result = deduplicate(dataset, "text")
        
        # 验证结果：应该只保留100条不同的text
        assert len(result) == 100
