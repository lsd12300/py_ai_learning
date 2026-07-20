# -*- coding: utf-8 -*-

from PIL import Image
import json
from pathlib import Path


def del_pre_gen_images():
    for file in Path("D:/Projects/AI").iterdir():
        if file.is_file() and file.name.startswith("背包按钮_"):
            file.unlink()


def cut_image(json_path):
    del_pre_gen_images()
    with open(json_path, "r", encoding="utf-8") as f:
        txt = f.read()
        txt = txt.replace("'", "\"")
        datas = json.loads(txt)

    # img = Image.open("D:/Projects/AI/背包.png")
    img = Image.open("D:/Projects/AI/01B.png")
    index = 0

    if type(datas) == list:
        for item in datas:
            rect = item["bbox"]
            rect[0] = rect[0] / 1000 * img.width
            rect[1] = rect[1] / 1000 * img.height
            rect[2] = rect[2] / 1000 * img.width
            rect[3] = rect[3] / 1000 * img.height
            print(rect)
            tile = img.crop(tuple(rect))
            tile.save(f"D:/Projects/AI/背包按钮_{index}.png")
            index += 1
    # elif type(datas) == dict:
    #     rect = datas["bbox"]
    #     tile = img.crop(tuple(rect))
    #     tile.save(f"D:/Projects/AI/背包按钮_{index}.png")
    #     index += 1


    # for category, rects in datas.items():
    #     for rect in rects:
    #         tile = img.crop(tuple(rect))
    #         tile.save(f"D:/Projects/AI/背包按钮_{index}.png")
    #         index += 1


if __name__ == "__main__":
    cut_image("D:/Projects/AI/背包按钮.json")