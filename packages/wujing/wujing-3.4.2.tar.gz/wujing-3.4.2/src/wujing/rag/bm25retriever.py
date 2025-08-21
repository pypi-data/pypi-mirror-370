from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, List, Optional, Self, Literal

from llama_index.core import QueryBundle
from llama_index.core.constants import DEFAULT_SIMILARITY_TOP_K
from llama_index.core.retrievers import BaseRetriever
from llama_index.core.schema import BaseNode, NodeWithScore, TextNode
from pydantic import validate_call
from sqlalchemy import text

from wujing.rag.internal.fts.base_fts import BaseFTSDatabase, Document
from wujing.rag.internal.fts.duckdb_fts import DuckDBFTSDatabase
from wujing.rag.internal.fts.sqlite_fts import SQLiteFTSDatabase
from wujing.rag.stemmer import MixedLanguageStemmer
from wujing.rag.tokenizer import ChineseTokenizer

logger = logging.getLogger(__name__)

DEFAULT_PERSIST_FILENAME = "retriever.json"


class BM25Retriever(BaseRetriever):
    """增强的 BM25 检索器，支持 DuckDB FTS 或 SQLite FTS 后端

    这个检索器可以使用 DuckDB FTS 或 SQLite FTS 作为后端进行文档检索，
    充分利用数据库内建的 BM25 算法，包括高级中英文分词和词干提取。

    Args:
        nodes (List[BaseNode], optional):
            要索引的节点。如果未提供，将从现有数据库加载。
        tokenizer (ChineseTokenizer, optional):
            自定义分词器。默认使用 ChineseTokenizer。
        stemmer (MixedLanguageStemmer, optional):
            词干提取器。默认创建新的实例。
        backend (Literal["duckdb", "sqlite"], optional):
            FTS 后端类型。默认为 "duckdb"。
        db_path (str, optional):
            数据库路径。默认为 ".diskcache/bm25_retriever.db"。
        table_name (str, optional):
            数据库表名。默认为 "documents"。
        similarity_top_k (int, optional):
            返回结果数量。默认为 DEFAULT_SIMILARITY_TOP_K。
        use_stemming (bool, optional):
            是否使用词干提取。默认为 True。
        verbose (bool, optional):
            是否显示进度。默认为 False。
    """

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def __init__(
        self,
        nodes: Optional[List[BaseNode]] = None,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        backend: Literal["duckdb", "sqlite"] = "duckdb",
        db_path: str = ".diskcache/bm25_retriever.db",
        table_name: str = "documents",
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        use_stemming: bool = True,
        verbose: bool = False,
    ) -> None:
        self.backend = backend
        self.db_path = db_path
        self.table_name = table_name
        self.similarity_top_k = similarity_top_k
        self.use_stemming = use_stemming
        self._verbose = verbose

        # 根据后端类型创建相应的数据库实例
        self.database = self._create_fts_database(
            backend=backend,
            db_path=db_path,
            table_name=table_name,
            top_k=similarity_top_k,
            tokenizer=tokenizer,
            stemmer=stemmer,
            use_stemming=use_stemming,
        )

        # 如果提供了节点，则初始化数据库
        if nodes is not None:
            self._setup_database_with_nodes(nodes)

        super().__init__(verbose=verbose)

    def _create_fts_database(
        self,
        backend: Literal["duckdb", "sqlite"],
        db_path: str,
        table_name: str,
        top_k: int,
        tokenizer: Optional[ChineseTokenizer],
        stemmer: Optional[MixedLanguageStemmer],
        use_stemming: bool,
    ) -> BaseFTSDatabase:
        """根据后端类型创建相应的 FTS 数据库实例"""
        if backend == "duckdb":
            return DuckDBFTSDatabase(
                db_file=db_path,
                table_name=table_name,
                top_k=top_k,
                tokenizer=tokenizer,
                stemmer=stemmer,
                use_stemming=use_stemming,
            )
        elif backend == "sqlite":
            return SQLiteFTSDatabase(
                db_file=db_path,
                table_name=table_name,
                top_k=top_k,
                tokenizer=tokenizer,
                stemmer=stemmer,
                use_stemming=use_stemming,
            )
        else:
            raise ValueError(f"不支持的 FTS 后端类型: {backend}")

    def _setup_database_with_nodes(self, nodes: List[BaseNode]) -> None:
        """使用节点设置 FTS 数据库，将节点转换为 Document 对象"""
        try:
            documents = []
            for i, node in enumerate(nodes):
                text = node.get_content()

                metadata = {"node_id": node.node_id or str(i), "node_index": str(i)}

                if hasattr(node, "metadata") and node.metadata:
                    for key, value in node.metadata.items():
                        metadata[f"node_{key}"] = str(value)

                documents.append(Document(text=text, metadata=metadata))

            self.database.initialize(documents)

            logger.info(f"成功初始化包含 {len(nodes)} 个节点的 {self.backend.upper()} BM25 索引")
        except Exception as e:
            logger.error(f"{self.backend.upper()} BM25 数据库初始化失败: {e}")
            raise

    @classmethod
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def from_defaults(
        cls,
        nodes: List[BaseNode],
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        backend: Literal["duckdb", "sqlite"] = "duckdb",
        db_path: str = ".diskcache/bm25_retriever.db",
        table_name: str = "documents",
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        use_stemming: bool = True,
        verbose: bool = False,
    ) -> Self:
        """从默认参数创建增强 BM25 检索器"""
        return cls(
            nodes=nodes,
            tokenizer=tokenizer,
            stemmer=stemmer,
            backend=backend,
            db_path=db_path,
            table_name=table_name,
            similarity_top_k=similarity_top_k,
            use_stemming=use_stemming,
            verbose=verbose,
        )

    @classmethod
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def from_documents(
        cls,
        documents: List[str],
        backend: Literal["duckdb", "sqlite"] = "duckdb",
        similarity_top_k: int = DEFAULT_SIMILARITY_TOP_K,
        use_stemming: bool = True,
        verbose: bool = False,
    ) -> Self:
        """从文档字符串列表创建增强 BM25 检索器"""
        nodes = [TextNode(text=doc) for doc in documents]
        return cls.from_defaults(
            nodes=nodes,
            backend=backend,
            similarity_top_k=similarity_top_k,
            use_stemming=use_stemming,
            verbose=verbose,
        )

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def get_persist_args(self) -> Dict[str, Any]:
        """获取持久化参数字典"""
        return {
            "backend": self.backend,
            "similarity_top_k": self.similarity_top_k,
            "use_stemming": self.use_stemming,
            "db_path": self.db_path,
            "table_name": self.table_name,
            "verbose": self._verbose,
        }

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def persist(self, path: str, **kwargs: Any) -> None:
        """持久化检索器到目录"""
        os.makedirs(path, exist_ok=True)

        with open(os.path.join(path, DEFAULT_PERSIST_FILENAME), "w", encoding="utf-8") as f:
            json.dump(self.get_persist_args(), f, indent=2, ensure_ascii=False)

        logger.info(f"检索器已持久化到: {path}")
        logger.info(f"注意：节点元信息已存储在 {self.backend.upper()} 数据库中，无需单独保存")

    @classmethod
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def from_persist_dir(cls, path: str, **kwargs: Any) -> Self:
        """从目录加载检索器"""
        config_path = os.path.join(path, DEFAULT_PERSIST_FILENAME)
        if os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                retriever_data = json.load(f)
        else:
            retriever_data = {}

        instance = cls(**retriever_data)

        # 确保数据库连接和FTS扩展正确初始化
        try:
            # 对于DuckDB，通过建立连接来确保FTS扩展被加载
            if instance.backend == "duckdb":
                with instance.database.get_connection() as conn:
                    # 验证表是否存在（DuckDB方式）
                    result = conn.execute(text(f"SELECT table_name FROM information_schema.tables WHERE table_name='{instance.table_name}';")).fetchone()
                    if not result:
                        logger.warning(f"表 {instance.table_name} 不存在于持久化数据库中")
            elif instance.backend == "sqlite":
                with instance.database.get_connection() as conn:
                    # 验证表是否存在（SQLite方式）
                    result = conn.execute(text(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{instance.table_name}';")).fetchone()
                    if not result:
                        logger.warning(f"表 {instance.table_name} 不存在于持久化数据库中")
        except Exception as e:
            logger.warning(f"验证持久化数据库时出现问题: {e}")

        logger.info("检索器已从持久化目录加载")
        logger.info(f"注意：节点元信息将从 {instance.backend.upper()} 数据库中动态加载")
        return instance

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        """执行 FTS BM25 检索，将检索结果转换为 NodeWithScore"""
        if not query_bundle.query_str.strip():
            logger.warning("查询字符串为空")
            return []

        try:
            document_results = self.database.retrieve(query_bundle.query_str)

            node_results = []
            for doc_result in document_results:
                document = doc_result["document"]
                score = doc_result["score"]

                node_id = document.metadata.get("node_id", "")

                text_node = TextNode(text=document.text, id_=node_id)

                node_metadata = {}
                for key, value in document.metadata.items():
                    if key.startswith("node_") and key not in ["node_id", "node_index"]:
                        original_key = key[5:]  # 移除 "node_" 前缀
                        node_metadata[original_key] = value

                if node_metadata:
                    text_node.metadata = node_metadata

                node_results.append(NodeWithScore(node=text_node, score=score))

            logger.info(f"{self.backend.upper()} BM25 检索返回 {len(node_results)} 个结果")
            return node_results

        except Exception as e:
            logger.error(f"{self.backend.upper()} BM25 检索失败: {e}")
            return []

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def clear_cache(self) -> None:
        """清空缓存"""
        if hasattr(self.database, "_tokenize_query") and hasattr(self.database._tokenize_query, "cache_clear"):
            self.database._tokenize_query.cache_clear()

        if self.database.tokenizer and hasattr(self.database.tokenizer, "clear_cache"):
            self.database.tokenizer.clear_cache()
        if self.database.stemmer and hasattr(self.database.stemmer, "clear_cache"):
            self.database.stemmer.clear_cache()

        logger.info("所有缓存已清空")

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def get_stats(self) -> Dict[str, Any]:
        """获取检索器统计信息"""
        stats = {
            "backend": self.backend,
            "similarity_top_k": self.similarity_top_k,
            "use_stemming": self.use_stemming,
            "db_path": self.db_path,
            "table_name": self.table_name,
            "corpus_size": "存储在数据库中",
        }

        if self.database.tokenizer and hasattr(self.database.tokenizer, "get_stats"):
            stats["tokenizer_stats"] = self.database.tokenizer.get_stats()

        if self.database.stemmer and hasattr(self.database.stemmer, "get_cache_info"):
            stats["stemmer_cache"] = self.database.stemmer.get_cache_info()

        return stats

    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def update_processors(
        self,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        use_stemming: Optional[bool] = None,
    ) -> None:
        """更新分词器和词干提取器"""
        self.database.update_processors(
            tokenizer=tokenizer,
            stemmer=stemmer,
            use_stemming=use_stemming,
        )

        if use_stemming is not None:
            self.use_stemming = use_stemming

        logger.info("已更新处理器")

    def close(self) -> None:
        """关闭数据库连接"""
        if self.database:
            self.database.close()

    def __enter__(self) -> BM25Retriever:
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        self.close()
