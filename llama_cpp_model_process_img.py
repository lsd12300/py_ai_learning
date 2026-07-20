# -*- coding: utf-8 -*-
# llama.cpp 本地运行模型 解析图片

import base64
import os
from llama_cpp.llama_chat_format import Qwen25VLChatHandler
from llama_cpp.llama_chat_format import Qwen3VLChatHandler
from custom_package.llama_cpp_model import LlamaCppModel
from llama_cpp import Llama


# ----------------- 核心配置 ------------------
GGUF_MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/UI-Venus-1.5-8B-Q5_K_M.gguf"
MMRP_MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/UI-Venus-1.5-8B-mmproj-BF16.gguf"
# GGUF_MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/UI-Venus-Ground-7B.Q5_K_M.gguf"
# MMRP_MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/UI-Venus-Ground-7B.mmproj-Q8_0.gguf"
# GGUF_MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/UI-TARS-1.5-7B-q4_k_m.gguf"
# MMRP_MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/UI-TARS-1.5-7B-q8_0.mmproj"
# GGUF_MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/Holo2-8B.Q4_K_M.gguf"
# MMRP_MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/Holo2-8B.mmproj-Q8_0.gguf"
# IMAGE_PATH = "D:/Projects/AI/背包.png"
IMAGE_PATH = "D:/Projects/AI/01B_背包_道具.png"
OUTPUT_JSON_PATH = "D:/Projects/AI/背包按钮.json"
# ---------------------------------------------




def image_to_data_url(path: str) -> str:
    """将图片转为 base64 数据 URI"""
    if not os.path.isfile(path):
        raise FileNotFoundError(f"图片不存在: {path}")
    with open(path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    ext = path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    return f"data:{mime};base64,{b64}"




# ========== 加载模型 ==========
chat_handler = Qwen25VLChatHandler(clip_model_path=MMRP_MODEL_PATH, verbose=False)
llm = Llama(
    model_path=GGUF_MODEL_PATH,
    chat_handler=chat_handler,
    n_ctx=4096,           # 上下文长度，根据需要调整
    n_threads=8,          # 线程数，根据需要调整
    n_gpu_layers=-1,      # 使用所有 GPU 层（需 CUDA 支持）
    verbose=False,        # 关闭详细日志
    flash_attn_type=1,    # 启用 flash attention
)

# ========== 构建提示 ==========
# UI-TARS 使用 <image> 占位符表示图像输入
prompt = """你是一个专业的UI界面助手。分析游戏截图, 给出详细界面结构, 仅输出UI元素相关的信息"""
# prompt = """你是一个专业的UI元素检测助手。请定位下图片中 '家园'按钮, 输出其矩形框区域bbox"""
# prompt = """请检测图片中所有可交互按钮, 以按钮的背景图片计算bbox, 以Json格式输出.
# '''json
# [
#     { "bbox":[x1,y1,x2,y2], "label":按钮上的文字, "score":置信度},
#     ...
# ]
# '''
# """

# ========== 调用模型 ==========
messages = [
    {
        "role": "user",
        "content": [
            {"type": "image_url", "image_url": {"url": image_to_data_url(IMAGE_PATH)}},
            {"type": "text", "text": prompt},
        ],
    }
]
response = llm.create_chat_completion(
    messages=messages,
    temperature=0.0,       # 低温度使输出更确定
    max_tokens=2048,
)

# 提取原始输出
output_text = response["choices"][0]["message"]["content"]
print("模型原始输出：")
print(output_text)