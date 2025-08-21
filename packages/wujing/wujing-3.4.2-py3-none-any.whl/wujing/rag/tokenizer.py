import logging
import os
import string
from functools import lru_cache
from typing import List, Optional, Set

import jieba
import nltk
import nltk.data
from nltk.corpus import stopwords as nltk_stopwords


class ChineseTokenizer:
    """高性能中英文分词器，支持停用词过滤和标点符号清理。

    特性：
    - 支持中英文混合文本分词
    - 智能停用词过滤
    - 标点符号清理
    - 线程安全
    - 缓存优化
    """

    def __init__(self, min_token_length: int = 2, log_level: int = logging.WARNING):
        """
        初始化分词器。

        Args:
            min_token_length: 最小词汇长度，默认为2
            log_level: jieba日志级别，默认为WARNING
        """
        self.min_token_length = min_token_length
        self._setup_jieba(log_level)
        self._setup_nltk()

        # 懒加载缓存属性
        self._stopwords_cache: Optional[Set[str]] = None
        self._punctuation_cache: Optional[Set[str]] = None

    def _setup_jieba(self, log_level: int) -> None:
        """配置jieba分词器。"""
        jieba.setLogLevel(log_level)

    def _setup_nltk(self) -> None:
        """配置NLTK数据路径，支持多种路径查找策略。"""
        # 优先级顺序：相对路径 -> 环境变量 -> 默认路径
        possible_paths = [
            os.path.join(os.path.dirname(__file__), "internal", "nltk_data"),
            os.environ.get("NLTK_DATA", ""),
            os.path.expanduser("~/nltk_data"),
        ]

        for nltk_data_path in possible_paths:
            if nltk_data_path and os.path.exists(nltk_data_path):
                if nltk_data_path not in nltk.data.path:
                    nltk.data.path.append(nltk_data_path)
                return

        logging.warning("No valid NLTK data directory found. Stopwords functionality may not work properly.")

    @property
    def _stopwords(self) -> Set[str]:
        """懒加载停用词集合。"""
        if self._stopwords_cache is None:
            self._stopwords_cache = self._load_stopwords()
        return self._stopwords_cache

    @property
    def _punctuation(self) -> Set[str]:
        """懒加载标点符号集合。"""
        if self._punctuation_cache is None:
            self._punctuation_cache = self._load_punctuation()
        return self._punctuation_cache

    @lru_cache(maxsize=1)
    def _load_stopwords(self) -> Set[str]:
        """加载中英文停用词集合。"""
        try:
            chinese_stopwords = set(nltk_stopwords.words("chinese"))
            english_stopwords = set(nltk_stopwords.words("english"))
            return chinese_stopwords | english_stopwords
        except LookupError as e:
            logging.warning(f"Failed to load stopwords: {e}")
            return set()

    @lru_cache(maxsize=1)
    def _load_punctuation(self) -> Set[str]:
        """加载中英文标点符号集合。"""
        chinese_punctuation = (
            "！？｡。＂＃＄％＆＇（）＊＋，－／：；＜＝＞＠［＼］＾＿｀｛｜｝～｟｠｢｣､、〃》「」『』【】〔〕〖〗〘〙〚〛〜〝〞〟〰–—''‛"
            "„‟…‧﹏."
        )
        return set(string.punctuation + chinese_punctuation)

    def tokenize(self, text: Optional[str]) -> List[str]:
        """
        对文本进行分词处理。

        Args:
            text: 待分词的文本

        Returns:
            过滤后的词汇列表
        """
        if not text or not text.strip():
            return []

        # 预处理：去除首尾空白
        cleaned_text = text.strip()

        # 使用jieba进行搜索引擎模式分词
        tokens = jieba.cut_for_search(cleaned_text)

        # 过滤词汇：去除停用词、标点符号和长度不足的词
        # 避免重复调用strip()
        filtered_tokens = []
        for token in tokens:
            stripped_token = token.strip()
            if self._is_valid_token(stripped_token):
                filtered_tokens.append(stripped_token)

        return filtered_tokens

    def tokenize_batch(self, texts: List[str]) -> List[List[str]]:
        """
        批量分词处理，提高处理大量文本的效率。

        Args:
            texts: 待分词的文本列表

        Returns:
            分词结果列表
        """
        return [self.tokenize(text) for text in texts]

    def add_custom_stopwords(self, words: List[str]) -> None:
        """
        添加自定义停用词。

        Args:
            words: 要添加的停用词列表
        """
        if self._stopwords_cache is not None:
            self._stopwords_cache.update(words)
        else:
            # 如果还没有初始化，先加载然后添加
            _ = self._stopwords  # 触发懒加载
            self._stopwords_cache.update(words)

    def get_stats(self) -> dict:
        """
        获取分词器统计信息。

        Returns:
            包含统计信息的字典
        """
        return {
            "min_token_length": self.min_token_length,
            "stopwords_count": len(self._stopwords) if self._stopwords_cache else "not_loaded",
            "punctuation_count": len(self._punctuation) if self._punctuation_cache else "not_loaded",
        }

    def _is_valid_token(self, token: str) -> bool:
        """
        检查词汇是否有效。

        Args:
            token: 待检查的词汇（应已去除空白）

        Returns:
            是否为有效词汇
        """
        # 快速检查：空字符串或长度不足
        if not token or len(token) < self.min_token_length:
            return False

        # 检查是否为停用词或标点符号
        return token not in self._stopwords and token not in self._punctuation


