import json
from core.llm_client import LLMClient
from config.prompts import SYSTEM_AGENT_PROMPT
from tools import AVAILABLE_TOOLS

class LinPaperAgent:
    def __init__(self):
        self.client = LLMClient()
        self.memory = [{"role": "system", "content": SYSTEM_AGENT_PROMPT}]

    def run(self, user_input: str) -> str:
        """Agent 主事件循环"""
        self.memory.append({"role": "user", "content": user_input})
        
        max_iterations = 5  # 防止无限循环
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            
            # 1. 大脑思考
            message = self.client.chat_with_tools(self.memory)
            
            # 2. 如果不需要调用工具，直接返回文字给用户
            if not message.tool_calls:
                # 记录 AI 的回复
                self.memory.append({"role": "assistant", "content": message.content})
                return message.content

            # 3. 记录 AI 的工具调用决策
            self.memory.append({
                "role": "assistant",
                "content": message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    } for tc in message.tool_calls
                ]
            })

            # 4. 执行工具调用
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                print(f"[Agent 调度] 正在调用工具: {func_name}，参数: {args}")
                
                # 实际执行工具函数
                if func_name in AVAILABLE_TOOLS:
                    result = AVAILABLE_TOOLS[func_name](**args)
                else:
                    result = f"Error: 找不到工具 {func_name}"
                
                print(f"[Agent 调度] 工具 {func_name} 执行完成")
                
                # 5. 将工具的执行结果传回给大模型
                self.memory.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": func_name,
                    "content": str(result)
                })
            
            # 继续循环：大模型看到工具结果后，决定下一步是继续调工具还是回答用户
        
        return "抱歉，处理超时，请稍后重试。"
