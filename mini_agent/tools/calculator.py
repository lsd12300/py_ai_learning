# -*- coding: utf-8 -*-
# 计算器工具


def calculate(expression: str) -> str:
    """
    计算数学表达式.
    只允许数字和基本运算符, 防止代码注入.
    """
    allowed_chars = set("0123456789.+-*/(), ")
    if not all(char in allowed_chars for char in expression):
        return f"表达式包含不允许的字符: {expression}"

    try:
        result = eval(expression) # eval() 可执行任意 Python 代码, 注意安全风险
        return f"{expression} = {result}"
    except ZeroDivisionError as e:
        return f"错误: 除数不能为零"
    except SyntaxError as e:
        return f"表达式语法错误: {expression}"
    except Exception as e:
        return f"计算出错: {e}"
