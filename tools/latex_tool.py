import re

def latex_format_cleaner(raw_latex: str) -> str:
    """
    清洗和校验大模型/OCR 提取出的 LaTeX 字符串
    """
    if not raw_latex:
        return ""
        
    # 1. 移除多余的 markdown 标记 (例如 ```latex ... ```)
    cleaned = re.sub(r"```(latex)?", "", raw_latex)
    
    # 2. 合并多余的连续空行
    cleaned = re.sub(r'\n\s*\n', '\n\n', cleaned)
    
    # 3. 简单的符号配对检查 (修复行内公式缺少 $ 的情况，非常基础的规则)
    if cleaned.count('$') % 2 != 0:
        # 如果 $ 不成对，强制在末尾补全（实际场景可接入专业的 pylatexenc 库）
        cleaned += '$'
        
    # 4. 去除首尾空白
    return cleaned.strip()

# 【提示】如果要让主控 Agent 能自主调用这个工具，你需要：
# 1. 在 tools/__init__.py 的 AVAILABLE_TOOLS 中加上它
# 2. 在 config/tools_meta.py 中声明它的 JSON Schema