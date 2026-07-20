MAX_NEW_TOKENS = 8192
TEMPERATURE = 0.1
TOP_P = 0.8

LLAMA_CPP_URL = "http://127.0.0.1:8080/v1"  # Llama-CPP 服务器地址
IMAGE_PATH = "D:/Projects/AI/01B.png"
JSON_PATH = "D:/Projects/AI/背包按钮.json"

STRUCTURE_PROMPT = """You are a professional game UI structure analysis expert. Your task is to extract and analyze the interface structure based on game screenshots.

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