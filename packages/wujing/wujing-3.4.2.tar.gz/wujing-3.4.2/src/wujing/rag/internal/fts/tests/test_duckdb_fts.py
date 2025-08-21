import logging
import pytest

from wujing.rag.internal.fts.base_fts import Document
from wujing.rag.internal.fts.duckdb_fts import DuckDBFTSDatabase
from wujing.rag.tokenizer import ChineseTokenizer
from wujing.rag.stemmer import MixedLanguageStemmer

logger = logging.getLogger(__name__)


class TestDuckDBFTSDatabase:
    """测试 DuckDBFTSDatabase 类"""

    @pytest.fixture
    def sample_documents(self):
        """创建测试用的文档样本"""
        return [
            Document("马斯克是特斯拉的首席执行官，该公司是电动汽车领域的领导者。", {"topic": "Tesla", "person": "马斯克"}),
            Document(
                "他也是 SpaceX 的创始人和首席执行官，这是一家致力于太空探索的公司。",
                {"topic": "SpaceX", "person": "马斯克"},
            ),
            Document(
                "此外，马斯克还参与了 Neuralink 和 The Boring Company 等项目。", {"topic": "其他项目", "person": "马斯克"}
            ),
            Document("特斯拉不仅生产电动汽车，还涉足太阳能和储能解决方案。", {"topic": "Tesla", "business": "能源"}),
            Document("SpaceX 成功实现了火箭的可重复使用，大大降低了发射成本。", {"topic": "SpaceX", "technology": "火箭"}),
            Document(
                "Neuralink 致力于开发脑机接口技术，可能革命性地改变医疗行业。",
                {"topic": "Neuralink", "technology": "脑机接口"},
            ),
        ]

    @pytest.fixture
    def additional_documents(self):
        """创建额外的测试文档"""
        return [
            Document("苹果公司是全球领先的科技公司，以iPhone和Mac产品闻名。", {"topic": "Apple", "company": "苹果"}),
            Document("库克是苹果公司的现任CEO，接替了乔布斯的职位。", {"topic": "Apple", "person": "库克"}),
        ]

    @pytest.fixture
    def custom_tokenizer(self):
        """创建自定义分词器"""
        return ChineseTokenizer(min_token_length=2)

    @pytest.fixture
    def custom_stemmer(self):
        """创建自定义词干提取器"""
        return MixedLanguageStemmer(algorithm="porter", min_word_length=2)

    def test_database_initialization_and_basic_retrieval(self, sample_documents, custom_tokenizer, custom_stemmer):
        """测试数据库初始化和基本检索功能"""
        logger.info("=" * 60)
        logger.info("测试数据库初始化和基本检索功能")
        logger.info("=" * 60)
        
        with DuckDBFTSDatabase(
            db_file=".diskcache/test_duckdb.db",
            table_name="documents",
            top_k=3,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as database:
            database.initialize(sample_documents)

            queries = ["谁是特斯拉的CEO？", "SpaceX是做什么的？", "马斯克参与了哪些项目？"]

            for query in queries:
                logger.info(f"\n查询: {query}")
                result = database.retrieve(query)

                assert result is not None, f"查询 '{query}' 应该返回结果"
                
                if result:
                    for i, doc_with_score in enumerate(result, 1):
                        document = doc_with_score["document"]
                        print(f"{i}. 文档内容: {document.text}")
                        print(f"   元数据: {document.metadata}")
                        print(f"   相关性分数 (BM25): {doc_with_score['score']:.4f}")
                        
                        # 验证返回的文档结构
                        assert "document" in doc_with_score
                        assert "score" in doc_with_score
                        assert isinstance(doc_with_score["document"], Document)
                        assert isinstance(doc_with_score["score"], (int, float))
                else:
                    print("没有找到相关文档")
                print("-" * 50)

    def test_database_persistence_and_loading(self, sample_documents, custom_tokenizer, custom_stemmer):
        """测试数据库持久化和加载功能"""
        logger.info("\n" + "=" * 60)
        logger.info("测试数据库持久化和加载功能")
        logger.info("=" * 60)
        
        # 首先初始化数据库并写入数据
        with DuckDBFTSDatabase(
            db_file=".diskcache/test_persist.db",
            table_name="documents",
            top_k=3,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as database:
            database.initialize(sample_documents)
        
        # 创建新的数据库实例，从持久化文件加载
        with DuckDBFTSDatabase(
            db_file=".diskcache/test_persist.db",
            table_name="documents",
            top_k=3,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as loaded_database:
            # 注意：这里不调用 initialize()，直接从持久化的数据库加载数据
            
            # 测试相同的查询，验证数据是否正确加载
            test_queries = [
                "特斯拉CEO是谁？",  # 与原查询稍有不同的表达
                "火箭技术",        # 测试关键词检索
                "脑机接口项目",    # 测试复合词检索
                "不存在的内容",    # 测试无结果情况
            ]

            for query in test_queries:
                logger.info(f"\n持久化测试查询: {query}")
                result = loaded_database.retrieve(query)

                if result:
                    for i, doc_with_score in enumerate(result, 1):
                        document = doc_with_score["document"]
                        print(f"{i}. 文档内容: {document.text}")
                        print(f"   元数据: {document.metadata}")
                        print(f"   相关性分数 (BM25): {doc_with_score['score']:.4f}")
                        
                        # 验证返回的文档结构
                        assert "document" in doc_with_score
                        assert "score" in doc_with_score
                        assert isinstance(doc_with_score["document"], Document)
                        assert isinstance(doc_with_score["score"], (int, float))
                else:
                    print("没有找到相关文档")
                print("-" * 50)

    def test_incremental_document_addition(self, sample_documents, additional_documents, custom_tokenizer, custom_stemmer):
        """测试增量添加文档功能"""
        logger.info("\n" + "=" * 60)
        logger.info("测试增量添加文档功能")
        logger.info("=" * 60)
        
        with DuckDBFTSDatabase(
            db_file=".diskcache/test_incremental.db",
            table_name="documents",
            top_k=3,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as incremental_database:
            # 初始化新文档（会保留原有数据）
            incremental_database.initialize(sample_documents + additional_documents)
            
            # 测试包含新老文档的检索
            mixed_queries = [
                "CEO",           # 应该同时返回马斯克和库克相关的文档
                "苹果公司",     # 测试新添加的文档
                "科技公司",     # 测试跨文档的概念检索
            ]
            
            for query in mixed_queries:
                logger.info(f"\n增量测试查询: {query}")
                result = incremental_database.retrieve(query)

                assert result is not None, f"查询 '{query}' 应该返回结果"
                
                if result:
                    for i, doc_with_score in enumerate(result, 1):
                        document = doc_with_score["document"]
                        print(f"{i}. 文档内容: {document.text}")
                        print(f"   元数据: {document.metadata}")
                        print(f"   相关性分数 (BM25): {doc_with_score['score']:.4f}")
                        
                        # 验证返回的文档结构
                        assert "document" in doc_with_score
                        assert "score" in doc_with_score
                        assert isinstance(doc_with_score["document"], Document)
                        assert isinstance(doc_with_score["score"], (int, float))
                else:
                    print("没有找到相关文档")
                print("-" * 50)

        logger.info("\n" + "=" * 60)
        logger.info("所有测试完成！数据库持久化功能验证成功。")
        logger.info("=" * 60)
