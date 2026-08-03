# -*- coding: utf-8 -*-
# qdrant 测试: 混合搜索 + 重排序


from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, models


embedding_model = "bge-m3"
embedding_url = "http://127.0.0.1:8080/v1"

collection_name = "hybrid_search"


client = QdrantClient(url=embedding_url, api_key="abc")
if client.collection_exists(collection_name):
    client.delete_collection(collection_name)


# 创建数据集合
client.create_collection(
    collection_name=collection_name,
    vectors_config={
        # 384维 稠密嵌入。 使用余弦计算距离（即 语义比较）
        "dense": VectorParams(
            size=384,
            distance=Distance.COSINE,
        ),
        # 96维 延迟交互嵌入，采用最大相似度比较器匹配多向量；仅用于重排序，而非ANN（Approximate Nearest Neighbor，近似最近邻）检索，所以禁用 HNSW 索引。
        "multi": VectorParams(
            size=96,
            distance=Distance.COSINE,
            multivector_config=models.MultiVectorConfig(
                comparator=models.MultiVectorComparator.MAX_SIM,
            ),
            hnsw_config=models.HnswConfigDiff(m=0),    # 禁用 HNSW 
        ),
    },
    # 稀疏嵌入，用于关键词检索。
    sparse_vectors_config={
        "sparse": models.SparseVectorParams(modifier=models.Modifier.IDF),
    }
)


