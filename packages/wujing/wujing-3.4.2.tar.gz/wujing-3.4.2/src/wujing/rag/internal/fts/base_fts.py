import hashlib
import json
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Annotated, Dict, List, Optional, Self, Union

from pydantic import Field, validate_call

from wujing.rag.stemmer import MixedLanguageStemmer
from wujing.rag.tokenizer import ChineseTokenizer

logger = logging.getLogger(__name__)


@dataclass
class Document:
    """文档数据类"""
    text: str
    metadata: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        if not isinstance(self.text, str):
            raise TypeError("text must be a string")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def to_dict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        return {
            "text": self.text,
            "metadata": self.metadata,
        }


class BaseFTSDatabase(ABC):
    """FTS 数据库基础抽象类"""
    
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def __init__(
        self,
        db_file: str,
        table_name: str = "documents",
        top_k: Annotated[int, Field(gt=0)] = 2,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        use_stemming: bool = True,
    ):
        self.db_file = db_file
        self.table_name = table_name
        self.top_k = top_k
        self.use_stemming = use_stemming

        self.tokenizer = tokenizer if tokenizer is not None else ChineseTokenizer()
        self.stemmer = (
            stemmer
            if stemmer is not None
            else MixedLanguageStemmer(algorithm="porter", min_word_length=2)
            if use_stemming
            else None
        )

    def _process_text(self, text: str) -> List[str]:
        """处理文本：分词和可选的词干提取"""
        tokens = self.tokenizer.tokenize(text)
        if self.use_stemming and self.stemmer is not None:
            tokens = self.stemmer.stem_words(tokens)
        return tokens

    def _generate_document_id(self, document: Document) -> str:
        """为文档生成唯一标识符，基于文本内容和元数据的哈希值"""
        content = f"{document.text}|{json.dumps(document.metadata, sort_keys=True, ensure_ascii=False)}"
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    @lru_cache(maxsize=256)
    def _tokenize_query(self, query: str) -> str:
        """缓存查询分词结果"""
        processed_tokens = self._process_text(query)
        return self._format_query_tokens(processed_tokens)

    @abstractmethod
    def _format_query_tokens(self, tokens: List[str]) -> str:
        """格式化查询词元，子类需要实现具体的查询语法"""
        pass

    @abstractmethod
    def _reset_and_setup_database(self) -> None:
        """重置并设置数据库，子类需要实现具体的数据库操作"""
        pass

    @abstractmethod
    def get_connection(self):
        """获取数据库连接，子类需要实现具体的连接管理"""
        pass

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def insert_data(self, data: List[Document], batch_size: int = 1000) -> None:
        """插入 Document 对象到数据库"""
        if not data:
            logger.warning("没有数据需要插入")
            return

        logger.info(f"开始批量插入 {len(data)} 个文档...")

        try:
            processed_data = []
            for i, document in enumerate(data):
                if not document.text.strip():
                    logger.warning(f"文档 {i} 文本内容为空，跳过")
                    continue

                doc_id = self._generate_document_id(document)
                processed_tokens = self._process_text(document.text)
                tokenized_text = " ".join(processed_tokens)
                metadata_json = json.dumps(document.metadata, ensure_ascii=False) if document.metadata else None

                processed_data.append({
                    "id": doc_id,
                    "original_text": document.text,
                    "tokenized_text": tokenized_text,
                    "metadata": metadata_json,
                })

            self._insert_processed_data(processed_data, batch_size)
            logger.info(f"成功插入 {len(processed_data)} 个文档")

        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            raise

    @abstractmethod
    def _insert_processed_data(self, processed_data: List[Dict], batch_size: int) -> None:
        """插入处理后的数据，子类需要实现具体的插入逻辑"""
        pass

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def initialize(self, documents: List[Document]) -> Self:
        """完整初始化数据库：重置、设置、插入文档数据"""
        try:
            logger.info("开始初始化数据库...")
            self._reset_and_setup_database()
            self.insert_data(documents)
            logger.info("数据库初始化完成")
            return self
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise

    @abstractmethod
    def close(self) -> None:
        """关闭数据库连接"""
        pass

    def __enter__(self) -> Self:
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        self.close()

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def retrieve(self, query: str) -> List[Dict]:
        """执行 FTS 检索"""
        if not query.strip():
            logger.warning("查询字符串为空")
            return []

        try:
            tokenized_query = self._tokenize_query(query)
            if not tokenized_query.strip():
                logger.warning("分词后查询为空")
                return []

            return self._execute_fts_query(tokenized_query)

        except Exception as e:
            logger.error(f"FTS 检索失败: {e}")
            return []

    @abstractmethod
    def _execute_fts_query(self, tokenized_query: str) -> List[Dict]:
        """执行具体的 FTS 查询，子类需要实现"""
        pass

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def update_processors(
        self,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        use_stemming: Optional[bool] = None,
    ) -> None:
        """更新分词器和词干提取器并清除相关缓存"""
        if tokenizer is not None:
            self.tokenizer = tokenizer
        if stemmer is not None:
            self.stemmer = stemmer
        if use_stemming is not None:
            self.use_stemming = use_stemming
            if not use_stemming:
                self.stemmer = None

        self._tokenize_query.cache_clear()
        logger.info("已更新处理器并清除缓存")

    def _create_document_from_result(self, original_text: str, metadata_json: Optional[str]) -> Document:
        """从查询结果创建 Document 对象"""
        metadata = json.loads(metadata_json) if metadata_json else {}
        return Document(text=original_text, metadata=metadata)
