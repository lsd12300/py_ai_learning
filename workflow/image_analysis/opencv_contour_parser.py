# -*- coding: utf-8 -*-
# 使用 OpenCV 解析游戏界面元素轮廓
# 缺点:
#   1. 只能检测矩形轮廓
#   2. 不能检测文字
#   3. 元素分类不准确, 仅通过几何特征分类.  可结合AI模型 对每个元素区域进行分类.
#   4. 形态学滤波 可能会合并相邻同色元素
#   5. 阈值硬编码, 不同界面要根据实际情况调整.



import cv2
import numpy as np
import os


def parse_game_ui(image_path, bg_color_coords=None):
    # 读取图片, 转换为灰度图.
    img = cv2.imread(image_path)    # 打开图片 返回 numpy数组. 不支持中文路径
    h, w = img.shape[:2]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 1. 边缘检测 查找UI元素边界
    edges = cv2.Canny(gray, 30, 100)    # Canny边缘检测算法. 两个参数为阈值, 梯度小于30为非边缘, 大于100为边缘.
    kernel = np.ones((5, 5), np.uint8)  # 返回一个5x5的数组, 元素全为1.
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)  # 形态学滤波. 闭合运算, 对边缘做"膨胀->腐蚀", 过滤小黑孔, 把断裂的轮廓线连接起来

    # 2. 查找潜在的UI元素轮廓
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓. RETR_EXTERNAL: 只取最外层轮廓; CHAIN_APPROX_SIMPLE: 简单的轮廓近似, 只返回轮廓的边界点.

    # 背景图检测
    # if bg_color_coords is not None:
    #     bg_contour = find_bg(img, bg_color_coords)
    #     contours = contours.__add__((bg_contour,))  # 修改 元组


    # 3. 根据轮廓计算AABB包围盒
    elements = []
    for i, cnt in enumerate(contours):
        x, y, bw, bh = cv2.boundingRect(cnt)    # 将任意形状的轮廓转换为矩形框.
        area = bw * bh
        # 元素面积<500 认为噪点.  元素面积>95%屏幕面积 认为全屏背景.
        # if area < 500 or area > w * h * 0.95:
        if area < 500 or area > w * h * 0.98:
            continue
        element = {
            "id": i + 1,
            "bbox": [int(x), int(y), int(x + bw), int(y + bh)],
            "size": [int(bw), int(bh)],
        }
        elements.append(element)

    # 4. 通过包含关系构建层级结构
    elements.sort(key=lambda e: (e["bbox"][1], e["bbox"][0]))    # 升序排序, 先 y 后 x
    for e in elements:
        e["children"] = []
        e["text"] = None
    root = {"elements": []}
    for e in elements:
        parent = find_parent(e, elements)
        if parent:
            parent["children"].append(e)
        else:
            root["elements"].append(e)

    root["screen_size"] = [w, h]
    return root, closed, edges

def find_area(cv_image, color, range=10, kernel_size=5):
    """
    查找 与指定颜色相近的区域
    :param cv_image: opencv 图像, numpy数组, 形状为 (v, h, 3)
    :param color: 目标颜色
    :param range: 颜色范围阈值, 用于确定相似度
    :param kernel_size: 形态学操作的核大小, 用于填充孔洞.  类似卷积, 值越大细节越少 (即 接近全白矩形)
    :return: 包含所有相似区域的轮廓列表
    """

    lower = np.array([max(0, c - range) for c in color])  # 颜色值每个通道 上下范围
    upper = np.array([min(255, c + range) for c in color])
    mask = cv2.inRange(cv_image, lower, upper)

    # 闭运算 填充 UI元素孔洞
    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 50))  # 50x50的区域, 元素全为1.
    kernel = np.ones((kernel_size, kernel_size), np.uint8)  # 返回一个kernel_sizexkernel_size的数组, 元素全为1.
    closed = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # 找最大的轮廓 作为背景图
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    # bg_contour = max(bg_contours, key=cv2.contourArea)
    return contours


def find_top_buttom_bar(cv_img, range=50, kernel_size=9):
    """
    查找游戏界面的顶部和底部栏
    :return: 包含顶部栏和底部栏的轮廓列表
    """

    img_h, img_w = cv_img.shape[:2]  # 图片高度, 宽度
    lu_color = cv_img[0, 0]  # 左上角像素颜色
    ld_color = cv_img[img_h-1, 0]  # 左下角像素颜色

    # 如果上下栏颜色差小于阈值, 则使用同一个颜色.
    diff = np.subtract(lu_color, ld_color, dtype=np.int16)  # 指定格式为 int16.  uint8 无法表示负数
    use_same_color = np.all(np.abs(diff) < range)
    if use_same_color:
        color = 0.5 * (lu_color + ld_color)
    else:
        color = lu_color
    
    contours = find_area(cv_img, color, range, kernel_size)  # 查找区域
    elements = []
    for i, cnt in enumerate(contours):
        x, y, w, h = cv2.boundingRect(cnt) # AABB包围盒
        if w == img_w:  # 全屏宽度
            element = {
                "id": i + 1,
                "bbox": [int(x), int(y), int(x + w), int(y + h)],
                "size": [int(w), int(h)],
            }
            elements.append(element)

    # 当上下栏 颜色差大时, 需要查找底栏
    if not use_same_color:
        contours = find_area(cv_img, ld_color, range, kernel_size)
        ele_count = len(elements)
        for i, cnt in enumerate(contours):
            x, y, w, h = cv2.boundingRect(cnt) # AABB包围盒
            if w == img_w:  # 全屏宽度
                element = {
                    "id": ele_count + 1,
                    "bbox": [int(x), int(y), int(x + w), int(y + h)],
                    "size": [int(w), int(h)],
                }
                ele_count += 1
                elements.append(element)

    return elements


