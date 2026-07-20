# -*- coding: utf-8 -*-
# 工作流主函数


import argparse
from config import IMAGE_PATH, LLAMA_CPP_URL, MODEL_NAME, JSON_PATH
from analysis_structure import AnalysisStructure



def main():
    parser = argparse.ArgumentParser(
        description="解析并定位界面元素"
    )
    parser.add_argument(
        "image_path",
        nargs="?",
        default=None,
        help="游戏截图的路径",
    )
    parser.add_argument(
        "--model_name", "-m", default=None, help="模型名称"
    )
    parser.add_argument(
        "--server_url", "-s", default=None, help="服务器地址"
    )
    args = parser.parse_args()


    # 参数默认值
    image_path = args.image_path
    if image_path is None:
        image_path = IMAGE_PATH
    server_url = args.server_url
    if server_url is None:
        server_url = LLAMA_CPP_URL
    model_name = args.model_name
    if model_name is None:
        model_name = MODEL_NAME

    analyzer = AnalysisStructure(model_name)
    result = analyzer.analyze(image_path)
    with open(JSON_PATH, "w") as f:
        f.write(result)

if __name__ == "__main__":
    main()