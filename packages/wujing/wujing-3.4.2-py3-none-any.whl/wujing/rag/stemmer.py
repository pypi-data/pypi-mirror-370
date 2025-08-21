import re
from functools import lru_cache
from typing import List, Union

import Stemmer
from wujing.rag.tokenizer import tokenize


class MixedLanguageStemmer:
    """支持中英文混合的词干提取器

    特性：
    - 支持中英文混合文本的词干提取
    - 英文使用Porter词干提取算法
    - 中文保持原词不变
    - 缓存优化，提高性能
    - 支持批量处理
    """

    # 预编译正则表达式，提高性能
    _CHINESE_PATTERN = re.compile(r"[\u4e00-\u9fff]")
    _ENGLISH_PATTERN = re.compile(r"^[a-zA-Z]+$")

    def __init__(self, algorithm: str = "porter", min_word_length: int = 2):
        """
        初始化词干提取器

        Args:
            algorithm: 英文词干提取算法，默认使用porter
            min_word_length: 最小词长，短于此长度的词将被过滤
        """
        try:
            self.english_stemmer = Stemmer.Stemmer(algorithm)
        except Exception as e:
            raise ValueError(f"不支持的词干提取算法: {algorithm}") from e

        self.min_word_length = min_word_length

    @lru_cache(maxsize=10000)
    def _is_chinese_word(self, word: str) -> bool:
        """检查是否包含中文字符（带缓存）"""
        return bool(self._CHINESE_PATTERN.search(word))

    @lru_cache(maxsize=10000)
    def _is_pure_english_word(self, word: str) -> bool:
        """检查是否为纯英文单词（带缓存）"""
        return bool(self._ENGLISH_PATTERN.match(word))

    def stemWord(self, word: str) -> str:
        """
        对单个词进行词干提取

        Args:
            word: 待处理的词

        Returns:
            词干提取后的结果
        """
        if not word or len(word) < self.min_word_length:
            return word

        # 包含中文字符，直接返回原词
        if self._is_chinese_word(word):
            return word

        # 纯英文单词，进行词干提取
        if self._is_pure_english_word(word):
            return self.english_stemmer.stemWord(word.lower())

        # 其他情况（数字、符号等），返回原词
        return word

    def stem_words(self, words: List[str]) -> List[str]:
        """
        批量词干提取

        Args:
            words: 词列表

        Returns:
            处理后的词列表
        """
        return [self.stemWord(word) for word in words if word]

    def __call__(self, text: Union[str, List[str]]) -> List[str]:
        """
        支持文本或词列表的词干提取

        Args:
            text: 待处理的文本或词列表

        Returns:
            词干提取后的词列表
        """
        if isinstance(text, str):
            tokens = tokenize(text)
        elif isinstance(text, list):
            tokens = text
        else:
            raise TypeError("输入必须是字符串或字符串列表")

        return self.stem_words(tokens)

    def clear_cache(self) -> None:
        """清除缓存"""
        self._is_chinese_word.cache_clear()
        self._is_pure_english_word.cache_clear()

    def get_cache_info(self) -> dict:
        """获取缓存统计信息"""
        return {
            "chinese_word_cache": self._is_chinese_word.cache_info()._asdict(),
            "english_word_cache": self._is_pure_english_word.cache_info()._asdict(),
        }


if __name__ == "__main__":
    # 创建词干提取器
    stemmer = MixedLanguageStemmer()

    print("=== 单词词干提取测试 ===")
    word_examples = ["running", "jumped", "中文词汇", "testing", "今天天气怎么样", "Hello", "world"]
    for word in word_examples:
        stemmed = stemmer.stemWord(word)
        print(f"'{word}' -> '{stemmed}'")

    print("\n=== 文本词干提取测试 ===")
    text_examples = [
        "I am running and jumping happily today",
        "今天天气很好，我在跑步和跳跃",
        "The testing framework is working perfectly",
        "混合语言测试：running 和 跳跃 combined together",
    ]

    for text in text_examples:
        stemmed = stemmer(text)
        print(f"原文: {text}")
        print(f"词干: {stemmed}")
        print()

    print("=== 缓存统计信息 ===")
    cache_info = stemmer.get_cache_info()
    print(f"中文词缓存: {cache_info['chinese_word_cache']}")
    print(f"英文词缓存: {cache_info['english_word_cache']}")

    print("\n=== 批量处理测试 ===")
    word_list = ["running", "中文", "testing", "词汇", "jumped"]
    batch_result = stemmer.stem_words(word_list)
    print(f"词列表: {word_list}")
    print(f"批量结果: {batch_result}")
