import base64
from openai import OpenAI
from config.settings import settings
from config.tools_meta import TOOLS_DECLARATION

class LLMClient:
    """主模型客户端（qwen-max），用于 Agent 调度和工具调用"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL
        )
        self.model = settings.LLM_MODEL_NAME
        self.vision_model = settings.VISION_MODEL_NAME

    def chat_with_tools(self, messages: list) -> dict:
        """带工具调用的通用对话"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=TOOLS_DECLARATION,
            tool_choice="auto"
        )
        return response.choices[0].message

    def chat_with_image(self, prompt: str, base64_image: str) -> str:
        """多模态直通调用（使用 qwen-vl-plus）"""
        response = self.client.chat.completions.create(
            model=self.vision_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ]
        )
        return response.choices[0].message.content

    def chat_simple(self, messages: list) -> str:
        """简单对话（无工具调用）"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content


class DeepSeekClient:
    """DeepSeek 客户端，专门用于生成变式题"""
    
    def __init__(self):
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL
        )
        self.model = settings.DEEPSEEK_MODEL_NAME

    def chat(self, messages: list) -> str:
        """简单对话"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content

    def generate_variants(self, prompt: str) -> str:
        """生成变式题"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

