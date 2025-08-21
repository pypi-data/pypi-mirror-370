# encoding: utf-8
# @File  : pdf_writer1_0.py
# @Author: ronin.G
# @Date  : 2025/08/21/14:44

from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import re
import os

# ============ 新增：PDF 二次处理 ============
try:
    from PyPDF2 import PdfReader, PdfWriter
except ImportError:
    raise ImportError("请安装 PyPDF2: pip install PyPDF2")

class YTracker:
    def __init__(self, start_y, page_height, margin):
        self.current_y = start_y
        self.page_height = page_height
        self.margin = margin

    def add_text_height(self, line_count, line_height):
        height_used = line_count * line_height
        self.current_y -= height_used
        return height_used

    def add_fixed_height(self, height):
        self.current_y -= height
        return height

    def get_y(self):
        return self.current_y

    def set_y(self, y):
        self.current_y = y

    def check_new_page(self):
        """检查是否需要换页"""
        if self.current_y <= self.margin:
            return True
        return False

    def reset_for_new_page(self):
        """重置Y坐标为新页顶部"""
        self.current_y = self.page_height - self.margin


class SimplePDFDocument:
    def __init__(self, filename, pagesize, margin=50, font_name="semibold", font_size=20,header_size = 10,header=None, footer=None):
        """
        :param filename: PDF 文件名
        :param pagesize: 页面大小，如 A4, landscape(A4)
        :param margin: 边距
        :param font_name: 字体名（需已注册）
        :param font_size: 字号
        :param header_size 页眉字号
        :param header: 页眉文本，支持 {page} {total}，如 "第 {page} 页，共 {total} 页"
        :param footer: 页脚文本，支持 {page} {total}
        """
        self.filename = filename
        self.pagesize = pagesize
        self.margin = margin
        self.font_name = font_name
        self.font_size = font_size
        self.header_size = header_size
        self.line_height = font_size + 6
        self.width, self.height = pagesize
        self.text_width = self.width - 2 * margin

        # 页眉页脚
        self.header_text = header
        self.footer_text = footer

        # 创建临时画布
        self.c = canvas.Canvas(filename + ".tmp.pdf", pagesize=pagesize)
        self.c.setFont(font_name, font_size)

        # Y 坐标管理器
        self.y_tracker = YTracker(start_y=self.height - margin, page_height=self.height, margin=self.margin)

        # 清理零宽字符
        self._clean_text = lambda text: re.sub(r'[\u200b-\u200f\u202a-\u202e]', '', text)

        # 页面计数
        self.page_count = 0

        # 开始第一页
        self._start_new_page()

    def add_cover_page(self,title,subtitle=None,note=None,
                       title_font_size=36,subtitle_font_size=24,note_font_size=14,
                       title_font_name=None,subtitle_font_name=None,note_font_name=None):
        """
        添加封面页到当前页面（通常是第一页）
        """
        # 使用默认字体
        title_font_name = title_font_name or self.font_name
        subtitle_font_name = subtitle_font_name or self.font_name
        note_font_name = note_font_name or self.font_name

        # === 关键：不要 new_page()，直接使用当前页面 ===

        # 垂直居中布局
        center_y = self.height / 2
        line_spacing = 40

        y = center_y + line_spacing  # 主标题位置

        # 清除可能已有的内容（比如页眉/页脚占位）—— 可选
        # 实际上 canvas 没有“清除”，我们只需确保不提前画东西即可

        # 设置字体并绘制主标题
        self.c.setFont(title_font_name,title_font_size)
        title_width = self.c.stringWidth(title,title_font_name,title_font_size)
        x = (self.width - title_width) / 2
        self.c.drawString(x,y,title)

        # 副标题
        if subtitle:
            y -= line_spacing
            self.c.setFont(subtitle_font_name,subtitle_font_size)
            subtitle_width = self.c.stringWidth(subtitle,subtitle_font_name,subtitle_font_size)
            x = (self.width - subtitle_width) / 2
            self.c.drawString(x,y,subtitle)

        # 注释
        if note:
            y -= line_spacing * 1.5
            self.c.setFont(note_font_name,note_font_size)
            note_width = self.c.stringWidth(note,note_font_name,note_font_size)
            x = (self.width - note_width) / 2
            self.c.drawString(x,y,note)

        # 更新 Y 跟踪器，防止后续内容重叠
        self.y_tracker.set_y(y - 50)

        # ✅ 关键：手动标记当前页为“封面”，避免在 save() 中给封面加页眉页脚
        self.is_first_page_cover = True  # 添加标记
    def _start_new_page(self):
        """开始一个新页面"""
        if self.page_count > 0:
            self.c.showPage()

        self.page_count += 1
        self.c.setFont(self.font_name, self.font_size)
        self.y_tracker.reset_for_new_page()

        # # === 绘制页眉：放在最顶部中间 === 跟下边save()里边的重复了，先注释掉
        # if self.header_text:
        #     header = self.header_text.format(page=self.page_count, total="?")
        #     y_pos = self.height - self.margin + 25  # 调整 +10 控制上下位置
        #     self._draw_text_center(header, y_pos, font_size=self.font_size - 4)
        #
        # # === 绘制页脚占位（临时）===
        # if self.footer_text:
        #     footer = self.footer_text.format(page=self.page_count, total="?")
        #     self._draw_text_center(footer, self.margin - 15, font_size=self.font_size - 4)

    def _draw_text_center(self, text, y, font_size=None):
        """在主画布上居中绘制文本"""
        if font_size is None:
            font_size = self.font_size
        self.c.setFont(self.font_name, font_size)
        text_width = self.c.stringWidth(text, self.font_name, font_size)
        x = (self.width - text_width) / 2
        self.c.drawString(x, y, text)

    def _wrap_text(self, text, max_width):
        """返回文本的行列表"""
        from reportlab.pdfbase.pdfmetrics import stringWidth
        lines = []
        current_line = ""
        for char in text:
            test_line = current_line + char
            if stringWidth(test_line, self.font_name, self.font_size) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        return lines

    def _handle_new_page(self):
        """处理换页逻辑"""
        if self.y_tracker.check_new_page():
            self._start_new_page()

    def new_page(self):
        """手动插入新页面"""
        self._start_new_page()
        print(f"📄 已手动创建新页面 (第 {self.page_count} 页)")

    def add_paragraph(self, text, align="left"):
        self._handle_new_page()
        text = self._clean_text(text)
        lines = self._wrap_text(text, self.text_width)
        line_count = len(lines)

        x = self.margin
        if align == "center":
            x = (self.width - self.text_width) / 2
        elif align == "right":
            x = self.width - self.margin - self.text_width

        text_obj = self.c.beginText(x, self.y_tracker.get_y())
        text_obj.setFont(self.font_name, self.font_size)
        for line in lines:
            text_obj.textLine(line)
        self.c.drawText(text_obj)

        self.y_tracker.add_text_height(line_count, self.line_height)

    def add_image(self, image_path, width=300, align="left", space_after=18):
        self._handle_new_page()
        try:
            img = ImageReader(image_path)
            img_width, img_height = img.getSize()
            aspect = img_height / img_width
            display_width = width
            display_height = width * aspect

            x = self.margin
            if align == "center":
                x = (self.width - display_width) / 2
            elif align == "right":
                x = self.width - self.margin - display_width

            y = self.y_tracker.get_y() - display_height
            self.c.drawImage(image_path, x, y, width=display_width, height=display_height,
                             preserveAspectRatio=True, mask='auto')
            self.y_tracker.add_fixed_height(display_height + space_after)
        except Exception as e:
            print(f"[警告] 图片加载失败: {image_path}, 错误: {e}")
            self.y_tracker.add_fixed_height(100 + space_after)

    def add_spacing(self, height):
        self.y_tracker.add_fixed_height(height)

    def save(self):
        """保存 PDF，注入总页数"""
        self.c.save()
        temp_pdf = self.filename + ".tmp.pdf"

        # 如果没有页眉页脚，直接重命名
        if not self.header_text and not self.footer_text:
            os.rename(temp_pdf, self.filename)
            print(f"✅ PDF 已保存: {self.filename}")
            return

        # 读取临时 PDF
        reader = PdfReader(temp_pdf)
        total_pages = len(reader.pages)
        output = PdfWriter()

        # 为每一页注入页眉页脚
        for i in range(total_pages):
            page = reader.pages[i]
            from reportlab.pdfgen import canvas
            from io import BytesIO
            packet = BytesIO()
            c = canvas.Canvas(packet, pagesize=self.pagesize)

            # 设置字体
            try:
                c.setFont(self.font_name, self.font_size - 4)
            except Exception:
                c.setFont("Helvetica", self.font_size - 4)

            # === 绘制页眉：最顶部中间 ===
            if self.header_text:
                header = self.header_text.format(page=i+1, total=total_pages)
                y_pos = self.height - self.margin + 25
                self._draw_text_center_pdf(c, header, y_pos)

            # === 绘制页脚：底部中间 ===
            if self.footer_text:
                footer = self.footer_text.format(page=i+1, total=total_pages)
                y_pos = self.margin - 15
                self._draw_text_center_pdf(c, footer, y_pos)

            c.save()
            packet.seek(0)
            overlay = PdfReader(packet).pages[0]
            page.merge_page(overlay)
            output.add_page(page)

        # 写入最终文件
        with open(self.filename, "wb") as f:
            output.write(f)

        # 删除临时文件
        os.remove(temp_pdf)
        print(f"✅ PDF 已保存: {self.filename} (共 {total_pages} 页)")

    def _draw_text_center_pdf(self, c, text, y):
        """在外部 canvas 上居中绘制文本（安全版）"""
        font_name = self.font_name
        font_size = self.header_size # self.font_size - 4

        # 显式设置字体
        try:
            c.setFont(font_name, font_size)
        except Exception:
            c.setFont("Helvetica", font_size)

        # 使用一致的字体计算宽度
        actual_font = c._fontname
        actual_size = c._fontsize
        text_width = c.stringWidth(text, actual_font, actual_size)
        x = (self.width - text_width) / 2
        c.drawString(x, y, text)