# 线程安全的全局默认分词器实例
_default_tokenizer: Optional[ChineseTokenizer] = None
_tokenizer_lock = None


def get_default_tokenizer() -> ChineseTokenizer:
    """获取默认分词器实例（线程安全的单例模式）。"""
    global _default_tokenizer, _tokenizer_lock

    if _default_tokenizer is None:
        # 延迟导入Lock以避免在模块级别导入threading
        if _tokenizer_lock is None:
            from threading import Lock

            _tokenizer_lock = Lock()

        with _tokenizer_lock:
            # 双重检查锁定模式
            if _default_tokenizer is None:
                _default_tokenizer = ChineseTokenizer()

    return _default_tokenizer


def tokenize(text: Optional[str]) -> List[str]:
    """
    便捷的分词函数，使用默认分词器。

    Args:
        text: 待分词的文本

    Returns:
        过滤后的词汇列表
    """
    return get_default_tokenizer().tokenize(text)


def tokenize_batch(texts: List[str]) -> List[List[str]]:
    """
    便捷的批量分词函数，使用默认分词器。

    Args:
        texts: 待分词的文本列表

    Returns:
        分词结果列表
    """
    return get_default_tokenizer().tokenize_batch(texts)


if __name__ == "__main__":
    import time

    # 测试示例
    print("=== 中英文分词器测试 ===")

    # 使用默认分词器
    text_examples = [
        "今天天气很好，我们去公园散步，are you fine。",
        "这是一个测试文本，包含中文和English混合内容！",
        "人工智能AI技术发展迅速，machine learning很重要。",
        "",  # 空文本测试
        "   ",  # 空白文本测试
    ]

    for i, text in enumerate(text_examples, 1):
        print(f"\n示例 {i}:")
        print(f"原文: '{text}'")
        tokens = tokenize(text)
        print(f"分词结果: {tokens}")
        print(f"词汇数量: {len(tokens)}")

    # 测试自定义分词器
    print("\n=== 自定义分词器测试 ===")
    custom_tokenizer = ChineseTokenizer(min_token_length=1, log_level=logging.INFO)
    text = "我爱你中国！I love China."
    tokens = custom_tokenizer.tokenize(text)
    print(f"自定义分词器结果: {tokens}")

    # 测试批量分词
    print("\n=== 批量分词测试 ===")
    batch_texts = [
        "机器学习是人工智能的重要分支",
        "Natural language processing is fascinating",
        "深度学习在图像识别中应用广泛",
    ]
    batch_results = tokenize_batch(batch_texts)
    for text, result in zip(batch_texts, batch_results):
        print(f"文本: {text}")
        print(f"分词: {result}")

    # 性能测试
    print("\n=== 性能测试 ===")
    test_text = "机器学习和深度学习是人工智能领域的核心技术，natural language processing也很重要。" * 100

    start_time = time.time()
    for _ in range(100):
        tokenize(test_text)
    end_time = time.time()

    print(f"处理100次大文本耗时: {end_time - start_time:.4f}秒")

    # 显示统计信息
    print("\n=== 分词器统计 ===")
    print(get_default_tokenizer().get_stats())
