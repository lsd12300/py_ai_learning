# -*- coding: utf-8 -*-
# 使用 Rex-Omni + SAM2 模型检测 UI效果图内的元素


MODEL_PATH_REX_OMNI = "D:/Projects/Learnings/python/AI/Hugface_Model/Rex-Omni"
# IMAGE_PATH = "D:/Projects/AI/背包.png"
IMAGE_PATH = "D:/Projects/AI/01B_背包_道具.png"
SAM2_CHECKPOINT_PATH = "D:\Projects\Learnings\python\AI\Hugface_Model\sam2.1_hiera_large.pt"
SAM2_MODEL_CFG_PATH = "configs/sam2.1/sam2.1_hiera_l.yaml"
SAVE_JSON_PATH = "D:/Projects/AI/背包按钮.json"


from PIL import Image
image = Image.open(IMAGE_PATH).convert("RGB")


'''
# 1. Rex-Omni 定位元素
from custom_package.rex_omni_transformer import RexOmniTransformer
rex_omni_transformer = RexOmniTransformer(MODEL_PATH_REX_OMNI)
# categories = ["按钮", "文本", "进度条", "滑块", "滚动视图", "图标", "头像", "道具框", "输入框"]
categories = ["按钮", "标签按钮"]
# visual_prompt_boxes = [[40, 1317, 220, 1400]]
predictions, raw_image_size, resized_image_size = rex_omni_transformer.detection_ui(image, categories, task="detection")
# print(predictions)

if predictions is None:
    import sys
    sys.exit(1)

# 保存 JSON 文件
import json
with open(SAVE_JSON_PATH, "w", encoding="utf-8") as f:
    json.dump(predictions, f, ensure_ascii=False, indent=4)

# 切割图片
from cut_image import cut_image
cut_image(SAVE_JSON_PATH)


# 删除模型, 释放内存
rex_omni_transformer.del_model()
'''


import json
with open(SAVE_JSON_PATH, "r", encoding="utf-8") as f:
    txt = f.read()
    datas = json.loads(txt)
    predictions = datas

    for item in datas:
        rect = item["bbox"]
        rect[0] = rect[0] / 1000 * image.width
        rect[1] = rect[1] / 1000 * image.height
        rect[2] = rect[2] / 1000 * image.width
        rect[3] = rect[3] / 1000 * image.height


# 2. SAM2 精细分割---获取像素级Mask
from custom_package.sam2_model import SAM2Model
sam2_model = SAM2Model(SAM2_MODEL_CFG_PATH, SAM2_CHECKPOINT_PATH)
masks = sam2_model.predict_mask2(image, predictions)


import numpy as np
import matplotlib.pyplot as plt

def show_mask(mask, ax, random_color=False, borders = True):
    if random_color:
        color = np.concatenate([np.random.random(3), np.array([0.6])], axis=0)
    else:
        color = np.array([30/255, 144/255, 255/255, 0.6])
    h, w = mask.shape[-2:]
    mask = mask.astype(np.uint8)
    mask_image =  mask.reshape(h, w, 1) * color.reshape(1, 1, -1)
    if borders:
        import cv2
        contours, _ = cv2.findContours(mask,cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE) 
        # Try to smooth contours
        contours = [cv2.approxPolyDP(contour, epsilon=0.01, closed=True) for contour in contours]
        mask_image = cv2.drawContours(mask_image, contours, -1, (1, 1, 1, 0.5), thickness=2) 
    ax.imshow(mask_image)

def show_box(box, ax):
    x0, y0 = box[0], box[1]
    w, h = box[2] - box[0], box[3] - box[1]
    ax.add_patch(plt.Rectangle((x0, y0), w, h, edgecolor='green', facecolor=(0, 0, 0, 0), lw=2)) 


plt.figure(figsize=(10, 10))
plt.imshow(image)
for mask in masks:
    show_mask(mask.squeeze(0), plt.gca(), random_color=True)
# for box in input_boxes:
#     show_box(box, plt.gca())
plt.axis('off')
# plt.show()
plt.savefig("plt.png")   # 保存图片

