# -*- coding: utf-8 -*-
# 测试 Mem0库


from mem0 import Memory
# from mem0.vector_stores import chroma

config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "qwen3.5-9b",
            "temperature": 0.8,
            "openai_base_url": "http://127.0.0.1:8080/v1",
            "api_key": "abc",
            "max_tokens": 4096,
            "top_p": 0.95,
            "top_k": 40,
            # "enable_vision": config.enable_vision,
            # "vision_details": config.vision_details,
            # "http_client_proxies": config.http_client_proxies,
        }
    },
    "vector_store": {
        "provider": "chroma",
        "config": {
            "collection_name": "test_collection"
        }
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "qwen3.5-9b",
            "api_key": "abc",
            "embedding_dims": 1536,
            # "ollama_base_url": "http://127.0.0.1:8080/v1",
            "openai_base_url": "http://127.0.0.1:8080/v1",
        }
    }
}


from qdrant_client import QdrantClient
