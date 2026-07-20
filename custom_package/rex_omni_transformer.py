# -*- coding: utf-8 -*-

from typing import List, Optional, Union

import torch
from rex_omni import RexOmniWrapper, RexOmniVisualize
from PIL import Image


class RexOmniTransformer:
    """transformers 使用 Rex-Omni 模型"""

    def __init__(self, model_path):
        self.model = RexOmniWrapper(
            model_path=model_path,
            backend="transformers",
            max_tokens=2048,
            temperature=0.0,
            top_p=0.05,
            top_k=1,
            repetition_penalty=1.05,
        )

    def detection_ui(self, image: Image, categories: list, task: str = "gui_grounding", visual_prompt_boxes: Optional[
            Union[List[List[float]], List[List[List[float]]]]] = None):
        """检测图片内的元素"""
        results = self.model.inference(images=image, task=task, categories=categories, visual_prompt_boxes=visual_prompt_boxes)
        result = results[0]
        if result["success"]:
            predictions = result["extracted_predictions"]
            raw_image_size = result["image_size"]
            resized_image_size = result["resized_size"]

            # visualize = RexOmniVisualize(
            #     image=image,
            #     predictions=predictions,
            #     font_size=20,
            #     draw_width=5,
            #     show_labels=True,
            # )
            # visualize.save("gui_detection.png")
            return self.process_predictions(predictions), raw_image_size, resized_image_size
        else:
            print(result["error"])

    def process_predictions(self, predictions: dict) -> dict:
        """处理 Rex-Omni 模型的预测结果"""
        results = {}
        for category, annotations in predictions.items():
            results[category] = []
            for i, annotation in enumerate(annotations):
                annotation_type = annotation.get("type", "box")
                coords = annotation.get("coords", [])

                if annotation_type == "box" and len(coords) == 4:
                    results[category].append(coords)

        return results


    def del_model(self):
        """删除模型, 清空缓存, 释放内存"""
        del self.model
        import gc
        gc.collect()
        torch.cuda.empty_cache()
        torch.cuda.synchronize()