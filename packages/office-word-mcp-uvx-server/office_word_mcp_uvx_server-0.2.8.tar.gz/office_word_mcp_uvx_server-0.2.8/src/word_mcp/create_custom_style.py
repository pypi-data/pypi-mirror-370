"""在Word文档中创建自定义样式的功能模块。"""

import os
from typing import Dict, Any, Optional
from docx import Document
from docx.shared import Pt, RGBColor
from docx.enum.style import WD_STYLE_TYPE
from .exceptions import FileError, DocumentError, ValidationError


def create_custom_style(
    filepath: str,
    style_name: str,
    bold: Optional[bool] = None,
    italic: Optional[bool] = None,
    font_size: Optional[int] = None,
    font_name: Optional[str] = None,
    color: Optional[str] = None,
    base_style: Optional[str] = None
) -> Dict[str, Any]:
    """
    在Word文档中创建一个自定义样式。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        style_name: 新样式的名称
        bold: 是否加粗（True/False）
        italic: 是否斜体（True/False）
        font_size: 字体大小（点数）
        font_name: 字体名称
        color: 文字颜色（如'red', 'blue'等）
        base_style: 基于的现有样式名称

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - style_name: 创建的样式名称
        - properties: 样式属性
        - base_style: 基于的样式

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时
    """
    try:
        # 验证参数
        if not filepath:
            raise ValidationError("文件路径不能为空")

        if not style_name:
            raise ValidationError("样式名称不能为空")

        if not style_name.strip():
            raise ValidationError("样式名称不能只包含空格")

        # 验证字体大小
        if font_size is not None:
            try:
                font_size = int(font_size)
                if font_size <= 0 or font_size > 200:
                    raise ValidationError("字体大小必须在1-200之间")
            except (ValueError, TypeError):
                raise ValidationError("字体大小必须是整数")

        # 检查文件是否存在
        if not os.path.exists(filepath):
            raise FileError(f"文件不存在: {filepath}")

        # 检查文件扩展名
        if not filepath.lower().endswith('.docx'):
            raise FileError("文件格式不支持，只支持.docx格式")

        # 检查文件是否可写
        if not os.access(filepath, os.W_OK):
            raise FileError(f"文件不可写: {filepath}")

        # 打开文档
        doc = Document(filepath)

        # 检查样式是否已存在
        existing_styles = [style.name for style in doc.styles]
        if style_name in existing_styles:
            raise ValidationError(f"样式'{style_name}'已存在")

        # 验证基础样式是否存在
        if base_style and base_style not in existing_styles:
            raise ValidationError(f"基础样式'{base_style}'不存在")

        # 创建样式
        try:
            # 创建段落样式
            style = doc.styles.add_style(style_name, WD_STYLE_TYPE.PARAGRAPH)

            # 设置基础样式
            if base_style:
                try:
                    style.base_style = doc.styles[base_style]
                except:
                    # 如果设置基础样式失败，继续创建
                    pass

            # 设置字体属性
            font = style.font

            if bold is not None:
                font.bold = bold

            if italic is not None:
                font.italic = italic

            if font_size is not None:
                font.size = Pt(font_size)

            if font_name:
                font.name = font_name

            if color:
                # 定义常见颜色映射
                color_map = {
                    'red': RGBColor(255, 0, 0),
                    'blue': RGBColor(0, 0, 255),
                    'green': RGBColor(0, 128, 0),
                    'yellow': RGBColor(255, 255, 0),
                    'black': RGBColor(0, 0, 0),
                    'gray': RGBColor(128, 128, 128),
                    'grey': RGBColor(128, 128, 128),
                    'white': RGBColor(255, 255, 255),
                    'purple': RGBColor(128, 0, 128),
                    'orange': RGBColor(255, 165, 0),
                    'brown': RGBColor(165, 42, 42),
                    'pink': RGBColor(255, 192, 203)
                }

                try:
                    if color.lower() in color_map:
                        font.color.rgb = color_map[color.lower()]
                    else:
                        # 尝试从字符串解析RGB颜色
                        font.color.rgb = RGBColor.from_string(color)
                except Exception:
                    # 如果颜色设置失败，保持默认颜色
                    pass

        except Exception as e:
            raise DocumentError(f"创建样式时发生错误: {str(e)}")

        # 保存文档
        doc.save(filepath)

        # 构建样式属性信息
        properties = {}
        if bold is not None:
            properties['bold'] = bold
        if italic is not None:
            properties['italic'] = italic
        if font_size is not None:
            properties['font_size'] = font_size
        if font_name:
            properties['font_name'] = font_name
        if color:
            properties['color'] = color

        return {
            "message": f"成功创建自定义样式: {style_name}",
            "file_path": filepath,
            "style_name": style_name,
            "properties": properties,
            "base_style": base_style or "无"
        }

    except (FileError, ValidationError) as e:
        raise
    except Exception as e:
        raise DocumentError(f"创建自定义样式时发生错误: {str(e)}")