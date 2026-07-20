import base64
import json
from PIL import Image
from io import BytesIO
from llama_cpp import Llama
from custom_package.json_extract import extract_json_from_txt



class LlamaCppModel:
    """使用llama.cpp 加载模型"""

    def __init__(self, model_path: str, handler, chat_format: str = None):
        self.llm = Llama(
            model_path=model_path,
            chat_handler=handler,
            n_ctx=4096,
            n_gpu_layers=-1,
            n_threads=8,
            verbose=False,
            chat_format=chat_format,
            # repeat_penalty=1.2,     # 重复惩罚，大于1会降低重复词的概率
            # top_p = 1.0,    # 核采样概率阈值（0.9 表示只从累积概率前 90% 的词里选）
            # top_k = 40,    # 只从概率最高的 k 个词里采样
            # stop=["<|im_end|>", "\n\n\n"],  # 遇到这些字符串时提前停止
            # temperature=0.0, # 控制随机性, 0.0 最确定, 1.0 最随机
            # grounding_mode="bbox", #强制输出边界框
            # stream=False,  # 不开启流式输出
            # do_sample=False,  # 不开启采样, 直接输出确定性结果
            # max_tokens=512,  # 最大输出token数
        )

        # 系统提示词
        self.system_prompt = """你是一个专业的游戏UI解析专家，专门识别游戏截图中的可点击按钮和交互元素。

你的任务是：
1. 仔细分析提供的游戏截图
2. 识别所有真正可点击的按钮、图标、文字链接、复选框和单选按钮
3. 忽略纯文本、背景装饰和不可交互的元素
4. 提供精确的边界框坐标，误差不超过5像素
5. 输出严格的JSON格式，不要包含任何其他文字、解释或Markdown标记

每个元素必须包含以下字段：
- "name": 按钮的功能名称（如"开始游戏"、"设置"、"返回"、"关闭"）
- "text": 按钮上显示的文字（如果没有则为空字符串）
- "bbox": 边界框坐标 [x_min, y_min, x_max, y_max]（像素值，左上角为原点）
- "type": 元素类型（"button"|"icon"|"text_link"|"checkbox"|"radio"）

注意事项：
- 不要遗漏任何可见的交互元素，包括角落和边缘的小图标
- 如果是游戏特有的图标，请根据其形状和位置合理推测功能名称
- 坐标必须精确，确保边界框完全包围按钮
- 输出必须是有效的JSON格式，不能有任何语法错误
"""

    
    def image_to_base64_uri(self, img_path):
        """将图片转换为base64编码的url"""
        img = Image.open(img_path).convert("RGB")
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_base64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_base64}", img.width, img.height
    
        # with open(img_path, "rb").convert("RGB") as f:
        #     img_base64 = base64.b64encode(f.read()).decode("utf-8")
        # return f"data:image/png;base64,{img_base64}"


    def process_image(self, img_path, prompt: str):
        """处理图片"""
        data_uri, img_width, img_height = self.image_to_base64_uri(img_path)

        completion = self.llm.create_chat_completion(
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": data_uri}},
                    {"type": "text", "text": prompt},
                ]},
            ],
            # stop=["<|im_end|>", "\n\n"],  # 提前停止标记
            # top_p = 1.0,    # 确定性输出
            temperature=0.0, # 控制随机性, 0.0 最确定, 1.0 最随机
            # stream=False,  # 不开启流式输出
            max_tokens=512,  # 最大输出token数
            frequency_penalty=0,  # 频率惩罚, 避免重复输出
        )
        
        # 提取输出的Json字符串
        result_txt = completion["choices"][0]["message"]["content"]
        print(result_txt)
        result_txt = extract_json_from_txt(result_txt)
        result_txt = self.process_position(result_txt, img_width, img_height)
        return result_txt
    
    def process_position(self, result_txt: str, img_width: int, img_height: int):
        """处理位置. qwen 系模型  输出的坐标都是 0-1000. 需要按图片宽高 进行转换 xy / 1000 * 图片宽高"""
        try:
            datas = json.loads(result_txt)
        except:
            import json5
            datas = json5.loads(result_txt)

        if type(datas) == list:
            for item in datas:
                item["bbox"][0] *= (img_width / 1000)
                item["bbox"][1] *= (img_height / 1000)
                item["bbox"][2] *= (img_width / 1000)
                item["bbox"][3] *= (img_height / 1000)
        elif type(datas) == dict:
            datas["bbox"][0] *= (img_width / 1000)
            datas["bbox"][1] *= (img_height / 1000)
            datas["bbox"][2] *= (img_width / 1000)
            datas["bbox"][3] *= (img_height / 1000)
        return json.dumps(datas, ensure_ascii=False)
    


if __name__ == "__main__":
    from llama_cpp.llama_chat_format import Qwen3VLChatHandler
    handle = Qwen3VLChatHandler(clip_model_path="D:/Projects/Learnings/python/AI/Hugface_Model/Holo2-8B.mmproj-Q8_0.gguf", verbose=False)

    # qwen 类模型  输出的坐标都是 0-1000. 需要按图片宽高 进行转换 xy / 1000 * 图片宽高
    model = LlamaCppModel("D:/Projects/Learnings/python/AI/Hugface_Model/Holo2-8B.Q4_K_M.gguf", handle)

    prompt = "请分析这张游戏截图，识别并列出所有可点击的按钮和交互元素."


    result_txt = model.process_image("D:/Projects/AI/背包.png", prompt)
    print(result_txt)