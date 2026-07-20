# -*- coding: utf-8 -*-
# 使用 OpenAI 库对接 Llama-CPP 服务器

import re
import base64
import os
import json
from openai import OpenAI
from PIL import Image
from custom_package.utils import encode_image_url, crop_images_from_json, delete_files_with_prefix
from custom_package.locate_anything_prompt import prompt_category, prompt_multi


LLAMA_CPP_URL = "http://127.0.0.1:8080/v1"  # Llama-CPP 服务器地址
IMAGE_PATH = "D:/Projects/AI/01B.png"
JSON_PATH = "D:/Projects/AI/01B_structure.json"



# 请求服务器
def request_server(client: OpenAI, prompt: str, img_url: str) -> str:
    """请求服务器, 返回服务器回复"""
    req = client.chat.completions.create(
        model="any",
        messages=[
            {"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": img_url}},
            {"type": "text", "text": prompt},
        ]}
        ],
        max_tokens=1024,
    )
    return req.choices[0].message.content


# 解析包围框
def parse_bbox(text: str) -> list:
    """解析包围框文本, 返回所有框的坐标"""
    # print(text)
    results = []

    # 1. 先提取所有 ref 内容 （非贪婪）
    ref_matches = list(re.finditer(r"<ref>(.*?)</ref>", text))
    for i, ref_match in enumerate(ref_matches):
        ref = ref_match.group(1)
        start = ref_match.end()   # 当前 ref 结束位置
        # 下一个 ref 的开始位置（若没有则到字符串末尾）
        end = ref_matches[i+1].start() if i+1 < len(ref_matches) else len(text)
        segment = text[start:end]   # 该 ref 对应的 box 区域

        # 2. 解析 box 区域.  返回的是 归一化的坐标 0-1000
        boxes = []
        for box in re.finditer(r'<box><(\d+)><(\d+)><(\d+)><(\d+)></box>', segment):
            boxes.append([int(x) for x in box.groups()])
        results.append({'ref': ref, 'bbox': boxes})
    return results

def crop_image(rect: list, image: Image.Image, save_path: str) -> None:
    rect[0] = rect[0] / 1000 * image.width
    rect[1] = rect[1] / 1000 * image.height
    rect[2] = rect[2] / 1000 * image.width
    rect[3] = rect[3] / 1000 * image.height
    tile = image.crop(tuple(rect))
    tile.save(save_path)




if __name__ == "__main__":
    img_url = encode_image_url(IMAGE_PATH)
    client = OpenAI(
        base_url=LLAMA_CPP_URL,    # Llama-CPP 服务器地址
        api_key="abcd", # 随便填, 不会用到
    )

    # 删除旧图片, 重新裁切
    img_path_no_ext = os.path.splitext(IMAGE_PATH)[0] # 不带后缀的文件路径
    img_name = os.path.basename(IMAGE_PATH) # 带后缀的文件名
    img_name_no_ext = img_name.split(".")[0] # 不带后缀的文件名
    delete_files_with_prefix(os.path.dirname(IMAGE_PATH), f"{img_name_no_ext}_crop_")

    raw_img = Image.open(IMAGE_PATH)

    # results = parse_bbox(request_server(client, prompt_category(["Title Bar", "Scroll View", "Tool Bar", "Main Navigation Bar"]), img_url))
    # results = parse_bbox(request_server(client, prompt_multi("Grid Item"), img_url))
    results = parse_bbox(request_server(client, prompt_multi("?"), img_url))
    print(results)
    for rect in results:
        ref = rect["ref"]
        bbox = rect["bbox"]
        for i, box in enumerate(bbox):
            # save_path = f"{img_path_no_ext}_crop_{ref}_{i}.png"
            save_path = f"{img_path_no_ext}_crop__{i}.png"
            crop_image(box, raw_img, save_path)

    # # 加载界面结构 json 文件
    # with open(JSON_PATH, "r", encoding="utf-8") as f:
    #     data = json.load(f)

    # for item in data:
    #     item_type = item["type"]
    #     if item_type != "Title Bar":
    #         continue

    #     prompt = f"Locate the {item_type}."
    #     rect = parse_bbox(request_server(client, prompt, img_url))
    #     print(rect)
    #     save_path = f"{img_path_no_ext}_crop_{item_type}.png"
    #     crop_image(rect, raw_img, save_path)

    #     if item["children"] is None: 
    #         continue
    #     item_img = Image.open(save_path)
    #     item_img_url = encode_image_url(save_path)
    #     for child in item["children"]:
    #         child_type = child["type"]
    #         if child.get("text", "None") != "None":
    #             child_rect = parse_bbox(request_server(client, f"Please locate the text referred as {child['text']}.", img_url))
    #         if child.get("icon", "None") != "None":
    #             child_rect = parse_bbox(request_server_category(client, [child["icon"]], img_url))

    #         # child_rect = parse_bbox(request_server_category(client, [child_type], item_img_url))
    #         if child_rect is None:
    #             continue
    #         print(child_rect)
    #         save_path = f"{img_path_no_ext}_crop_{item_type}_{child_type}.png"
    #         crop_image(child_rect, raw_img, save_path)


