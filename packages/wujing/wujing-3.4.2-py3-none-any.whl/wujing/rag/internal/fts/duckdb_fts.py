import logging
import os
from contextlib import contextmanager
from typing import Annotated, Dict, List, Optional

from pydantic import Field, validate_call
from sqlalchemy import Engine, create_engine, text

from wujing.rag.internal.fts.base_fts import BaseFTSDatabase
from wujing.rag.stemmer import MixedLanguageStemmer
from wujing.rag.tokenizer import ChineseTokenizer

logger = logging.getLogger(__name__)


class DuckDBFTSDatabase(BaseFTSDatabase):
    @validate_call(config=dict(arbitrary_types_allowed=True, validate_assignment=False))
    def __init__(
        self,
        db_file: str = ".diskcache/duckdb_fts.db",
        table_name: str = "documents",
        top_k: Annotated[int, Field(gt=0)] = 2,
        tokenizer: Optional[ChineseTokenizer] = None,
        stemmer: Optional[MixedLanguageStemmer] = None,
        use_stemming: bool = True,
    ):
        super().__init__(db_file, table_name, top_k, tokenizer, stemmer, use_stemming)
        self._engine: Optional[Engine] = None
        self._fts_setup_done = False

    def _format_query_tokens(self, tokens: List[str]) -> str:
        """格式化查询词元为 DuckDB FTS 语法"""
        return " ".join(tokens)

    @property
    def engine(self) -> Engine:
        if self._engine is None:
            os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
            self._engine = create_engine(f"duckdb:///{self.db_file}")
            # 重新创建 engine 时重置 FTS 设置状态
            self._fts_setup_done = False
        return self._engine

    @contextmanager
    def get_connection(self):
        conn = self.engine.connect()
        try:
            if not self._fts_setup_done:
                conn.execute(text("INSTALL fts;"))
                conn.execute(text("LOAD fts;"))
                self._fts_setup_done = True
            yield conn
        except Exception as e:
            logger.error(f"数据库操作失败: {e}")
            raise
        finally:
            conn.close()

    def _reset_and_setup_database(self) -> None:
        """重置并设置数据库"""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None

            if os.path.exists(self.db_file):
                os.remove(self.db_file)
                logger.info(f"已删除数据库文件: {self.db_file}")

            self._fts_setup_done = False

            with self.get_connection() as conn:
                create_table_sql = f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        id TEXT PRIMARY KEY,
                        original_text TEXT NOT NULL,
                        tokenized_text TEXT NOT NULL,
                        metadata TEXT  -- Document 的元数据，JSON 格式
                    );
                """
                conn.execute(text(create_table_sql))
                conn.commit()
                logger.info(f"数据库表 {self.table_name} 创建成功")
        except Exception as e:
            logger.error(f"重置和设置数据库失败: {e}")
            raise

    def _insert_processed_data(self, processed_data: List[Dict], batch_size: int) -> None:
        """插入处理后的数据到 DuckDB"""
        with self.get_connection() as conn:
            trans = conn.begin()
            try:
                # 使用 INSERT OR REPLACE 来实现幂等性
                insert_sql = text(f"""
                    INSERT OR REPLACE INTO {self.table_name} (id, original_text, tokenized_text, metadata) 
                    VALUES (:id, :original_text, :tokenized_text, :metadata)
                """)

                for i in range(0, len(processed_data), batch_size):
                    batch = processed_data[i : i + batch_size]
                    conn.execute(insert_sql, batch)

                    if i + batch_size < len(processed_data):
                        logger.info(f"已处理 {i + len(batch)}/{len(processed_data)} 个文档")

                fts_index_sql = text(f"PRAGMA create_fts_index('{self.table_name}', 'id', 'tokenized_text');")
                conn.execute(fts_index_sql)
                trans.commit()

            except Exception as e:
                trans.rollback()
                logger.error(f"插入文档失败，已回滚: {e}")
                raise

    def _execute_fts_query(self, tokenized_query: str) -> List[Dict]:
        """执行 DuckDB FTS 查询"""
        with self.get_connection() as conn:
            fts_query = text(f"""
                SELECT 
                    d.original_text,
                    d.metadata,
                    fts_scores.score
                FROM (
                    SELECT 
                        id,
                        fts_main_{self.table_name}.match_bm25(id, :tokenized_query) AS score
                    FROM {self.table_name}
                    WHERE fts_main_{self.table_name}.match_bm25(id, :tokenized_query) IS NOT NULL
                    ORDER BY score DESC
                    LIMIT :top_k
                ) AS fts_scores
                INNER JOIN {self.table_name} d ON fts_scores.id = d.id
                ORDER BY fts_scores.score DESC;
            """)

            results = conn.execute(fts_query, {"tokenized_query": tokenized_query, "top_k": self.top_k}).fetchall()
            logger.info(f"FTS 检索返回 {len(results)} 个结果")

        document_results = []
        for original_text, metadata_json, score in results:
            document = self._create_document_from_result(original_text, metadata_json)
            document_results.append({"document": document, "score": float(score)})

        return document_results

    def close(self) -> None:
        """关闭数据库连接"""
        try:
            if self._engine:
                self._engine.dispose()
                self._engine = None
                logger.info("数据库连接已关闭")
        except Exception as e:
            logger.error(f"关闭数据库连接失败: {e}")
