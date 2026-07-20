# -*- coding: utf-8 -*-
# 项目配置, 环境变量配置

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> None:
    """加载 .env 配置文件"""
    env_path = Path(__file__).parent / ".env"
    print(env_path)

    # 加载环境变量配置
    load_dotenv(dotenv_path=env_path)

    if not os.environ.get("OPENAI_API_KEY"):
        raise EnvironmentError(
            "\n错误: 缺少 OPENAI_API_KEY 环境变量\n"
            "\nj解决方法: \n"
            "1. 项目根目录创建 .env 文件\n"
            "2. 在 .env 文件中填入 OPENAI_API_KEY 环境变量\n"
        )


if __name__ == "__main__":
    load_config()