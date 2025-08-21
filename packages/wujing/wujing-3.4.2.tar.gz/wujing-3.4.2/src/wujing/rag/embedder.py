import rich
import uuid
import chromadb
from chromadb.utils import embedding_functions
from pathlib import Path
from typing import List, Dict, Optional, Any
from chromadb.config import Settings
import numpy as np


class Embedder:
    def __init__(
        self,
        persist_directory: str = ".diskcache/chroma",
        embedding_model: str = "BAAI/bge-m3",
        device: str = "cuda",
        reset_db: bool = False,
    ):
        self.embedding_model = embedding_model
        self.device = device

        self.db_dir = Path(persist_directory).absolute()

        self.client = chromadb.PersistentClient(
            path=self.db_dir.as_posix(),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

        if reset_db:
            self.client.reset()

        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model,
            device=self.device,
        )

    def upsert(self, collection_name: str, documents: List[str], metadata: Optional[List[Dict]] = None) -> List[str]:
        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
        )

        ids = [str(uuid.uuid4()) for _ in documents]

        collection.upsert(
            documents=documents,
            metadatas=metadata,
            ids=ids,
        )
        return ids

    def query(
        self,
        collection_name: str,
        query_texts: List[str],
        n_results: int = 5,
        include: List[str] = ["documents", "metadatas", "distances"],
    ) -> Dict:
        collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=self.embedding_function,
        )

        query_result = collection.query(
            query_texts=query_texts,
            n_results=n_results,
            include=include,
        )
        return self._add_similarity_probabilities(query_result=query_result)

    def _add_similarity_probabilities(self, query_result: Dict[str, Any]) -> Dict[str, Any]:
        if "distances" not in query_result or not query_result["distances"]:
            return query_result

        # 处理每个查询的距离列表
        all_similarities = []
        all_probabilities = []

        for distance_list in query_result["distances"]:
            distances = np.array(distance_list)
            similarities = np.exp(-distances)

            # 计算 softmax 概率
            exp_scores = np.exp(similarities - np.max(similarities))
            probabilities = exp_scores / exp_scores.sum()

            # 转换为百分比形式
            percentages = [f"{prob * 100:.1f}%" for prob in probabilities]

            all_similarities.append(similarities.tolist())
            all_probabilities.append(percentages)

        # 添加到结果中
        query_result["similarities"] = all_similarities
        query_result["probabilities"] = all_probabilities

        return query_result

    def reset_collection(self, collection_name: str):
        self.client.delete_collection(name=collection_name)

    def get_embeddings(self, collection_name: str):
        collection = self.client.get_collection(name=collection_name)
        return collection.get(include=["embeddings"])["embeddings"]


if __name__ == "__main__":
    embedder = Embedder(
        embedding_model="./../../../models/BAAI/bge-m3",
        reset_db=True,
        persist_directory=".diskcache/chroma2",
    )
    embedder.upsert(
        "collection",
        [
            "A man is eating food.",
            "A man is eating a piece of bread.",
            "The girl is carrying a baby.",
            "A man is riding a horse.",
            "A woman is playing violin.",
            "Two men pushed carts through the woods.",
            "A man is riding a white horse on an enclosed ground.",
            "A monkey is playing drums.",
            "A cheetah is running behind its prey.",
            "The spaghetti's been eaten.",
            "A man is eating spaghetti.",
            "A man is drink water.",
            "You look so beautiful today",
            "You look a bit beautiful today",
            "تبدين جميلة اليوم",
            "أنت جميلة جدا اليوم",
        ],
    )
    rich.print(
        embedder.query(
            "collection",
            ["你今天好漂亮", "you look so beautiful today"],
            n_results=3,
        )
    )