def find_parent(elem, all_elems):
    """查找元素elem的父元素. 遍历所有元素, 找到包含elem的最小元素."""
    ex1, ey1, ex2, ey2 = elem["bbox"]
    best = None
    for p in all_elems:
        if p["id"] == elem["id"]:
            continue
        px1, py1, px2, py2 = p["bbox"]
        if px1 <= ex1 and py1 <= ey1 and px2 >= ex2 and py2 >= ey2:
            # check if fully contained
            if best is None:
                best = p
            else:
                # pick smallest container
                ba = (best["bbox"][2]-best["bbox"][0])*(best["bbox"][3]-best["bbox"][1])
                ca = (p["bbox"][2]-p["bbox"][0])*(p["bbox"][3]-p["bbox"][1])
                if ca < ba:
                    best = p
    return best

# 可视化 绘制每个元素的矩形框
def draw_element_rect(img, element):
    x1,y1,x2,y2 = element["bbox"]
    cv2.rectangle(img, (x1,y1), (x2,y2), (0,255,0), 2)  # 绿色矩形框
    cv2.putText(img, str(element["id"]), (x1,y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 1)  # 文本
    if element["children"] is not None and len(element["children"]) > 0:
        for child in element["children"]:
            draw_element_rect(img, child)


def process_img(cv_img):
    h, w = cv_img.shape[:2]

    # 查找顶部栏和底部栏
    elements = find_top_buttom_bar(cv_img)
    is_full_screen = len(elements) > 0  # 有一个全屏栏, 则为全屏界面
    for e in elements:
        print(e)

    # 1. 边缘检测 查找UI元素边界
    gray_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)  # 转灰度图
    edges = cv2.Canny(gray_img, 30, 100)    # Canny边缘检测算法. 两个参数为阈值, 梯度小于30为非边缘, 大于100为边缘.
    kernel = np.ones((5, 5), np.uint8)  # 返回一个5x5的数组, 元素全为1.
    closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)  # 形态学滤波. 闭合运算, 对边缘做"膨胀->腐蚀", 过滤小黑孔, 把断裂的轮廓线连接起来

    # 2. 查找潜在的UI元素轮廓
    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # 查找轮廓. RETR_EXTERNAL: 只取最外层轮廓; CHAIN_APPROX_SIMPLE: 简单的轮廓近似, 只返回轮廓的边界点.


    # 3. 根据轮廓计算AABB包围盒
    len_ele = len(elements)
    for i, cnt in enumerate(contours):
        x, y, bw, bh = cv2.boundingRect(cnt)    # 将任意形状的轮廓转换为矩形框.
        area = bw * bh
        # 元素面积<500 认为噪点.  元素面积>95%屏幕面积 认为全屏背景.
        if area < 500 or area > w * h * 0.95:
            continue
        element = {
            "id": len_ele + i + 1,
            "bbox": [int(x), int(y), int(x + bw), int(y + bh)],
            "size": [int(bw), int(bh)],
        }
        elements.append(element)

    # 4. 通过包含关系构建层级结构
    elements.sort(key=lambda e: (e["bbox"][1], e["bbox"][0]))    # 升序排序, 先 y 后 x
    for e in elements:
        e["children"] = []
        e["text"] = None
    root = {"elements": []}
    for e in elements:
        parent = find_parent(e, elements)
        if parent:
            parent["children"].append(e)
        else:
            root["elements"].append(e)

    root["is_full_screen"] = is_full_screen
    root["size"] = [w, h]

    return root


if __name__ == "__main__":
    import sys
    image_path = sys.argv[1]
    # result, closed_img, edges_img = parse_game_ui(image_path)
    cv_img = cv2.imread(image_path)
    result = process_img(cv_img)

    import json
    with open(os.path.splitext(image_path)[0] + "_result.json", "w") as f:
        json.dump(result, f, indent=2)

    # 可视化结果
    img = cv2.imread(image_path)
    for e in result["elements"]:
        draw_element_rect(img, e)
    # cv2.imshow("UI Elements", img)
    # cv2.waitKey(0)
    save_path = os.path.splitext(image_path)[0] + "_result.png"
    cv2.imwrite(save_path, img)

    # import sys
    # sys.path.append("D:\Projects\Learnings\python\AI\python")
    # from custom_package.utils import concat_images_h
    # imgs = [img, closed_img, edges_img]
    # concat_img = concat_images_h(imgs)
    # cv2.imwrite(os.path.splitext(image_path)[0] + "_result.png", concat_img)


    # color = raw_img[0, 0]  # 左上角点颜色
    # contours, mask_img, closed_img = find_area(raw_img, color, 50)

    # imgs = [raw_img, closed_img, mask_img]
    # concat_img = concat_images_h(imgs)
    # cv2.imwrite(os.path.splitext(image_path)[0] + "_result.png", concat_img)

    # for i, cnt in enumerate(contours):
    #     x, y, bw, bh = cv2.boundingRect(cnt)    # 将任意形状的轮廓转换为矩形框.
    #     area = bw * bh
    #     if area > 500:
    #         print(x, y, x+bw, y+bh, bw, bh, area)

    # 查找 上下栏
    # top_buttom_bar_contours = find_top_buttom_bar(raw_img)
    # for cnt in top_buttom_bar_contours:
    #     x, y, w, h = cv2.boundingRect(cnt) # AABB包围盒
    #     print(x, y, w, h)
