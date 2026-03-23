TOOLS_DECLARATION =[
    {
        "type": "function",
        "function": {
            "name": "vision_extract_latex",
            "description": "当用户上传了包含数学题的图片时调用，提取图片中的 LaTeX 公式和文字描述。",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_path": {"type": "string", "description": "图片的本地文件路径"}
                },
                "required": ["image_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "memory_save_mistake",
            "description": "将诊断出的错题、考点和解析存入用户的数据库错题本中。",
            "parameters": {
                "type": "object",
                "properties": {
                    "latex_content": {"type": "string", "description": "题目的LaTeX内容"},
                    "knowledge_points": {"type": "string", "description": "考点，多个用逗号分隔"},
                    "analysis": {"type": "string", "description": "AI的诊断解析"}
                },
                "required":["latex_content", "knowledge_points", "analysis"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_pdf_paper",
            "description": "根据原始题目生成变式题试卷。需要提供原始题目内容和知识点。",
            "parameters": {
                "type": "object",
                "properties": {
                    "original_question": {"type": "string", "description": "原始题目的内容，用于生成变式题"},
                    "knowledge_point": {"type": "string", "description": "题目涉及的知识点"}
                },
                "required": ["original_question", "knowledge_point"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "latex_format_cleaner",
            "description": "清理、格式化和校验 LaTeX 字符串，去除多余空格并修复常见语法错误。",
            "parameters": {
                "type": "object",
                "properties": {
                    "raw_latex": {"type": "string", "description": "原始的、未经清理的 LaTeX 文本"}
                },
                "required": ["raw_latex"]
            }
        }
    }
]
