# -*- coding: utf-8 -*-


import os

from core.config import settings


def main():
    """主函数"""
    print(settings.memory.mode)
    print(settings.memory.storage_dir)
    # print(settings.logging.level)
    print(settings.api_key)


if __name__ == "__main__":
    main()