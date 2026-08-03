# from custom_package.holo2_transformer import Holo2Transformer
# from custom_package.locate_anything_worker import LocateAnythingWorker
import torch
from transformers import (
    AutoProcessor,
    AutoModelForMultimodalLM,
    BitsAndBytesConfig
)

from PIL import Image
import torch

import os
from custom_package.utils import re_match_json


# MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/Holol2-4B"
# MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/LocateAnything-3B"
MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/Qwen3.5-4B"
# IMAGE_PATH = "D:/Projects/AI/背包.png"
IMAGE_PATH = "D:/Projects/AI/01B.png"

USE_4BIT = False
DEVICE = "cuda"
MAX_NEW_TOKENS = 8192
TEMPERATURE = 0.1
TOP_P = 0.8
PROMPT = """You are a professional game UI structure analysis expert. Your task is to extract and analyze the interface structure based on game screenshots.

Identify all visible UI elements, output its type ("Title Bar", "Scroll View", "Scroll Item", "Grid View", "Grid Item", "Tool Bar", "Main Navigation Bar", "Text", "Button", "Icon").
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


def load_model(model_path):
    """加载模型"""
    config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_use_double_quant=True,
        bnb_4bit_quant_type="nf4",
    ) if USE_4BIT else None
    processor = AutoProcessor.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForMultimodalLM.from_pretrained(
        model_path,
        quantization_config=config,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        device_map=DEVICE,
    )
    return processor, model


def process_image(model, processor, image_path: str) -> dict:
    """处理图片"""
    image = Image.open(image_path).convert("RGB")
    orig_width, orig_height = image.size

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": PROMPT},
            ],
        }
    ]

    text = processor.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    inputs = processor(
        text=[text],
        images=[image],
        padding=True,
        return_tensors="pt",
    )

    generated_ids = model.generate(
        **inputs.to(model.device),
        max_new_tokens=MAX_NEW_TOKENS,
        temperature=TEMPERATURE,
        top_p=TOP_P,
        do_sample=True,
        pad_token_id=processor.tokenizer.pad_token_id,
    )

    generated_ids_trimmed = [
        out_ids[len(in_ids):]
        for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
    ]

    output_text = processor.batch_decode(
        generated_ids_trimmed,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    )[0]

    return output_text



if __name__ == "__main__":
    processor, model = load_model(MODEL_PATH)
    print(f"加载模型结束, 开始处理图片")
    output_text = process_image(model, processor, IMAGE_PATH)

    # 提取json字符串, 保存
    json_str = re_match_json(output_text)
    with open(f"{os.path.splitext(IMAGE_PATH)[0]}_structure.json", "w") as f:
        f.write(json_str)

