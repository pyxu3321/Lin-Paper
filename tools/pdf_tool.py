import os
import re
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm
from config.settings import settings
from config.prompts import DIAGRAM_TYPES_PROMPT, DIAGRAM_ANALYSIS_PROMPT, VARIANT_QUESTIONS_PROMPT
from core.llm_client import DeepSeekClient, LLMClient
import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon, Circle, Ellipse, FancyArrowPatch, Arc
import matplotlib
matplotlib.use('Agg')
import numpy as np
from io import BytesIO

def get_chinese_font():
    """尝试获取中文字体"""
    font_paths = [
        "C:/Windows/Fonts/simsun.ttc",
        "C:/Windows/Fonts/simhei.ttf",
        "C:/Windows/Fonts/msyh.ttc",
    ]
    
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                pdfmetrics.registerFont(TTFont('ChineseFont', font_path))
                return 'ChineseFont'
            except:
                continue
    return None


class DiagramFactory:
    """通用数学图形绘制工厂"""
    
    def __init__(self):
        self.figsize = (5, 4)
        self.dpi = 150
    
    def _create_base_figure(self):
        """创建基础图形对象"""
        fig, ax = plt.subplots(figsize=self.figsize)
        return fig, ax
    
    def _finalize_figure(self, fig, ax):
        """完成图形绘制，返回 BytesIO"""
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        plt.tight_layout()
        buf = BytesIO()
        plt.savefig(buf, format='png', dpi=self.dpi, bbox_inches='tight', facecolor='white')
        buf.seek(0)
        plt.close()
        return buf
    
    def draw_intersecting_lines(self, angle=45, line1_labels=("A", "B"), 
                                 line2_labels=("C", "D"), intersection_label="O"):
        """绘制两条直线相交的图形"""
        fig, ax = self._create_base_figure()
        
        angle = max(1, min(179, int(angle)))
        angle_rad = np.radians(angle)
        
        ax.plot([-2.5, 2.5], [0, 0], 'b-', linewidth=2.5)
        
        length = 2.5
        x2_end1 = length * np.cos(angle_rad)
        y2_end1 = length * np.sin(angle_rad)
        x2_end2 = -length * np.cos(angle_rad)
        y2_end2 = -length * np.sin(angle_rad)
        
        ax.plot([x2_end2, x2_end1], [y2_end2, y2_end1], 'r-', linewidth=2.5)
        
        ax.plot(0, 0, 'ko', markersize=10, zorder=5)
        ax.annotate(intersection_label, xy=(0, 0), xytext=(0.2, -0.4), 
                    fontsize=14, fontweight='bold')
        
        ax.set_xlim(-3, 3)
        ax.set_ylim(-3, 3)
        
        ax.annotate(line1_labels[0], xy=(-2.7, 0.2), fontsize=14, fontweight='bold', color='blue')
        ax.annotate(line1_labels[1], xy=(2.5, 0.2), fontsize=14, fontweight='bold', color='blue')
        ax.annotate(line2_labels[0], xy=(x2_end2 - 0.3, y2_end2 - 0.3), 
                    fontsize=14, fontweight='bold', color='red')
        ax.annotate(line2_labels[1], xy=(x2_end1 + 0.2, y2_end1 + 0.3), 
                    fontsize=14, fontweight='bold', color='red')
        
        return self._finalize_figure(fig, ax)
    
    def draw_coordinate_system(self, x_range=(-5, 5), y_range=(-5, 5), 
                                functions=None, points=None, show_grid=True):
        """绘制直角坐标系，支持函数曲线和点"""
        fig, ax = self._create_base_figure()
        
        ax.axhline(y=0, color='black', linewidth=1.5)
        ax.axvline(x=0, color='black', linewidth=1.5)
        
        ax.annotate('x', xy=(x_range[1] - 0.3, 0.3), fontsize=12, fontweight='bold')
        ax.annotate('y', xy=(0.3, y_range[1] - 0.3), fontsize=12, fontweight='bold')
        
        ax.annotate('', xy=(x_range[1], 0), xytext=(x_range[0], 0),
                    arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
        ax.annotate('', xy=(0, y_range[1]), xytext=(0, y_range[0]),
                    arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
        
        if functions:
            x = np.linspace(x_range[0], x_range[1], 500)
            for func in functions:
                expr = func.get('expression', 'x')
                color = func.get('color', 'blue')
                label = func.get('label', '')
                
                try:
                    y = eval(expr, {'x': x, 'np': np, 'sin': np.sin, 'cos': np.cos, 
                                    'tan': np.tan, 'sqrt': np.sqrt, 'abs': np.abs,
                                    'exp': np.exp, 'log': np.log, 'pi': np.pi})
                    ax.plot(x, y, color=color, linewidth=2, label=label)
                except:
                    pass
        
        if points:
            for pt in points:
                px, py = pt.get('x', 0), pt.get('y', 0)
                label = pt.get('label', '')
                color = pt.get('color', 'red')
                ax.plot(px, py, 'o', color=color, markersize=8)
                if label:
                    ax.annotate(label, xy=(px, py), xytext=(px + 0.2, py + 0.2), 
                               fontsize=12, fontweight='bold')
        
        ax.set_xlim(x_range[0] - 0.5, x_range[1] + 0.5)
        ax.set_ylim(y_range[0] - 0.5, y_range[1] + 0.5)
        ax.grid(show_grid, alpha=0.3, linestyle='--')
        
        ax.set_xticks(list(range(int(x_range[0]), int(x_range[1]) + 1)))
        ax.set_yticks(list(range(int(y_range[0]), int(y_range[1]) + 1)))
        
        return self._finalize_figure(fig, ax)
    
    def draw_triangle(self, vertices, labels=None, show_angles=False, show_sides=False):
        """绘制三角形"""
        fig, ax = self._create_base_figure()
        
        vertices = np.array(vertices)
        triangle = Polygon(vertices, fill=False, edgecolor='blue', linewidth=2.5)
        ax.add_patch(triangle)
        
        if labels:
            for i, label in enumerate(labels):
                vx, vy = vertices[i]
                offset_x = 0.3 if vx >= 0 else -0.5
                offset_y = 0.3 if vy >= 0 else -0.5
                ax.annotate(label, xy=(vx, vy), xytext=(vx + offset_x, vy + offset_y),
                           fontsize=14, fontweight='bold')
        
        ax.plot(vertices[:, 0], vertices[:, 1], 'ro', markersize=8)
        
        min_x, max_x = vertices[:, 0].min() - 1, vertices[:, 0].max() + 1
        min_y, max_y = vertices[:, 1].min() - 1, vertices[:, 1].max() + 1
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)
        
        return self._finalize_figure(fig, ax)
    
    def draw_circle(self, center=(0, 0), radius=2, points=None, 
                    show_radius=False, show_center=True, center_label="O"):
        """绘制圆"""
        fig, ax = self._create_base_figure()
        
        circle = Circle(center, radius, fill=False, edgecolor='blue', linewidth=2.5)
        ax.add_patch(circle)
        
        if show_center:
            ax.plot(center[0], center[1], 'ko', markersize=8)
            ax.annotate(center_label, xy=center, xytext=(center[0] + 0.2, center[1] + 0.2),
                       fontsize=14, fontweight='bold')
        
        if points:
            for pt in points:
                px, py = pt.get('x', 0), pt.get('y', 0)
                label = pt.get('label', '')
                ax.plot(px, py, 'ro', markersize=8)
                if label:
                    ax.annotate(label, xy=(px, py), xytext=(px + 0.2, py + 0.2),
                               fontsize=12, fontweight='bold')
                if show_radius and show_center:
                    ax.plot([center[0], px], [center[1], py], 'g--', linewidth=1.5)
        
        ax.set_xlim(center[0] - radius - 1, center[0] + radius + 1)
        ax.set_ylim(center[1] - radius - 1, center[1] + radius + 1)
        
        return self._finalize_figure(fig, ax)
    
    def draw_ellipse(self, center=(0, 0), a=3, b=2, show_axes=False, 
                     show_foci=False, foci_labels=("F1", "F2")):
        """绘制椭圆"""
        fig, ax = self._create_base_figure()
        
        ellipse = Ellipse(center, 2*a, 2*b, fill=False, edgecolor='blue', linewidth=2.5)
        ax.add_patch(ellipse)
        
        ax.plot(center[0], center[1], 'ko', markersize=6)
        
        if show_axes:
            ax.plot([center[0] - a, center[0] + a], [center[1], center[1]], 
                   'g--', linewidth=1.5, label='长轴')
            ax.plot([center[0], center[0]], [center[1] - b, center[1] + b], 
                   'r--', linewidth=1.5, label='短轴')
        
        if show_foci:
            c = np.sqrt(a**2 - b**2) if a > b else np.sqrt(b**2 - a**2)
            if a > b:
                f1, f2 = (center[0] - c, center[1]), (center[0] + c, center[1])
            else:
                f1, f2 = (center[0], center[1] - c), (center[0], center[1] + c)
            ax.plot([f1[0], f2[0]], [f1[1], f2[1]], 'ro', markersize=8)
            ax.annotate(foci_labels[0], xy=f1, xytext=(f1[0] - 0.5, f1[1] - 0.5),
                       fontsize=12, fontweight='bold')
            ax.annotate(foci_labels[1], xy=f2, xytext=(f2[0] + 0.3, f2[1] - 0.5),
                       fontsize=12, fontweight='bold')
        
        ax.set_xlim(center[0] - a - 1, center[0] + a + 1)
        ax.set_ylim(center[1] - b - 1, center[1] + b + 1)
        
        return self._finalize_figure(fig, ax)
    
    def draw_parabola(self, a=1, vertex=(0, 0), direction='up', 
                       x_range=(-3, 3), show_focus=True, show_directrix=True):
        """绘制抛物线"""
        fig, ax = self._create_base_figure()
        
        if direction in ['up', 'down']:
            x = np.linspace(x_range[0], x_range[1], 500)
            y = a * (x - vertex[0])**2 + vertex[1]
            if direction == 'down':
                y = -a * (x - vertex[0])**2 + vertex[1]
            ax.plot(x, y, 'b-', linewidth=2.5)
            
            if show_focus:
                p = 1 / (4 * a)
                if direction == 'up':
                    focus = (vertex[0], vertex[1] + p)
                else:
                    focus = (vertex[0], vertex[1] - p)
                ax.plot(focus[0], focus[1], 'ro', markersize=8)
                ax.annotate('F', xy=focus, xytext=(focus[0] + 0.2, focus[1] + 0.2),
                           fontsize=12, fontweight='bold')
            
            if show_directrix:
                p = 1 / (4 * a)
                if direction == 'up':
                    directrix_y = vertex[1] - p
                else:
                    directrix_y = vertex[1] + p
                ax.axhline(y=directrix_y, color='g', linestyle='--', linewidth=1.5)
        else:
            y = np.linspace(x_range[0], x_range[1], 500)
            x = a * (y - vertex[1])**2 + vertex[0]
            if direction == 'left':
                x = -a * (y - vertex[1])**2 + vertex[0]
            ax.plot(x, y, 'b-', linewidth=2.5)
        
        ax.plot(vertex[0], vertex[1], 'ko', markersize=8)
        ax.annotate('V', xy=vertex, xytext=(vertex[0] + 0.2, vertex[1] + 0.2),
                   fontsize=12, fontweight='bold')
        
        ax.set_xlim(x_range[0] - 1, x_range[1] + 1)
        ax.set_ylim(x_range[0] - 1, x_range[1] + 1)
        
        return self._finalize_figure(fig, ax)
    
    def draw_polygon(self, vertices, labels=None, fill=False):
        """绘制多边形"""
        fig, ax = self._create_base_figure()
        
        vertices = np.array(vertices)
        polygon = Polygon(vertices, fill=fill, edgecolor='blue', 
                         facecolor='lightblue', linewidth=2.5)
        ax.add_patch(polygon)
        
        if labels:
            for i, label in enumerate(labels):
                vx, vy = vertices[i]
                ax.annotate(label, xy=(vx, vy), xytext=(vx + 0.2, vy + 0.2),
                           fontsize=14, fontweight='bold')
        
        ax.plot(vertices[:, 0], vertices[:, 1], 'ro', markersize=8)
        
        min_x, max_x = vertices[:, 0].min() - 1, vertices[:, 0].max() + 1
        min_y, max_y = vertices[:, 1].min() - 1, vertices[:, 1].max() + 1
        ax.set_xlim(min_x, max_x)
        ax.set_ylim(min_y, max_y)
        
        return self._finalize_figure(fig, ax)
    
    def draw_angle(self, vertex=(0, 0), arms=None, angle_value=45, 
                   label="", show_arc=True):
        """绘制角度"""
        fig, ax = self._create_base_figure()
        
        if arms is None:
            arms = [(1, 0), (np.cos(np.radians(angle_value)), np.sin(np.radians(angle_value)))]
        
        length = 3
        ax.plot([vertex[0], vertex[0] + length * arms[0][0]], 
               [vertex[1], vertex[1] + length * arms[0][1]], 'b-', linewidth=2.5)
        ax.plot([vertex[0], vertex[0] + length * arms[1][0]], 
               [vertex[1], vertex[1] + length * arms[1][1]], 'r-', linewidth=2.5)
        
        ax.plot(vertex[0], vertex[1], 'ko', markersize=10)
        
        if show_arc:
            arc = Arc(vertex, 1, 1, angle=0, theta1=0, theta2=angle_value, 
                     color='green', linewidth=2)
            ax.add_patch(arc)
        
        if label:
            mid_angle = np.radians(angle_value / 2)
            label_x = vertex[0] + 1.5 * np.cos(mid_angle)
            label_y = vertex[1] + 1.5 * np.sin(mid_angle)
            ax.annotate(label, xy=(label_x, label_y), fontsize=12, fontweight='bold')
        
        ax.set_xlim(-4, 4)
        ax.set_ylim(-4, 4)
        
        return self._finalize_figure(fig, ax)
    
    def draw_vectors(self, vectors, origin=(0, 0), show_components=False):
        """绘制向量"""
        fig, ax = self._create_base_figure()
        
        ax.axhline(y=0, color='gray', linewidth=0.5)
        ax.axvline(x=0, color='gray', linewidth=0.5)
        
        for vec in vectors:
            vx, vy = vec.get('x', 0), vec.get('y', 0)
            label = vec.get('label', '')
            color = vec.get('color', 'blue')
            ox, oy = vec.get('origin', origin)
            
            ax.annotate('', xy=(ox + vx, oy + vy), xytext=(ox, oy),
                       arrowprops=dict(arrowstyle='->', color=color, lw=2.5))
            
            if label:
                ax.annotate(label, xy=(ox + vx/2, oy + vy/2 + 0.3),
                           fontsize=12, fontweight='bold', color=color)
            
            if show_components:
                ax.plot([ox, ox + vx], [oy, oy], 'g--', linewidth=1)
                ax.plot([ox + vx, ox + vx], [oy, oy + vy], 'g--', linewidth=1)
        
        all_x = [v.get('x', 0) + v.get('origin', origin)[0] for v in vectors]
        all_y = [v.get('y', 0) + v.get('origin', origin)[1] for v in vectors]
        max_val = max(max(abs(min(all_x)), abs(max(all_x)), 
                         abs(min(all_y)), abs(max(all_y))) + 1, 4)
        
        ax.set_xlim(-max_val, max_val)
        ax.set_ylim(-max_val, max_val)
        
        return self._finalize_figure(fig, ax)
    
    def draw_histogram(self, data, bins=None, title="", xlabel="", ylabel=""):
        """绘制直方图"""
        fig, ax = self._create_base_figure()
        
        ax.hist(data, bins=bins, edgecolor='black', color='steelblue', alpha=0.7)
        
        if title:
            ax.set_title(title, fontsize=14)
        if xlabel:
            ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            ax.set_ylabel(ylabel, fontsize=12)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        
        return self._finalize_figure(fig, ax)
    
    def create_diagram(self, diagram_type: str, params: dict):
        """根据类型创建图形的统一入口"""
        try:
            if diagram_type == "intersecting_lines":
                return self.draw_intersecting_lines(**params)
            elif diagram_type == "coordinate_system":
                return self.draw_coordinate_system(**params)
            elif diagram_type == "triangle":
                return self.draw_triangle(**params)
            elif diagram_type == "circle":
                return self.draw_circle(**params)
            elif diagram_type == "ellipse":
                return self.draw_ellipse(**params)
            elif diagram_type == "parabola":
                return self.draw_parabola(**params)
            elif diagram_type == "polygon":
                return self.draw_polygon(**params)
            elif diagram_type == "angle":
                return self.draw_angle(**params)
            elif diagram_type == "vector":
                return self.draw_vectors(**params)
            elif diagram_type == "histogram":
                return self.draw_histogram(**params)
            else:
                print(f"[DiagramFactory] 不支持的图形类型: {diagram_type}")
                return None
        except Exception as e:
            print(f"[DiagramFactory] 绘制图形失败: {e}")
            return None





def get_diagram_params_from_qwen(question_content: str) -> dict:
    """让 qwen-max 分析题目，返回图形参数"""
    
    client = LLMClient()
    
    prompt = DIAGRAM_ANALYSIS_PROMPT.format(
        question_content=question_content,
        diagram_types=DIAGRAM_TYPES_PROMPT
    )

    try:
        response = client.chat_simple([{"role": "user", "content": prompt}])
        
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        
        json_match = re.search(r'\{[\s\S]*\}', json_str)
        if json_match:
            json_str = json_match.group(0)
        
        result = json.loads(json_str.strip())
        return result
        
    except Exception as e:
        print(f"[PDF Tool] 获取图形参数失败: {e}")
        return {"need_diagram": False, "diagram_type": "none", "params": {}}


def generate_pdf_paper(original_question: str, knowledge_point: str, num_questions: int = 5) -> str:
    """根据原始题目生成变式题试卷"""
    
    deepseek_client = DeepSeekClient()
    diagram_factory = DiagramFactory()
    
    prompt = VARIANT_QUESTIONS_PROMPT.format(
        num_questions=num_questions,
        original_question=original_question,
        knowledge_point=knowledge_point
    )

    title = f"{knowledge_point} 变式题专项练习"
    questions = []
    
    try:
        response = deepseek_client.chat([{"role": "user", "content": prompt}])
        print(f"[PDF Tool] DeepSeek 原始响应: {response[:500]}...")
        
        json_str = response
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
        elif "```" in response:
            json_str = response.split("```")[1].split("```")[0]
        
        json_match = re.search(r'\{[\s\S]*\}', json_str)
        if json_match:
            json_str = json_match.group(0)
        
        paper_data = json.loads(json_str.strip())
        title = paper_data.get("title", title)
        questions = paper_data.get("questions", [])
        
        print(f"[PDF Tool] 成功解析，题目数: {len(questions)}")
        
    except Exception as e:
        print(f"[PDF Tool] DeepSeek 生成变式题失败: {e}")
        
        questions = [
            {"id": 1, "content": "请根据原始题目生成变式题。"},
        ]

    filename = f"Paper_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(settings.OUTPUTS_DIR, filename)
    
    os.makedirs(settings.OUTPUTS_DIR, exist_ok=True)
    
    c = canvas.Canvas(file_path, pagesize=A4)
    width, height = A4
    
    chinese_font = get_chinese_font()
    
    if chinese_font:
        c.setFont(chinese_font, 18)
    else:
        c.setFont("Helvetica", 18)
    
    c.drawCentredString(width/2, height - 2*cm, title)
    
    if chinese_font:
        c.setFont(chinese_font, 10)
    else:
        c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 3*cm, f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if chinese_font:
        c.setFont(chinese_font, 12)
    else:
        c.setFont("Helvetica", 12)
    
    y = height - 4*cm
    
    for i, q in enumerate(questions, 1):
        content = q.get("content", str(q))
        
        c.drawString(2*cm, y, f"{i}.")
        
        y -= 0.5*cm
        lines = wrap_text(content, width - 4*cm, c)
        for line in lines:
            if y < 2*cm:
                c.showPage()
                if chinese_font:
                    c.setFont(chinese_font, 12)
                else:
                    c.setFont("Helvetica", 12)
                y = height - 2*cm
            c.drawString(2.5*cm, y, line)
            y -= 0.6*cm
        
        print(f"[PDF Tool] 正在分析题目 {i} 的图形需求...")
        diagram_info = get_diagram_params_from_qwen(content)
        
        if diagram_info.get("need_diagram") and diagram_info.get("diagram_type") != "none":
            try:
                diagram_type = diagram_info.get("diagram_type")
                params = diagram_info.get("params", {})
                
                img_buf = diagram_factory.create_diagram(diagram_type, params)
                
                if img_buf and y > 5*cm:
                    temp_img_path = os.path.join(settings.TEMP_DIR, f"diagram_{i}.png")
                    with open(temp_img_path, 'wb') as f:
                        f.write(img_buf.getvalue())
                    
                    c.drawImage(temp_img_path, 3*cm, y - 4*cm, width=6*cm, height=4*cm)
                    y -= 4.5*cm
                    print(f"[PDF Tool] 题目 {i} 图形已绘制: {diagram_type}")
                    
            except Exception as e:
                print(f"[PDF Tool] 绘制图形失败: {e}")
        
        y -= 1*cm
    
    c.save()
    
    return f"""试卷已生成！

文件: {file_path}
标题: {title}
题目数: {len(questions)}

请用 PDF 阅读器打开查看。"""


def wrap_text(text, max_width, canvas_obj):
    """文本自动换行"""
    lines = []
    current_line = ""
    
    for char in text:
        test_line = current_line + char
        if canvas_obj.stringWidth(test_line, canvas_obj._fontname, canvas_obj._fontsize) < max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = char
    
    if current_line:
        lines.append(current_line)
    
    return lines if lines else [text]
