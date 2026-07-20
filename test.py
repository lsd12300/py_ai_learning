# import matplotlib
# print(matplotlib.get_backend())


# 路径
# import os
# IMAGE_PATH = "D:/Projects/AI/01B_背包_道具.png.jpg"
# a = os.path.basename(IMAGE_PATH) # 带后缀的文件名
# print(a)
# b = a.split(".")[0] # 不带后缀的文件名
# print(b)

# c = os.path.splitext(IMAGE_PATH)[0] # 不带后缀的文件路径
# print(c)
# d = os.path.splitext(IMAGE_PATH)[-1] # 后缀名
# print(d)


# 正则
import re
import json
# from transformers_process_img import PROMPT
# # 匹配```json和```之间的内容
# match = re.search(r"```json(.*?)```", PROMPT, re.DOTALL)
# print(match.group(1))
# for item in re.findall(r"```json(.*?)```", PROMPT, re.DOTALL):
#     print(item)

# s = "<ref>Title Bar</ref><box><0><3><1000><49></box><ref>Scroll View</ref><box><0><46><1000><1000></box><ref>Tool Bar</ref><box><435><758><969><817></box><ref>Main Navigation Bar</ref><box><0><919><994><1000></box><|im_end|>"
# for m in re.finditer(r"<ref>(.*?)</ref><box><(\d+)><(\d+)><(\d+)><(\d+)></box>", s):
#     title = m.group(1)
#     numbers = [int(m.group(i)) for i in range(2, 6)]
#     print(title, numbers)
s = """{"action": "answer", "content": "您好！我是一个智能助手，没有具体的个人名字。您可以叫我"智能助手"或根据您的需求称呼我。有什么我可以帮您的吗？"}"""
match = re.search(r'({.*?})', s, re.DOTALL)
print(match.group(1))
print(json.loads(match.group(1)))
