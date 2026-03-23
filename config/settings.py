import os
from pathlib import Path
from dotenv import load_dotenv

# 1. 确定项目根目录 (Lin-Paper/ 目录)
BASE_DIR = Path(__file__).resolve().parent.parent

# 2. 显式加载 .env 文件
dotenv_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=dotenv_path)

class Settings:
    """
    系统配置中心：从环境变量读取配置，并定义默认路径
    """
    
    # --- LLM API 配置（用于 Agent 调度）---
    LLM_API_KEY = os.getenv("LLM_API_KEY")
    LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen-max")
    
    # 多模态模型配置（用于图片识别）
    VISION_MODEL_NAME = os.getenv("VISION_MODEL_NAME", "qwen-vl-plus")
    
    # --- DeepSeek 配置（用于生成变式题）---
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
    
    # --- 兼容旧属性名 ---
    @property
    def API_KEY(self):
        return self.LLM_API_KEY
    
    @property
    def BASE_URL(self):
        return self.LLM_BASE_URL
    
    @property
    def MODEL_NAME(self):
        return self.LLM_MODEL_NAME
    
    # --- 工作目录路径配置 ---
    WORKSPACE_DIR = BASE_DIR / "workspace"
    UPLOADS_DIR = WORKSPACE_DIR / "uploads"
    OUTPUTS_DIR = WORKSPACE_DIR / "outputs"
    TEMP_DIR = WORKSPACE_DIR / "temp"
    
    # --- 数据库路径配置 ---
    SQLITE_DB_PATH = BASE_DIR / "storage" / "relational_db" / "lin_paper.db"
    CHROMA_DB_PATH = BASE_DIR / "storage" / "vector_db"
    
    def init_workspace(self):
        """初始化系统所需的所有文件夹"""
        directories = [
            self.WORKSPACE_DIR,
            self.UPLOADS_DIR,
            self.OUTPUTS_DIR,
            self.TEMP_DIR,
            self.SQLITE_DB_PATH.parent,
            self.CHROMA_DB_PATH
        ]
        
        for dir_path in directories:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                print(f"[System] 已创建目录: {dir_path}")

# 实例化配置对象
settings = Settings()
settings.init_workspace()

if __name__ == "__main__":
    print(f"项目根目录: {BASE_DIR}")
    print(f"主模型: {settings.LLM_MODEL_NAME}")
    print(f"多模态模型: {settings.VISION_MODEL_NAME}")
    print(f"DeepSeek 模型: {settings.DEEPSEEK_MODEL_NAME}")
    print(f"数据库路径: {settings.SQLITE_DB_PATH}")
