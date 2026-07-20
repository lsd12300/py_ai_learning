# -*- coding: utf-8 -*-
# LocateAnything-3B 提示词模板


# 文本区域
# PROMPT_TXT = f"Please locate the text referred as {phrase}."

# 检测所有文本
# PROMPT_TXT = "Detect all the text in box format."

# 定位坐标
# PROMPT_POINT = f"Point to: {phrase}."

# GUI区域
# PROMPT_GUI = f"Locate the region that matches the following description: {phrase}."

# 包围框
# PROMPT_BOX = f"Locate the {phrase}."

# 单类型多对象
# PROMPT_MULTI = f"Locate all the instances that match the following description: {phrase}."

# 单类型单对象
# PROMPT_SINGLE = f"Locate a single instance that matches the following description: {phrase}."

# 多类型多对象
# phrase = "</c>".join(categories)
# prompt = f"Locate all the instances that match the following description: {phrase}."


def prompt_txt_grounding(phrase: str) -> str:
    """获取文本区域定位提示词"""
    return f"Please locate the text referred as {phrase}."

def prompt_txt_all() -> str:
    """获取检测所有文本提示词"""
    return f"Detect all the text in box format."

def prompt_point(phrase: str) -> str:
    """获取定位坐标提示词"""
    return f"Point to: {phrase}."

def prompt_gui(phrase: str) -> str:
    """获取GUI区域提示词"""
    return f"Locate the region that matches the following description: {phrase}."

def prompt_box(phrase: str) -> str:
    """获取包围框提示词"""
    return f"Locate the {phrase}."

def prompt_multi(phrase: str) -> str:
    """获取单类型多对象提示词"""
    return f"Locate all the instances that match the following description: {phrase}."

def prompt_single(phrase: str) -> str:
    """获取单类型单对象提示词"""
    return f"Locate a single instance that matches the following description: {phrase}."

def prompt_category(categories: list) -> str:
    """获取多类型多对象提示词"""
    phrase = "</c>".join(categories)
    return f"Locate all the instances that match the following description: {phrase}."
