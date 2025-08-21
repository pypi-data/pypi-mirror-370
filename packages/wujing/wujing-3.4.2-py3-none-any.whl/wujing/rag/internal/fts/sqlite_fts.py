import logging
import os
import sqlite3
from contextlib import contextmanager
from typing import Dict, List, Optional, Annotated

from pydantic import Field, validate_call

from wujing.rag.internal.fts.base_fts import BaseFTSDatabase
from wujing.rag.stemmer import MixedLanguageStemmer
from wujing.rag.tokenizer import ChineseTokenizer

logger = logging.getLogger(__name__)


class SQLiteFTSDatabase(BaseFTSDatabase):
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def __init__(
        self,
        db_file: str = ".diskcache/sqlite_fts.db",
        table_name: str = "documents",
        top_k: Annotated[int, Field(gt=0)] = 2,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        use_stemming: bool = True,
    ):
        super().__init__(db_file, table_name, top_k, tokenizer, stemmer, use_stemming)
        self._connection: Optional[sqlite3.Connection] = None

    def _format_query_tokens(self, tokens: List[str]) -> str:
        """格式化查询词元为 SQLite FTS 语法"""
        # 对于 SQLite FTS5，我们使用 OR 连接词语以实现更好的匹配
        if len(tokens) > 1:
            return " OR ".join(tokens)
        return " ".join(tokens)

    @property
    def connection(self) -> sqlite3.Connection:
        if self._connection is None:
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
            self._connection = sqlite3.connect(self.db_file)
            self._connection.row_factory = sqlite3.Row
        return self._connection

    @contextmanager
    def get_connection(self):
        conn = self.connection
        try:
            yield conn
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            conn.rollback()
            raise

    def _reset_and_setup_database(self) -> None:
        """重置并设置数据库"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None

            if os.path.exists(self.db_file):
                os.remove(self.db_file)
                logger.info(f"已删除数据库文件: {self.db_file}")

            with self.get_connection() as conn:
                # 创建主表
                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id TEXT PRIMARY KEY,
                        original_text TEXT NOT NULL,
                        tokenized_text TEXT NOT NULL,
                        metadata TEXT  -- Document 的元数据，JSON 格式
                    );
                """
                conn.execute(create_table_sql)

                # 创建 FTS5 虚拟表
                create_fts_table_sql = f"""
                    CREATE VIRTUAL TABLE IF NOT EXISTS {self.table_name}_fts USING fts5(
                        id UNINDEXED,
                        tokenized_text,
                        content='{self.table_name}',
                        content_rowid='rowid'
                    );
                """
                conn.execute(create_fts_table_sql)

                # 创建触发器以保持 FTS 表与主表同步
                create_insert_trigger_sql = f"""
                    CREATE TRIGGER IF NOT EXISTS {self.table_name}_ai AFTER INSERT ON {self.table_name} BEGIN
                        INSERT INTO {self.table_name}_fts(id, tokenized_text) VALUES (new.id, new.tokenized_text);
                    END;
                """
                conn.execute(create_insert_trigger_sql)

                create_delete_trigger_sql = f"""
                    CREATE TRIGGER IF NOT EXISTS {self.table_name}_ad AFTER DELETE ON {self.table_name} BEGIN
                        INSERT INTO {self.table_name}_fts({self.table_name}_fts, id, tokenized_text) VALUES('delete', old.id, old.tokenized_text);
                    END;
                """
                conn.execute(create_delete_trigger_sql)

                create_update_trigger_sql = f"""
                    CREATE TRIGGER IF NOT EXISTS {self.table_name}_au AFTER UPDATE ON {self.table_name} BEGIN
                        INSERT INTO {self.table_name}_fts({self.table_name}_fts, id, tokenized_text) VALUES('delete', old.id, old.tokenized_text);
                        INSERT INTO {self.table_name}_fts(id, tokenized_text) VALUES (new.id, new.tokenized_text);
                    END;
                """
                conn.execute(create_update_trigger_sql)

                conn.commit()
                logger.info(f"数据库表 {self.table_name} 和 FTS 表创建成功")
        except Exception as e:
            logger.error(f"重置和设置数据库失败: {e}")
            raise

    def _insert_processed_data(self, processed_data: List[Dict], batch_size: int) -> None:
        """插入处理后的数据到 SQLite"""
        with self.get_connection() as conn:
            try:
                # 使用 INSERT OR REPLACE 来实现幂等性
                insert_sql = f"""
                    INSERT OR REPLACE INTO {self.table_name} (id, original_text, tokenized_text, metadata) 
                    VALUES (?, ?, ?, ?)
                """

                for i in range(0, len(processed_data), batch_size):
                    batch = processed_data[i : i + batch_size]
                    # 转换为元组列表格式，符合 sqlite3 的 executemany 要求
                    batch_tuples = [
                        (item["id"], item["original_text"], item["tokenized_text"], item["metadata"])
                        for item in batch
                    ]
                    conn.executemany(insert_sql, batch_tuples)

                    if i + batch_size < len(processed_data):
                        logger.info(f"已处理 {i + len(batch)}/{len(processed_data)} 个文档")

                conn.commit()

            except Exception as e:
                conn.rollback()
                logger.error(f"插入文档失败，已回滚: {e}")
                raise

    def _execute_fts_query(self, tokenized_query: str) -> List[Dict]:
        """执行 SQLite FTS 查询"""
        with self.get_connection() as conn:
            # 使用 FTS5 的 BM25 排序功能
            fts_query = f"""
                SELECT 
                    d.original_text,
                    d.metadata,
                    bm25({self.table_name}_fts) as score
                FROM {self.table_name}_fts
                INNER JOIN {self.table_name} d ON {self.table_name}_fts.id = d.id
                WHERE {self.table_name}_fts MATCH ?
                ORDER BY bm25({self.table_name}_fts)
                LIMIT ?
            """

            cursor = conn.execute(fts_query, (tokenized_query, self.top_k))
            results = cursor.fetchall()
            logger.info(f"FTS 检索返回 {len(results)} 个结果")

        document_results = []
        for row in results:
            original_text = row["original_text"]
            metadata_json = row["metadata"]
            score = row["score"]

            document = self._create_document_from_result(original_text, metadata_json)
            # SQLite FTS5 的 BM25 分数是负值，分数越小越相关，所以取负值
            document_results.append({"document": document, "score": float(-score)})

        return document_results

    def close(self) -> None:
        """关闭数据库连接"""
        try:
            if self._connection:
                self._connection.close()
                self._connection = None
                logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")



