import sys
import os

# 确保能正确导入项目根目录的模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import LinPaperAgent
from config.settings import settings

def run_cli():
    print("="*60)
    print(" 🤖 欢迎来到 Lin-Paper AI 错题管家 (CLI 模式) ")
    print("="*60)
    print("提示：您可以直接输入问题，或者输入图片绝对路径让 AI 识别。输入 'exit' 退出。")
    print("-"*60)
    
    agent = LinPaperAgent()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("\n[Student] 👤 : ").strip()
            
            if user_input.lower() in['exit', 'quit']:
                print("👋 再见！")
                break
                
            if not user_input:
                continue
                
            print("\n[Lin-Paper] 🧠 思考调度中...")
            
            # 检查用户输入的是不是一个本地文件路径
            if os.path.exists(user_input) and user_input.lower().endswith(('.png', '.jpg', '.jpeg')):
                prompt = f"我上传了一张图片，路径是 {user_input}，请调用视觉工具提取公式，并存入错题本。"
                response = agent.run(prompt)
            else:
                # 正常文字对话
                response = agent.run(user_input)
                
            print(f"\n[Lin-Paper] 🤖 : {response}")
            
        except KeyboardInterrupt:
            print("\n👋 强制退出，再见！")
            break
        except Exception as e:
            print(f"\n❌ 系统发生异常: {str(e)}")

if __name__ == "__main__":
    run_cli()