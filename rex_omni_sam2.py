# -*- coding: utf-8 -*-


from typing import Dict, List, Tuple

import matplotlib.pyplot as plt
import numpy as np
import torch
from PIL import Image

from rex_omni import RexOmniVisualize, RexOmniWrapper
from sam2.build_sam import build_sam2
from sam2.sam2_image_predictor import SAM2ImagePredictor


MODEL_PATH_REX_OMNI = "D:/Projects/Learnings/python/AI/Hugface_Model/Rex-Omni"
# IMAGE_PATH = "D:/Projects/AI/背包.png"
IMAGE_PATH = "D:/Projects/AI/01B_背包_道具.png"
SAM2_CHECKPOINT_PATH = "D:\Projects\Learnings\python\AI\Hugface_Model\sam2.1_hiera_large.pt"
SAM2_MODEL_CFG_PATH = "configs/sam2.1/sam2.1_hiera_l.yaml"
SAVE_JSON_PATH = "D:/Projects/AI/背包按钮.json"
SAVE_VISUALIZATION_PATH = "D:/Projects/AI/背包按钮可视化.jpg"



def setup_sam2_model(model_path: str, checkpoint_path: str):
    """初始化 SAM2 模型"""
    sam2_model = build_sam2(model_path, checkpoint_path, device="cuda")
    sam2_predictor = SAM2ImagePredictor(sam2_model)
    return sam2_predictor


def setup_rexo_omni_model(model_path: str):
    """初始化 RexoOmni 模型"""
    rex_model = RexOmniWrapper(
        model_path=model_path,
        backend="transformers",
        max_tokens=2048,
        temperature=0.0,
        top_p=0.05,
        top_k=1,
        repetition_penalty=1.05,
    )
    return rex_model

def detect_objects_with_rex(
    rex_model: RexOmniWrapper,
    image: Image.Image,
    categories: List[str],
    task: str = "detection",
) -> Dict:
    """使用 RexoOmni 模型检测图片中的对象"""
    results = rex_model.inference(images=image, categories=categories, task=task)
    result = results[0]
    if not result["success"]:
        raise RuntimeError(
            f"Rex-Omni inference failed: {result.get('error', 'Unknown error')}"
        )

    return result

def extract_boxes_from_predictions(predictions: Dict) -> List[np.ndarray]:
    """从 RexoOmni 模型检测结果中提取矩形框"""
    boxes = []
    for category, detections in predictions.items():
        for detection in detections:
            if detection["type"] == "box":
                coords = detection["coords"]
                # Ensure format is [x1, y1, x2, y2]
                box = np.array([coords[0], coords[1], coords[2], coords[3]])
                boxes.append(box)

    return boxes

def generate_masks_with_sam(
    sam_predictor, image: np.ndarray, boxes: List[np.ndarray]
) -> Tuple[List[np.ndarray], List[float]]:
    """使用 SAM2 模型生成矩形框内的掩码"""
    # Set image for SAM
    sam_predictor.set_image(image)

    all_masks = []
    all_scores = []

    for box in boxes:
        # SAM expects boxes in [x1, y1, x2, y2] format
        masks, scores, _ = sam_predictor.predict(
            box=box, multimask_output=False  # Get single best mask
        )

        all_masks.append(masks[0])  # Take the first (best) mask
        all_scores.append(scores[0])

    return all_masks, all_scores


