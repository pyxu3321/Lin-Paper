# init_knowledge.py
"""
初始化数据库脚本
运行此脚本将创建必要的数据库表和目录结构
"""

from storage.relational_db import init_db
from config.settings import settings

def setup():
    print("=" * 50)
    print("Lin-Paper 系统初始化")
    print("=" * 50)
    
    print("\n1. 初始化关系型数据库...")
    init_db()
    
    print("\n2. 初始化工作目录...")
    settings.init_workspace()
    
    print("\n" + "=" * 50)
    print("初始化完成！系统已准备就绪。")
    print("=" * 50)

if __name__ == "__main__":
    setup()
