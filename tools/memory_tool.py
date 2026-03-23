from storage.relational_db import save_mistake_to_db

def memory_save_mistake(latex_content: str, knowledge_points: str, analysis: str = "", image_path: str = "") -> str:
    """保存错题到数据库的工具函数"""
    
    result = save_mistake_to_db(1, image_path, latex_content, knowledge_points, analysis)
    
    return f"✅ 错题已保存到数据库\n题目: {latex_content[:100]}...\n知识点: {knowledge_points}\n分析: {analysis[:100]}..."
