import json
import re



def extract_json_from_txt(txt: str) -> str:
    """
    从模型返回内容中提取JSON字符串.
        1. 去掉 <think> 标签
        2. 去掉 空行
    """

    # re.sub 正则匹配替换
    clean_txt = re.sub(r'<think>.*?</think>', '', txt, flags=re.IGNORECASE | re.DOTALL)
    return clean_txt