def visualize_results(
    image: Image.Image,
    predictions: Dict,
    masks: List[np.ndarray] = None,
    save_path: str = "output_visualization.jpg",
):
    """可视化保存 检测结果和掩码"""
    fig, axes = plt.subplots(1, 2 if masks is not None else 1, figsize=(20, 10))

    if masks is None:
        axes = [axes]

    # Left: Rex-Omni detection with boxes
    rex_vis = RexOmniVisualize(
        image=image,
        predictions=predictions,
        font_size=20,
        draw_width=5,
        show_labels=True,
    )
    axes[0].imshow(rex_vis)
    axes[0].set_title("Rex-Omni Detection (Bounding Boxes)", fontsize=16)
    axes[0].axis("off")

    # Right: SAM segmentation with masks
    if masks is not None:
        img_array = np.array(image)

        # Create colored mask overlay
        mask_overlay = np.zeros_like(img_array)
        colors = plt.cm.rainbow(np.linspace(0, 1, len(masks)))

        for mask, color in zip(masks, colors):
            mask_rgb = (mask[:, :, None] * color[:3] * 255).astype(np.uint8)
            mask_overlay = np.where(mask[:, :, None], mask_rgb, mask_overlay)

        # Blend original image with mask overlay
        alpha = 0.5
        blended = (alpha * img_array + (1 - alpha) * mask_overlay).astype(np.uint8)

        # Convert to PIL Image for drawing boxes and labels
        from PIL import ImageDraw, ImageFont

        blended_pil = Image.fromarray(blended)
        draw = ImageDraw.Draw(blended_pil)

        # Try to use a truetype font, fallback to default if not available
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20
            )
        except:
            font = ImageFont.load_default()

        # Draw boxes and labels for each detection
        mask_idx = 0
        for category, detections in predictions.items():
            for detection in detections:
                if detection["type"] == "box" and mask_idx < len(masks):
                    coords = detection["coords"]
                    x1, y1, x2, y2 = coords[0], coords[1], coords[2], coords[3]

                    # Get corresponding color
                    color = colors[mask_idx]
                    color_rgb = tuple((color[:3] * 255).astype(int).tolist())

                    # Draw bounding box
                    draw.rectangle([x1, y1, x2, y2], outline=color_rgb, width=5)

                    # Draw label background
                    label_text = category
                    bbox = draw.textbbox((x1, y1 - 25), label_text, font=font)
                    draw.rectangle(bbox, fill=color_rgb)

                    # Draw label text
                    draw.text(
                        (x1, y1 - 25), label_text, fill=(255, 255, 255), font=font
                    )

                    mask_idx += 1

        axes[1].imshow(blended_pil)
        axes[1].set_title("SAM Segmentation (Masks + Boxes + Labels)", fontsize=16)
        axes[1].axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=150, bbox_inches="tight")
    print(f"💾 Visualization saved to: {save_path}")
    plt.close()



def rex_omni_sam2_pipeline(
    image_path: str,
    categories: List[str],
    rex_model_path: str = MODEL_PATH_REX_OMNI,
    sam2_model_path: str = SAM2_MODEL_CFG_PATH,
    sam2_checkpoint_path: str = SAM2_CHECKPOINT_PATH,
    save_visualization_path: str = SAVE_VISUALIZATION_PATH,
):
    """RexoOmni 模型 + SAM2 模型 管线"""

    # 1. 加载图片
    image = Image.open(image_path).convert("RGB")
    img_array = np.array(image)


    # 2. 检测对象
    rex_model = setup_rexo_omni_model(rex_model_path)
    result = detect_objects_with_rex(rex_model, image, categories)
    predictions = result["extracted_predictions"]
    print(predictions)

    # 3. 提取矩形框
    boxes = extract_boxes_from_predictions(predictions)

    # 4. 销毁模型, 释放内存
    del rex_model
    import gc
    gc.collect()
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

    # 5. 生成掩码
    sam2_predictor = setup_sam2_model(sam2_model_path, sam2_checkpoint_path)
    masks, scores = generate_masks_with_sam(sam2_predictor, img_array, boxes)

    # 6. 可视化结果
    if save_visualization_path:
        visualize_results(image, predictions, masks, save_visualization_path)

    return {
        "predictions": predictions,
        "masks": masks,
        "scores": scores,
        "boxes": boxes,
    }



if __name__ == "__main__":
    rex_omni_sam2_pipeline(
        image_path=IMAGE_PATH,
        categories=["按钮", "标题", "底部标签页"],
    )