#!/usr/bin/env python3
"""
比较 DuckDB FTS 和 SQLite FTS 实现的测试脚本
"""

import logging
import os
import sys

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from wujing.rag.internal.fts.duckdb_fts import DuckDBFTSDatabase
from wujing.rag.internal.fts.sqlite_fts import SQLiteFTSDatabase, Document
from wujing.rag.tokenizer import ChineseTokenizer
from wujing.rag.stemmer import MixedLanguageStemmer


def setup_logging():
    """设置日志"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def create_test_documents():
    """创建测试文档"""
    return [
        Document("马斯克是特斯拉的首席执行官，该公司是电动汽车领域的领导者。", {"topic": "Tesla", "person": "马斯克"}),
        Document("他也是 SpaceX 的创始人和首席执行官，这是一家致力于太空探索的公司。", {"topic": "SpaceX", "person": "马斯克"}),
        Document("此外，马斯克还参与了 Neuralink 和 The Boring Company 等项目。", {"topic": "其他项目", "person": "马斯克"}),
        Document("特斯拉不仅生产电动汽车，还涉足太阳能和储能解决方案。", {"topic": "Tesla", "business": "能源"}),
        Document("SpaceX 成功实现了火箭的可重复使用，大大降低了发射成本。", {"topic": "SpaceX", "technology": "火箭"}),
        Document("Neuralink 致力于开发脑机接口技术，可能革命性地改变医疗行业。", {"topic": "Neuralink", "technology": "脑机接口"}),
    ]


def test_database_implementation(db_class, db_file, db_name):
    """测试数据库实现"""
    print(f"\n{'='*50}")
    print(f"测试 {db_name}")
    print(f"{'='*50}")
    
    documents = create_test_documents()
    custom_tokenizer = ChineseTokenizer(min_token_length=2)
    custom_stemmer = MixedLanguageStemmer(algorithm="porter", min_word_length=2)
    
    with db_class(
        db_file=db_file,
        table_name="documents",
        top_k=3,
        tokenizer=custom_tokenizer,
        stemmer=custom_stemmer,
        use_stemming=True,
    ) as database:
        database.initialize(documents)
        
        queries = ["谁是特斯拉的CEO？", "SpaceX是做什么的？", "马斯克参与了哪些项目？"]
        
        results = {}
        for query in queries:
            print(f"\n查询: {query}")
            result = database.retrieve(query)
            results[query] = result
            
            if result:
                for i, doc_with_score in enumerate(result, 1):
                    document = doc_with_score["document"]
                    print(f"{i}. 文档内容: {document.text}")
                    print(f"   元数据: {document.metadata}")
                    print(f"   相关性分数 (BM25): {doc_with_score['score']:.4f}")
            else:
                print("没有找到相关文档")
            print("-" * 30)
    
    return results


def compare_results(duckdb_results, sqlite_results):
    """比较两个实现的结果"""
    print(f"\n{'='*50}")
    print("结果比较")
    print(f"{'='*50}")
    
    for query in duckdb_results.keys():
        print(f"\n查询: {query}")
        
        duckdb_docs = [r["document"].text for r in duckdb_results[query]]
        sqlite_docs = [r["document"].text for r in sqlite_results[query]]
        
        print(f"DuckDB 返回 {len(duckdb_docs)} 个结果")
        print(f"SQLite 返回 {len(sqlite_docs)} 个结果")
        
        # 检查是否包含相同的文档（不考虑顺序）
        duckdb_set = set(duckdb_docs)
        sqlite_set = set(sqlite_docs)
        
        intersection = duckdb_set & sqlite_set
        duckdb_only = duckdb_set - sqlite_set
        sqlite_only = sqlite_set - duckdb_set
        
        print(f"共同结果: {len(intersection)} 个")
        if duckdb_only:
            print(f"仅 DuckDB 有: {len(duckdb_only)} 个")
        if sqlite_only:
            print(f"仅 SQLite 有: {len(sqlite_only)} 个")
        
        if len(intersection) == len(duckdb_docs) == len(sqlite_docs):
            print("✅ 结果完全一致")
        else:
            print("⚠️  结果存在差异")


def main():
    """主函数"""
    setup_logging()
    
    print("比较 DuckDB FTS 和 SQLite FTS 实现")
    
    # 确保缓存目录存在
    os.makedirs(".diskcache", exist_ok=True)
    
    # 测试 DuckDB FTS
    duckdb_results = test_database_implementation(
        DuckDBFTSDatabase,
        ".diskcache/compare_duckdb.db",
        "DuckDB FTS"
    )
    
    # 测试 SQLite FTS
    sqlite_results = test_database_implementation(
        SQLiteFTSDatabase,
        ".diskcache/compare_sqlite.db",
        "SQLite FTS"
    )
    
    # 比较结果
    compare_results(duckdb_results, sqlite_results)
    
    print(f"\n{'='*50}")
    print("测试完成！")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
