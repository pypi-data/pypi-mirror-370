"""BM25Retriever 的 pytest 测试模块

此模块包含对 BM25Retriever 的全面测试，支持 DuckDB 和 SQLite 两种后端。
"""

import json
import logging
import os
import shutil
import tempfile
import time
from typing import List

import pytest
from llama_index.core import QueryBundle

from wujing.rag.bm25retriever import BM25Retriever

# 配置日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


@pytest.fixture(scope="module")
def sample_documents() -> List[str]:
    """提供测试用的示例文档"""
    return [
        "马斯克是特斯拉的首席执行官，该公司是电动汽车领域的领导者。",
        "他也是 SpaceX 的创始人和首席执行官，这是一家致力于太空探索的公司。",
        "此外，马斯克还参与了 Neuralink 和 The Boring Company 等项目。",
        "特斯拉不仅生产电动汽车，还涉足太阳能和储能解决方案。",
        "SpaceX 已经成功进行了多次火箭发射和回收，降低了太空探索的成本。",
        "Neuralink 旨在开发脑机接口技术，帮助治疗神经系统疾病。",
        "The Tesla Model S is an electric luxury sedan with impressive performance.",
        "SpaceX Falcon 9 rockets are designed for reliable and safe transport of satellites.",
        "Neuralink aims to create brain-computer interfaces for medical applications.",
    ]


@pytest.fixture(scope="module")
def test_queries() -> List[str]:
    """提供测试用的查询语句"""
    return [
        "谁是特斯拉的CEO？",
        "SpaceX是做什么的？",
        "Neuralink的目标是什么？",
        "electric vehicles Tesla",
        "brain computer interface technology",
    ]


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    # 清理临时目录
    shutil.rmtree(temp_path, ignore_errors=True)


