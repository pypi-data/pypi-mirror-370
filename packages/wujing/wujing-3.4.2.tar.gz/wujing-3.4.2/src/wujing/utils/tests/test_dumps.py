import json
from datetime import datetime

import pytest

from wujing.utils.dumps import dumps2json


class CustomClass:
    """测试用的自定义类"""

    def __init__(self, value: str):
        self.value = value


class TestDumps2Json:
    """dumps2json 函数的测试类"""

    def test_dumps_none(self):
        """测试序列化 None 值"""
        result = dumps2json(None)
        assert result == json.dumps(None, indent=4, ensure_ascii=False)

    def test_dumps_simple_dict(self):
        """测试序列化简单字典"""
        test_dict = {"key": "value", "number": 42}
        result = dumps2json(test_dict)
        expected = json.dumps(test_dict, indent=4, ensure_ascii=False)
        assert result == expected

    def test_dumps_nested_dict(self):
        """测试序列化嵌套字典"""
        test_dict = {"nested": {"data": [1, 2, {"deep": "value"}]}}
        result = dumps2json(test_dict)
        expected = json.dumps(test_dict, indent=4, ensure_ascii=False)
        assert result == expected

    def test_dumps_list(self):
        """测试序列化列表"""
        test_list = [1, "string", {"key": "value"}, None]
        result = dumps2json(test_list)
        expected = json.dumps(test_list, indent=4, ensure_ascii=False)
        assert result == expected

    def test_dumps_chinese_characters(self):
        """测试序列化中文字符"""
        test_dict = {"中文": "测试", "english": "test"}
        result = dumps2json(test_dict)
        expected = json.dumps(test_dict, indent=4, ensure_ascii=False)
        assert result == expected
        assert "中文" in result  # 确保中文字符没有被转义

    @pytest.mark.parametrize("indent", [0, 1, 2, 4, 8])
    def test_dumps_with_different_indents(self, indent):
        """测试不同的缩进值"""
        test_dict = {"key": "value"}
        result = dumps2json(test_dict, indent=indent)
        expected = json.dumps(test_dict, indent=indent, ensure_ascii=False)
        assert result == expected

    def test_dumps_negative_indent_raises_error(self):
        """测试负缩进值抛出异常"""
        with pytest.raises(ValueError, match="indent must be a non-negative integer"):
            dumps2json({"key": "value"}, indent=-1)

    def test_dumps_non_integer_indent_raises_error(self):
        """测试非整数缩进值抛出异常"""
        with pytest.raises(ValueError, match="indent must be a non-negative integer"):
            dumps2json({"key": "value"}, indent="4")

    def test_dumps_custom_object_with_fallback(self):
        """测试自定义对象使用 jsonpickle 回退"""
        custom_obj = CustomClass("test_value")
        result = dumps2json(custom_obj, fallback_to_pickle=True)

        # 验证结果不为空且包含对象信息
        assert result is not None
        assert isinstance(result, str)
        assert "CustomClass" in result

    def test_dumps_datetime_with_fallback(self):
        """测试日期时间对象使用 jsonpickle 回退"""
        dt = datetime(2023, 1, 1, 12, 0, 0)
        result = dumps2json(dt, fallback_to_pickle=True)

        assert result is not None
        assert isinstance(result, str)
        assert "datetime" in result

    def test_dumps_custom_object_without_fallback_raises_error(self):
        """测试禁用回退时自定义对象抛出异常"""
        custom_obj = CustomClass("test_value")

        with pytest.raises(TypeError, match="Object of type .* is not JSON serializable"):
            dumps2json(custom_obj, fallback_to_pickle=False)

    def test_dumps_datetime_without_fallback_raises_error(self):
        """测试禁用回退时日期时间对象抛出异常"""
        dt = datetime(2023, 1, 1, 12, 0, 0)

        with pytest.raises(TypeError, match="Object of type .* is not JSON serializable"):
            dumps2json(dt, fallback_to_pickle=False)

    def test_dumps_set_with_fallback(self):
        """测试集合对象使用 jsonpickle 回退"""
        test_set = {1, 2, 3, "test"}
        result = dumps2json(test_set, fallback_to_pickle=True)

        assert result is not None
        assert isinstance(result, str)
        # 验证包含集合的相关信息
        assert "set" in result.lower()

    def test_dumps_complex_nested_structure(self):
        """测试复杂嵌套结构"""
        complex_data = {
            "string": "test",
            "number": 123,
            "float": 45.67,
            "boolean": True,
            "null_value": None,
            "list": [1, 2, 3, {"nested": "value"}],
            "nested_dict": {"inner": {"deep": "value", "array": [1, 2, 3]}},
        }

        result = dumps2json(complex_data)
        expected = json.dumps(complex_data, indent=4, ensure_ascii=False)
        assert result == expected

    def test_dumps_empty_structures(self):
        """测试空结构"""
        # 空字典
        assert dumps2json({}) == json.dumps({}, indent=4, ensure_ascii=False)

        # 空列表
        assert dumps2json([]) == json.dumps([], indent=4, ensure_ascii=False)

        # 空字符串
        assert dumps2json("") == json.dumps("", indent=4, ensure_ascii=False)

    def test_dumps_boolean_values(self):
        """测试布尔值"""
        assert dumps2json(True) == json.dumps(True, indent=4, ensure_ascii=False)
        assert dumps2json(False) == json.dumps(False, indent=4, ensure_ascii=False)

    def test_dumps_numeric_values(self):
        """测试数值类型"""
        # 整数
        assert dumps2json(42) == json.dumps(42, indent=4, ensure_ascii=False)

        # 浮点数
        assert dumps2json(3.14) == json.dumps(3.14, indent=4, ensure_ascii=False)

        # 负数
        assert dumps2json(-10) == json.dumps(-10, indent=4, ensure_ascii=False)

        # 零
        assert dumps2json(0) == json.dumps(0, indent=4, ensure_ascii=False)
