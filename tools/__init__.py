from .vision_tool import vision_extract_latex
from .memory_tool import memory_save_mistake
from .pdf_tool import generate_pdf_paper
from .latex_tool import latex_format_cleaner  # ✨ [新增]

AVAILABLE_TOOLS = {
    "vision_extract_latex": vision_extract_latex,
    "memory_save_mistake": memory_save_mistake,
    "generate_pdf_paper": generate_pdf_paper,
    "latex_format_cleaner": latex_format_cleaner # ✨ [新增]
}   