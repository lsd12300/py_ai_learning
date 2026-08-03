# -*- coding: utf-8 -*-
# llama-cpp 嵌入模型 测试


from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8080/v1",    # Llama-CPP 服务器地址
    api_key="abcd", # 随便填, 不会用到
)
result = client.embeddings.create(input="你是什么模型？", model="bge-m3")
print(result)