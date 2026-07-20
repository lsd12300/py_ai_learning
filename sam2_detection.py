# -*- coding: utf-8 -*-
# 使用 SAM2 模型检测 UI效果图内的元素


SAM2_CHECKPOINT_PATH = "D:\Projects\Learnings\python\AI\Hugface_Model\sam2.1_hiera_large.pt"
SAM2_MODEL_CFG_PATH = "configs/sam2.1/sam2.1_hiera_l.yaml"


from custom_package.sam2_model import SAM2Model
sam2_model = SAM2Model(SAM2_MODEL_CFG_PATH, SAM2_CHECKPOINT_PATH)
# masks = sam2_model.predict_mask(image, predictions)