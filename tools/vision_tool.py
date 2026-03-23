import base64
from core.llm_client import LLMClient
from config.prompts import VISION_EXTRACT_PROMPT
from tools.latex_tool import latex_format_cleaner

def encode_image(image_path: str) -> str:
    """将图片编码为 base64"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def vision_extract_latex(image_path: str) -> str:
    """
    视觉工具：调用多模态 API 提取图片中的数学公式
    :param image_path: 图片路径
    :return: 识别出的 LaTeX 文本
    """
    try:
        client = LLMClient()
        base64_image = encode_image(image_path)
        
        result = client.chat_with_image(VISION_EXTRACT_PROMPT, base64_image)
        
        cleaned_result = latex_format_cleaner(result)
        return cleaned_result
    except Exception as e:
        return f"视觉提取失败: {str(e)}"
