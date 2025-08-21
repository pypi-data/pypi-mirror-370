import logging
import pytest

from wujing.rag.internal.fts.base_fts import Document
from wujing.rag.internal.fts.sqlite_fts import SQLiteFTSDatabase
from wujing.rag.tokenizer import ChineseTokenizer
from wujing.rag.stemmer import MixedLanguageStemmer

logger = logging.getLogger(__name__)


class TestSQLiteFTSDatabase:
    """测试 SQLiteFTSDatabase 类"""

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
        
        with SQLiteFTSDatabase(
            db_file=".diskcache/test_sqlite.db",
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
        with SQLiteFTSDatabase(
            db_file=".diskcache/test_sqlite_persist.db",
            table_name="documents",
            top_k=2,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as database:
            database.initialize(sample_documents)
            
            # 执行一次查询验证数据已写入
            result = database.retrieve("特斯拉")
            assert len(result) > 0, "初始化后应该能查询到数据"
            logger.info(f"初始化后查询到 {len(result)} 个文档")

        # 重新打开数据库，验证数据持久化
        with SQLiteFTSDatabase(
            db_file=".diskcache/test_sqlite_persist.db",
            table_name="documents",
            top_k=2,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as database:
            # 直接查询，不重新初始化
            result = database.retrieve("特斯拉")
            assert len(result) > 0, "重新打开数据库后应该能查询到持久化的数据"
            logger.info(f"重新打开后查询到 {len(result)} 个文档")
            
            for i, doc_with_score in enumerate(result, 1):
                document = doc_with_score["document"]
                print(f"{i}. 文档内容: {document.text}")
                print(f"   元数据: {document.metadata}")
                print(f"   相关性分数 (BM25): {doc_with_score['score']:.4f}")

    def test_incremental_addition(self, sample_documents, additional_documents, custom_tokenizer, custom_stemmer):
        """测试增量添加文档功能"""
        logger.info("\n" + "=" * 60)
        logger.info("测试增量添加文档功能")
        logger.info("=" * 60)
        
        with SQLiteFTSDatabase(
            db_file=".diskcache/test_sqlite_incremental.db",
            table_name="documents",
            top_k=5,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as database:
            # 初始化基础文档
            database.initialize(sample_documents)
            initial_result = database.retrieve("公司")
            initial_count = len(initial_result)
            logger.info(f"初始文档数量，查询'公司'得到 {initial_count} 个结果")

            # 增量添加文档 - 使用 initialize 方法添加所有文档
            database.initialize(sample_documents + additional_documents)
            
            # 验证新文档已添加
            updated_result = database.retrieve("公司")
            updated_count = len(updated_result)
            logger.info(f"添加文档后，查询'公司'得到 {updated_count} 个结果")
            
            # 应该能找到更多相关文档
            assert updated_count >= initial_count, "添加文档后应该能找到更多相关结果"
            
            # 验证能查询到新添加的苹果相关内容
            apple_result = database.retrieve("苹果")
            assert len(apple_result) > 0, "应该能查询到新添加的苹果相关文档"
            logger.info(f"查询'苹果'得到 {len(apple_result)} 个结果")
            
            for i, doc_with_score in enumerate(apple_result, 1):
                document = doc_with_score["document"]
                print(f"{i}. 文档内容: {document.text}")
                print(f"   元数据: {document.metadata}")
                print(f"   相关性分数 (BM25): {doc_with_score['score']:.4f}")

    def test_query_variations(self, sample_documents, custom_tokenizer, custom_stemmer):
        """测试不同类型的查询"""
        logger.info("\n" + "=" * 60)
        logger.info("测试不同类型的查询")
        logger.info("=" * 60)
        
        with SQLiteFTSDatabase(
            db_file=".diskcache/test_sqlite_queries.db",
            table_name="documents",
            top_k=3,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as database:
            database.initialize(sample_documents)

            # 测试不同类型的查询
            test_queries = [
                ("单词查询", "特斯拉"),
                ("人名查询", "马斯克"),
                ("公司查询", "SpaceX"),
                ("技术查询", "电动汽车"),
                ("多词查询", "首席执行官"),
                ("技术术语", "脑机接口"),
            ]

            for query_type, query in test_queries:
                logger.info(f"\n{query_type}: {query}")
                result = database.retrieve(query)
                
                if result:
                    print(f"找到 {len(result)} 个相关文档:")
                    for i, doc_with_score in enumerate(result, 1):
                        document = doc_with_score["document"]
                        print(f"  {i}. {document.text[:50]}...")
                        print(f"     分数: {doc_with_score['score']:.4f}")
                else:
                    print("未找到相关文档")

    def test_empty_query_handling(self, sample_documents, custom_tokenizer, custom_stemmer):
        """测试空查询和边界情况处理"""
        logger.info("\n" + "=" * 60)
        logger.info("测试空查询和边界情况处理")
        logger.info("=" * 60)
        
        with SQLiteFTSDatabase(
            db_file=".diskcache/test_sqlite_edge_cases.db",
            table_name="documents",
            top_k=3,
            tokenizer=custom_tokenizer,
            stemmer=custom_stemmer,
            use_stemming=True,
        ) as database:
            database.initialize(sample_documents)

            # 测试边界情况
            edge_cases = [
                ("空字符串", ""),
                ("只有空格", "   "),
                ("不存在的词", "不存在的内容xyz"),
                ("标点符号", "。，！？"),
                ("数字", "12345"),
            ]

            for case_name, query in edge_cases:
                logger.info(f"\n测试 {case_name}: '{query}'")
                result = database.retrieve(query)
                
                if result:
                    print(f"意外找到 {len(result)} 个结果")
                    for doc_with_score in result:
                        print(f"  - {doc_with_score['document'].text[:30]}...")
                else:
                    print("正确处理：未找到结果")