class TestBM25Retriever:
    """BM25Retriever 测试类"""

    @pytest.mark.parametrize("backend", ["duckdb", "sqlite"])
    def test_create_retriever_from_documents(self, sample_documents: List[str], backend: str, temp_dir: str):
        """测试从文档创建检索器"""
        from llama_index.core.schema import TextNode
        
        db_path = os.path.join(temp_dir, f"test_{backend}.db")
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend=backend,
            similarity_top_k=3,
            use_stemming=True,
            verbose=True,
            db_path=db_path,
        ) as retriever:
            assert retriever.backend == backend
            assert retriever.similarity_top_k == 3
            assert retriever.use_stemming is True
            assert retriever.db_path == db_path

    @pytest.mark.parametrize("backend", ["duckdb", "sqlite"])
    def test_retriever_stats(self, sample_documents: List[str], backend: str, temp_dir: str):
        """测试检索器统计信息"""
        from llama_index.core.schema import TextNode
        
        db_path = os.path.join(temp_dir, f"test_stats_{backend}.db")
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend=backend,
            similarity_top_k=3,
            use_stemming=True,
            verbose=True,
            db_path=db_path,
        ) as retriever:
            stats = retriever.get_stats()
            
            # 验证统计信息包含必要字段
            assert "backend" in stats
            assert "similarity_top_k" in stats
            assert "use_stemming" in stats
            assert "db_path" in stats
            assert "table_name" in stats
            assert "corpus_size" in stats
            
            assert stats["backend"] == backend
            assert stats["similarity_top_k"] == 3
            assert stats["use_stemming"] is True

    @pytest.mark.parametrize("backend", ["duckdb", "sqlite"])
    def test_basic_retrieval(self, sample_documents: List[str], test_queries: List[str], backend: str, temp_dir: str):
        """测试基本检索功能"""
        from llama_index.core.schema import TextNode
        
        db_path = os.path.join(temp_dir, f"test_retrieval_{backend}.db")
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend=backend,
            similarity_top_k=3,
            use_stemming=True,
            verbose=True,
            db_path=db_path,
        ) as retriever:
            # 测试每个查询
            for query in test_queries[:3]:  # 测试前3个查询
                result = retriever.retrieve(QueryBundle(query_str=query))
                
                # 验证返回结果
                assert isinstance(result, list)
                assert len(result) <= 3  # 不超过 top_k
                
                # 验证结果结构
                for node_with_score in result:
                    assert hasattr(node_with_score, 'node')
                    assert hasattr(node_with_score, 'score')
                    assert isinstance(node_with_score.score, (int, float))
                    assert node_with_score.node.get_content() in sample_documents

    @pytest.mark.parametrize("backend", ["duckdb", "sqlite"])
    def test_empty_query(self, sample_documents: List[str], backend: str, temp_dir: str):
        """测试空查询处理"""
        from llama_index.core.schema import TextNode
        
        db_path = os.path.join(temp_dir, f"test_empty_{backend}.db")
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend=backend,
            similarity_top_k=3,
            use_stemming=True,
            verbose=True,
            db_path=db_path,
        ) as retriever:
            # 测试空字符串查询
            result = retriever.retrieve(QueryBundle(query_str=""))
            assert result == []
            
            # 测试只有空格的查询
            result = retriever.retrieve(QueryBundle(query_str="   "))
            assert result == []

    @pytest.mark.parametrize("backend", ["duckdb", "sqlite"])
    def test_persistence(self, sample_documents: List[str], backend: str, temp_dir: str):
        """测试检索器持久化和加载"""
        from llama_index.core.schema import TextNode
        
        db_path = os.path.join(temp_dir, f"test_persist_{backend}.db")
        persist_dir = os.path.join(temp_dir, f"persist_{backend}")
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        # 创建并持久化检索器
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend=backend,
            similarity_top_k=3,
            use_stemming=True,
            verbose=True,
            db_path=db_path,
        ) as retriever:
            retriever.persist(persist_dir)
        
        # 验证持久化文件存在
        config_file = os.path.join(persist_dir, "retriever.json")
        assert os.path.exists(config_file)
        
        # 验证配置文件内容
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        assert config["backend"] == backend
        assert config["similarity_top_k"] == 3
        assert config["use_stemming"] is True
        
        # 从持久化目录加载检索器
        with BM25Retriever.from_persist_dir(persist_dir) as loaded_retriever:
            assert loaded_retriever.backend == backend
            assert loaded_retriever.similarity_top_k == 3
            assert loaded_retriever.use_stemming is True
            
            # 测试加载的检索器是否能正常工作
            test_query = "马斯克CEO特斯拉"
            result = loaded_retriever.retrieve(QueryBundle(query_str=test_query))
            assert isinstance(result, list)

    def test_performance_comparison(self, sample_documents: List[str], temp_dir: str):
        """测试 DuckDB 和 SQLite 后端性能对比"""
        from llama_index.core.schema import TextNode
        
        test_query = "马斯克CEO特斯拉"
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        # DuckDB 性能测试
        duckdb_path = os.path.join(temp_dir, "perf_duckdb.db")
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend="duckdb",
            similarity_top_k=3,
            use_stemming=True,
            db_path=duckdb_path,
        ) as duckdb_retriever:
            start_time = time.time()
            duckdb_result = duckdb_retriever.retrieve(QueryBundle(query_str=test_query))
            duckdb_time = time.time() - start_time
        
        # SQLite 性能测试
        sqlite_path = os.path.join(temp_dir, "perf_sqlite.db")
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend="sqlite",
            similarity_top_k=3,
            use_stemming=True,
            db_path=sqlite_path,
        ) as sqlite_retriever:
            start_time = time.time()
            sqlite_result = sqlite_retriever.retrieve(QueryBundle(query_str=test_query))
            sqlite_time = time.time() - start_time
        
        # 验证两种后端都能返回结果
        assert len(duckdb_result) > 0
        assert len(sqlite_result) > 0
        
        # 记录性能数据（用于调试和优化）
        print(f"\nDuckDB FTS 检索耗时: {duckdb_time * 1000:.2f}ms，结果数量: {len(duckdb_result)}")
        print(f"SQLite FTS 检索耗时: {sqlite_time * 1000:.2f}ms，结果数量: {len(sqlite_result)}")

    def test_results_consistency(self, sample_documents: List[str], temp_dir: str):
        """测试 DuckDB 和 SQLite 后端结果一致性"""
        from llama_index.core.schema import TextNode
        
        test_query = "马斯克CEO特斯拉"
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        # DuckDB 结果
        duckdb_path = os.path.join(temp_dir, "consistency_duckdb.db")
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend="duckdb",
            similarity_top_k=3,
            use_stemming=True,
            db_path=duckdb_path,
        ) as duckdb_retriever:
            duckdb_result = duckdb_retriever.retrieve(QueryBundle(query_str=test_query))
        
        # SQLite 结果
        sqlite_path = os.path.join(temp_dir, "consistency_sqlite.db")
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend="sqlite",
            similarity_top_k=3,
            use_stemming=True,
            db_path=sqlite_path,
        ) as sqlite_retriever:
            sqlite_result = sqlite_retriever.retrieve(QueryBundle(query_str=test_query))
        
        # 验证结果数量一致性
        assert len(duckdb_result) == len(sqlite_result)
        
        # 提取文档内容进行对比
        duckdb_contents = [node.node.get_content() for node in duckdb_result]
        sqlite_contents = [node.node.get_content() for node in sqlite_result]
        
        # 验证返回的文档内容一致（顺序可能不同，但内容应该相同）
        assert set(duckdb_contents) == set(sqlite_contents)

    @pytest.mark.parametrize("backend", ["duckdb", "sqlite"])
    def test_cache_operations(self, sample_documents: List[str], backend: str, temp_dir: str):
        """测试缓存操作"""
        from llama_index.core.schema import TextNode
        
        db_path = os.path.join(temp_dir, f"test_cache_{backend}.db")
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend=backend,
            similarity_top_k=3,
            use_stemming=True,
            verbose=True,
            db_path=db_path,
        ) as retriever:
            # 测试清理缓存（不应该抛出异常）
            retriever.clear_cache()
            
            # 验证清理缓存后仍能正常检索
            test_query = "特斯拉"
            result = retriever.retrieve(QueryBundle(query_str=test_query))
            assert len(result) > 0

    def test_invalid_backend(self, sample_documents: List[str], temp_dir: str):
        """测试无效后端处理"""
        from llama_index.core.schema import TextNode
        from pydantic_core import ValidationError
        
        nodes = [TextNode(text=doc) for doc in sample_documents]
        with pytest.raises(ValidationError, match="Input should be 'duckdb' or 'sqlite'"):
            BM25Retriever.from_defaults(
                nodes=nodes,
                backend="invalid_backend",  # type: ignore
                db_path=os.path.join(temp_dir, "invalid.db"),
            )

    @pytest.mark.parametrize("backend", ["duckdb", "sqlite"])
    def test_context_manager(self, sample_documents: List[str], backend: str, temp_dir: str):
        """测试上下文管理器功能"""
        from llama_index.core.schema import TextNode
        
        db_path = os.path.join(temp_dir, f"test_context_{backend}.db")
        nodes = [TextNode(text=doc) for doc in sample_documents]
        
        # 测试正常使用上下文管理器
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend=backend,
            db_path=db_path,
        ) as retriever:
            result = retriever.retrieve(QueryBundle(query_str="特斯拉"))
            assert len(result) > 0
        
        # 上下文退出后，数据库连接应该被关闭
        # 这里我们只验证不会抛出异常


