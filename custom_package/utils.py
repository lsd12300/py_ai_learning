# -*- coding: utf-8 -*-
# 工具函数脚本

import base64
import os
import json
from PIL import Image
import numpy as np
import re


# 加载图片, 并编码为 base64 数据 URI
def encode_image_url(image_path: str) -> str:
    """将图片转为 base64 数据 URI"""
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"图片不存在: {image_path}")
    with open(image_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode("utf-8")
    ext = image_path.rsplit(".", 1)[-1].lower()
    mime = "image/png" if ext == "png" else "image/jpeg" if ext in ("jpg", "jpeg") else "image/png"
    return f"data:{mime};base64,{b64}"
    

# 删除目录下, 以指定前缀开头的文件
def delete_files_with_prefix(dir_path: str, prefix: str):
    """删除目录下, 以指定前缀开头的文件"""
    for file in os.listdir(dir_path):
        if file.startswith(prefix):
            os.remove(os.path.join(dir_path, file))


# 读取文件中json数据, 按字段bbox 裁切图片
def crop_images_from_json(json_path: str, image_path: str):
    """从json文件中读取数据, 按bbox裁切图片"""
    raw_img = Image.open(image_path)
    with open(json_path, "r") as f:
        data = json.load(f)
    index = 0
    for item in data:
        rect = item["bbox"]
        rect[0] = rect[0] / 1000 * raw_img.width
        rect[1] = rect[1] / 1000 * raw_img.height
        rect[2] = rect[2] / 1000 * raw_img.width
        rect[3] = rect[3] / 1000 * raw_img.height
        print(rect)
        tile = raw_img.crop(tuple(rect))
        tile.save(f"{json_path[:-5]}_{index}.png")
        index += 1

# 将多个图片以水平方向合并为一个图片
def concat_images_h(images, padding = 10, align = "bottom"):
    """
    将多个图片以水平方向合并为一个图片, 保持原图大小

    :param images: 图片列表, 每个元素为 numpy 数组对象
    :param padding: 图片之间的间距, 默认 10 像素
    :param align: 图片对齐方式, ("bottom", "top", "center"), 默认 "bottom"
    """
    if not images:
        print("错误: 图片列表为空")
        return
    
    count = len(images)
    
    # 都转换为3通道图片
    import cv2
    for i in range(count):
        shape_len = len(images[i].shape)
        if shape_len == 2:    # 单通道图 转换为3通道.  灰度图
            images[i] = cv2.cvtColor(images[i], cv2.COLOR_GRAY2BGR)
    
    # 计算合并后的图片宽度和高度
    max_height = max(img.shape[0] for img in images)
    total_width = sum(img.shape[1] + padding for img in images) - padding

    # 创建合并后的图片
    concat_img = np.zeros((max_height, total_width, 3), dtype=np.uint8) # 3通道, 255 填充. 无透明通道
    x = 0
    for i in range(count):
        # 计算对齐位置
        h, w = images[i].shape[:2] # 图片高度和宽度
        if align == "bottom":
            y = 0
        elif align == "top":
            y = max_height - h
        elif align == "center":
            y = (max_height - h) // 2
        else:
            raise ValueError(f"未知对齐方式: {align}")
        
        # 写入图片数据
        concat_img[y:y+h, x:x+w] = images[i]
        x += w + padding
    return concat_img


# 正则匹配```json和```之间的内容
def re_match_json(prompt: str) -> str:
    """从提示中提取```json和```之间的内容"""
    match = re.search(r"```json(.*?)```", prompt, re.DOTALL)
    if match:
        return match.group(1)
    else:
        return None
