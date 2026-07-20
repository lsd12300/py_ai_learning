# -*- coding: utf-8 -*-
# 使用 Rex-Omni 模型检测 UI效果图内的元素

# import torch
# from PIL import Image
# from rex_omni import RexOmniWrapper, RexOmniVisualize


# # 1. 初始化模型
# model = RexOmniWrapper(
#     model_path="D:/Projects/Learnings/python/AI/Hugface_Model/Rex-Omni",
#     backend="transformers",
#     max_tokens=2048,
#     temperature=0.0,
#     top_p=0.05,
#     top_k=1,
#     repetition_penalty=1.05,
#     do_sample=True,
# )

# # 2. 加载图片
# image = Image.open("D:/Projects/Gits/Rex-Omni/tutorials/detection_example/test_images/cafe.jpg").convert("RGB")
# categories = ["man", "woman", "cup", "laptop"]

# # 3. 执行检测
# results = model.inference(images=image, task="detection", categories=categories)

# # 4. 可视化结果
# visualize = RexOmniVisualize(
#     image=image,
#     predictions=results[0]["extracted_predictions"],
#     font_size=20,
#     draw_width=5,
#     show_labels=True,
# )
# visualize.save("cafe_detection.png")


from custom_package.rex_omni_transformer import RexOmniTransformer


MODEL_PATH = "D:/Projects/Learnings/python/AI/Hugface_Model/Rex-Omni"
IMAGE_PATH = "D:/Projects/AI/背包.png"


rex_omni_transformer = RexOmniTransformer(MODEL_PATH)

categories = ["按钮", "文本", "进度条", "滑块", "滚动视图", "开关", "图标", "头像", "技能框", "道具框", "血条", "魔法条", "关闭按钮", "返回按钮", "确认按钮", "输入框"]

predictions = rex_omni_transformer.detection_ui(IMAGE_PATH, categories)
# print(predictions)