# 性能基准测试（可选）
class TestBM25RetrieverPerformance:
    """BM25Retriever 性能测试类"""
    
    @pytest.mark.performance
    @pytest.mark.parametrize("backend", ["duckdb", "sqlite"])
    def test_large_corpus_performance(self, backend: str, temp_dir: str):
        """测试大语料库性能（标记为性能测试，默认不运行）"""
        from llama_index.core.schema import TextNode
        
        # 创建较大的文档集合
        large_documents = [
            f"这是第{i}个测试文档，包含关于人工智能、机器学习和深度学习的内容。" +
            f"文档{i}讨论了各种技术话题，包括自然语言处理、计算机视觉和推荐系统。"
            for i in range(100)
        ]
        
        db_path = os.path.join(temp_dir, f"large_corpus_{backend}.db")
        nodes = [TextNode(text=doc) for doc in large_documents]
        
        # 测试创建时间
        start_time = time.time()
        with BM25Retriever.from_defaults(
            nodes=nodes,
            backend=backend,
            similarity_top_k=10,
            db_path=db_path,
        ) as retriever:
            creation_time = time.time() - start_time
            
            # 测试检索时间
            start_time = time.time()
            result = retriever.retrieve(QueryBundle(query_str="人工智能机器学习"))
            retrieval_time = time.time() - start_time
            
            print(f"\n{backend.upper()} 大语料库测试:")
            print(f"  创建时间: {creation_time * 1000:.2f}ms")
            print(f"  检索时间: {retrieval_time * 1000:.2f}ms")
            print(f"  结果数量: {len(result)}")
            
            # 基本验证
            assert len(result) > 0
            assert len(result) <= 10
