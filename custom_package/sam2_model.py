# -*- coding: utf-8 -*-

from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor
import numpy as np
from PIL import Image


class SAM2Model:
    """SAM2 模型 分割"""

    def __init__(self, model_cfg: str, checkpoint_path: str):
        self.model = build_sam2(model_cfg, checkpoint_path, device="cuda")
        self.predictor = SAM2ImagePredictor(self.model)

    def predict_mask(self, image: Image, rex_omni_predictions: dict) -> np.ndarray:
        """对每个Rex-Omni检测到的元素，预测像素级Mask"""
        self.predictor.set_image(image)
        result_masks = []
        print(rex_omni_predictions)
        for category, coords in rex_omni_predictions.items():
            input_boxs = np.array(coords)
            masks, scores, _ = self.predictor.predict(
                point_coords=None,
                point_labels=None,
                box=input_boxs,
                multimask_output=False, # 只返回最佳Mask
            )
            result_masks.append(masks) # shape: (H, W)  二值Mask
        return result_masks
    

    def predict_mask2(self, image: Image, rex_omni_predictions: dict) -> np.ndarray:
        """对每个检测到的元素，预测像素级Mask"""
        self.predictor.set_image(image)
        rects = []
        print(rex_omni_predictions)
        for item in rex_omni_predictions:
            rects.append(item["bbox"])

        input_boxs = np.array(rects)
        masks, scores, _ = self.predictor.predict(
            point_coords=None,
            point_labels=None,
            box=input_boxs,
            multimask_output=False, # 只返回最佳Mask
        )

        return masks

    