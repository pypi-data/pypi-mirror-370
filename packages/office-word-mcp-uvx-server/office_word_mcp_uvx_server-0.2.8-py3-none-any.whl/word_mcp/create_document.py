"""创建新Word文档的功能模块。"""

import os
from typing import Dict, Any, Optional
from docx import Document
from .exceptions import FileError, DocumentError, ValidationError


def create_document(
    filepath: str,
    title: Optional[str] = None,
    author: Optional[str] = None
) -> Dict[str, Any]:
    """
    创建一个带有可选元数据的新 Word 文档。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        title: 可选的文档标题
        author: 可选的文档作者

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - title: 文档标题
        - author: 文档作者
        - created: 是否成功创建

    Raises:
        FileError: 当文件操作失败时
        DocumentError: 当文档创建失败时
        ValidationError: 当参数验证失败时
    """
    try:
        # 验证文件路径
        if not filepath:
            raise ValidationError("文件路径不能为空")

        # 确保文件有.docx扩展名
        if not filepath.endswith('.docx'):
            filepath = filepath + '.docx'

        # 检查文件是否已存在
        if os.path.exists(filepath):
            raise FileError(f"文件已存在: {filepath}")

        # 检查目录是否存在且可写
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
            except OSError as e:
                raise FileError(f"无法创建目录: {directory}, 错误: {str(e)}")

        if directory and not os.access(directory, os.W_OK):
            raise FileError(f"目录不可写: {directory}")

        # 创建新文档
        doc = Document()

        # 设置文档属性
        if title:
            doc.core_properties.title = title
        if author:
            doc.core_properties.author = author

        # 保存文档
        doc.save(filepath)

        return {
            "message": f"文档创建成功: {filepath}",
            "file_path": filepath,
            "title": title or "",
            "author": author or "",
            "created": True
        }

    except (FileError, ValidationError) as e:
        raise
    except Exception as e:
        raise DocumentError(f"创建文档时发生错误: {str(e)}")