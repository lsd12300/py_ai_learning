from ultralytics import YOLO
from PIL import Image
import json


OUTPUT_JSON_PATH = "D:/Projects/AI/背包按钮.json"


model = YOLO("D:/Projects/Learnings/python/AI/Hugface_Model/yolo-ui.pt")


def yolo_json_xyxy_offset(json_str: str, offsetX: float = 0, offsetY: float = 0):
    """
    解析YOLO JSON字符串, 将xyxy坐标偏移 offsetX, offsetY
    """
    try:
        datas = json.loads(json_str)
    except:
        import json5
        datas = json5.loads(json_str)
    for item in datas:
        item["box"]["x1"] += offsetX
        item["box"]["y1"] += offsetY
        item["box"]["x2"] += offsetX
        item["box"]["y2"] += offsetY
    return datas


# 分块解析
# Tiled inference (required — matches training)
img = Image.open("D:/Projects/AI/背包.png")
tile_size = 640
step = 512  # 20% overlap

all_results = []
for y in range(0, img.height, step):
    for x in range(0, img.width, step):
        tile = img.crop((x, y, min(x + tile_size, img.width), min(y + tile_size, img.height)))
        results = model(tile, imgsz=640, conf=0.25)
        # all_results.extend(results)
        print(x, y)

        # 还原原图坐标
        for result in results:
            json_item = yolo_json_xyxy_offset(result.to_json(), offsetX=x, offsetY=y)
            all_results.extend(json_item)

        # Translate detections back to full-image coordinates
        # for box in results[0].boxes:
        #     xyxy = box.xyxy[0].tolist()
        #     xyxy[0] += x; xyxy[1] += y; xyxy[2] += x; xyxy[3] += y
        #     print(xyxy)

with open(OUTPUT_JSON_PATH, "w", encoding="utf-8") as f:
    for result in all_results:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")
