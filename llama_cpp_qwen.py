# -*- coding: utf-8 -*-
# 使用 OpenAI 库对接 Llama-CPP 服务器

import re
import base64
import os
import json
from openai import OpenAI
from PIL import Image

from custom_package.utils import encode_image_url


LLAMA_CPP_URL = "http://127.0.0.1:8080/v1"  # Llama-CPP 服务器地址
IMAGE_PATH = "D:/Projects/AI/01B.png"
JSON_PATH = "D:/Projects/AI/01B_structure.json"
PROMPT = """You are a professional game UI structure analysis expert. Your task is to extract and analyze the interface structure based on game screenshots.

Identify all visible UI elements, output its type ("Title Bar", "Scroll View", "Scroll Item", "Grid Item", "Tool Bar", "Main Navigation Bar", "Text", "Button", "Icon").
Output in JSON format.
```json
[
    {
        "type": "Title Bar",
        "children": [
            {
                "type": "Text",
                "text": "背包",
            },
            {
                "type": "Button",
                "icon": "Question Mark",
            },
            {
                "type": "Icon",
                "icon": "Question Mark",
            },
        ]
    },
]
```
"""


img_url = encode_image_url(IMAGE_PATH)
client = OpenAI(
    base_url=LLAMA_CPP_URL,    # Llama-CPP 服务器地址
    api_key="abcd", # 随便填, 不会用到
)

req = client.chat.completions.create(
    model="any",
    messages=[
        {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img_url}},
            {"type": "text", "text": PROMPT},
        ]}
    ],
    max_tokens=8192,
)
print(req.choices[0].message.content)
