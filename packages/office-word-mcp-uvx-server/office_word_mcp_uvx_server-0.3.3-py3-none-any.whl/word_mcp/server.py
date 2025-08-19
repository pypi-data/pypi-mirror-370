"""Word MCP Server for manipulating Word documents."""

import logging
import os
import traceback
from pathlib import Path
from typing import Dict, Any, Optional, List

from fastmcp import FastMCP

# Import exceptions
from .exceptions import (
    ValidationError,
    DocumentError,
    SearchReplaceError,
    FileError
)

# Import functionality
from .search_and_replace_in_document import search_and_replace_in_document
from .get_document_xml import get_document_xml as get_doc_xml, get_document_xml_summary
from .find_text_in_document import find_text_in_document as find_text_in_doc
from .get_paragraph_text_from_document import get_paragraph_text_from_document as get_paragraph_text_from_doc, get_document_paragraphs_summary
from .create_document import create_document as create_doc
from .get_document_info import get_document_info as get_doc_info
from .get_document_text import get_document_text as get_doc_text
from .get_document_outline import get_document_outline as get_doc_outline
from .insert_header_near_text import insert_header_near_text as insert_header_near_text_func
from .insert_line_or_paragraph_near_text import insert_line_or_paragraph_near_text as insert_line_or_paragraph_near_text_func
from .add_paragraph import add_paragraph as add_paragraph_func
from .add_heading import add_heading as add_heading_func
from .add_picture import add_picture as add_picture_func
from .add_table import add_table as add_table_func
from .add_page_break import add_page_break as add_page_break_func
from .delete_paragraph import delete_paragraph as delete_paragraph_func
from .create_custom_style import create_custom_style as create_custom_style_func
from .format_text import format_text as format_text_func
from .format_table import format_table as format_table_func
from .protect_document import protect_document as protect_document_func
from .unprotect_document import unprotect_document as unprotect_document_func
from .add_footnote_to_document import add_footnote_to_document as add_footnote_to_document_func
from .add_endnote_to_document import add_endnote_to_document as add_endnote_to_document_func
from .customize_footnote_style import customize_footnote_style as customize_footnote_style_func

# Get project root directory path for log file path
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent

# Read version from VERSION file
def get_version() -> str:
    """读取项目根目录下VERSION文件中的版本号"""
    try:
        version_file = project_root / "VERSION"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                version = f.read().strip()
                return version
        else:
            # 如果VERSION文件不存在，返回默认版本号
            return "0.1.0"
    except Exception as e:
        # 如果读取失败，返回默认版本号
        print(f"Warning: Failed to read VERSION file: {e}")
        return "0.1.0"

# Initialize FastMCP server 
mcp = FastMCP(
    name="word-mcp",
    version=get_version()
)

# Set up logging and paths
LOG_FILE = project_root / "word-mcp.log"

# Initialize WORD_FILES_PATH variable without assigning a value
WORD_FILES_PATH = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE)
    ],
)
logger = logging.getLogger("word-mcp")


def get_word_path(filename: str) -> str:
    """
    获取 Word 文件的完整路径。

    Args:
        filename: Word 文件名

    Returns:
        Word 文件的完整路径

    Raises:
        ValueError: 当不是绝对路径时
    """
    # 强制要求绝对路径
    if not os.path.isabs(filename):
        raise ValueError(f"文件路径必须是绝对路径，当前路径: {filename}。任何时候都必须使用绝对路径。")

    return filename


@mcp.tool()
def search_and_replace(
    filepath: str,
    replacements: Dict[str, str]
) -> Dict[str, Any]:
    """
    在 Word 文档中搜索并替换文本。

    支持在普通段落和表格单元格中进行文本替换。

    Args:
        filepath: Word 文档文件路径（.docx 格式）
        replacements: 替换映射字典，键为要查找的文本，值为替换文本

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - total_replacements: 总替换次数
        - replacements_made: 执行的替换映射

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        SearchReplaceError: 当搜索替换操作失败时

    Example:
        search_and_replace(
            filepath="/path/to/document.docx",
            replacements={
                "%%name%%": "张三",
                "%%date%%": "2024-01-01",
                "%%amount%%": "1000"
            }
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 验证替换字典
        if not isinstance(replacements, dict):
            raise ValidationError("replacements 参数必须是字典类型")

        if not replacements:
            raise ValidationError("replacements 字典不能为空")

        # 执行搜索替换操作
        result = search_and_replace_in_document(full_path, replacements)

        logger.info(f"搜索替换操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError, SearchReplaceError) as e:
        logger.error(f"搜索替换操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise SearchReplaceError(f"未预期的错误: {str(e)}")


@mcp.tool()
def get_document_xml(
    filepath: str,
    summary_only: bool = False
) -> Dict[str, Any]:
    """
    获取 Word 文档的原始 XML 结构。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        summary_only: 是否只返回 XML 摘要信息（默认 False，返回完整 XML）

    Returns:
        包含 XML 结构信息的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - xml_structure: XML 结构信息
        - statistics: XML 统计信息

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        get_document_xml(
            filepath="/path/to/document.docx",
            summary_only=True
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 根据参数选择返回完整信息还是摘要
        if summary_only:
            result = get_document_xml_summary(full_path)
        else:
            result = get_doc_xml(full_path)

        logger.info(f"获取文档 XML 结构成功: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"获取文档 XML 结构失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def find_text_in_document(
    filepath: str,
    text_to_find: str,
    match_case: bool = True,
    whole_word: bool = False
) -> Dict[str, Any]:
    """
    在 Word 文档中查找特定文本的出现位置。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        text_to_find: 要查找的文本
        match_case: 是否区分大小写（默认 True）
        whole_word: 是否仅匹配完整单词（默认 False）

    Returns:
        包含查找结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - query: 查找的文本
        - match_case: 是否区分大小写
        - whole_word: 是否仅匹配完整单词
        - occurrences: 查找结果列表
        - total_count: 总计找到的次数

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时

    Example:
        find_text_in_document(
            filepath="/path/to/document.docx",
            text_to_find="标准值",
            match_case=False,
            whole_word=True
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 验证查找参数
        if not isinstance(text_to_find, str):
            raise ValidationError("text_to_find 参数必须是字符串类型")

        if not text_to_find.strip():
            raise ValidationError("查找文本不能为空")

        # 执行文本查找操作
        result = find_text_in_doc(full_path, text_to_find, match_case, whole_word)

        logger.info(f"文本查找操作成功完成: {full_path}, 查找文本: '{text_to_find}', 找到 {result.get('total_count', 0)} 处匹配")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"文本查找操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def get_paragraph_text_from_document(
    filepath: str,
    paragraph_index: int
) -> Dict[str, Any]:
    """
    从 Word 文档中获取特定段落的文本。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        paragraph_index: 段落索引（从0开始）

    Returns:
        包含段落信息的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - paragraph_index: 段落索引
        - paragraph_text: 段落文本内容
        - paragraph_style: 段落样式名称
        - is_heading: 是否为标题段落
        - total_paragraphs: 文档总段落数
        - character_count: 段落字符数
        - word_count: 段落词数（按空格分割）

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时

    Example:
        get_paragraph_text_from_document(
            filepath="/path/to/document.docx",
            paragraph_index=5
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 验证段落索引参数
        if not isinstance(paragraph_index, int):
            raise ValidationError("paragraph_index 参数必须是整数类型")

        if paragraph_index < 0:
            raise ValidationError("段落索引必须是非负整数（从0开始）")

        # 执行获取段落文本操作
        result = get_paragraph_text_from_doc(full_path, paragraph_index)

        logger.info(f"段落文本获取操作成功完成: {full_path}, 段落索引: {paragraph_index}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"段落文本获取操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def create_document(
    filepath: str,
    title: str = None,
    author: str = None
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

    Example:
        create_document(
            filepath="/path/to/new_document.docx",
            title="我的文档",
            author="张三"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行创建文档操作
        result = create_doc(full_path, title, author)

        logger.info(f"文档创建操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"文档创建操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def get_document_info(filepath: str) -> Dict[str, Any]:
    """
    获取Word文档的详细信息，包括属性、统计信息等。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）

    Returns:
        包含文档信息的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - title: 文档标题
        - author: 文档作者
        - subject: 文档主题
        - keywords: 关键词
        - created: 创建时间
        - modified: 修改时间
        - last_modified_by: 最后修改者
        - revision: 修订版本
        - page_count: 页数（近似值：章节数）
        - word_count: 总字数
        - paragraph_count: 段落数
        - table_count: 表格数
        - file_size: 文件大小（字节）

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        get_document_info(
            filepath="/path/to/document.docx"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行获取文档信息操作
        result = get_doc_info(full_path)

        logger.info(f"获取文档信息操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"获取文档信息操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def get_document_text(filepath: str) -> Dict[str, Any]:
    """
    从Word文档中提取所有文本内容，包括段落和表格中的文本。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）

    Returns:
        包含文档文本的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - text: 提取的所有文本内容
        - paragraph_count: 段落数量
        - table_count: 表格数量
        - total_characters: 总字符数
        - total_words: 总词数

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        get_document_text(
            filepath="/path/to/document.docx"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行获取文档文本操作
        result = get_doc_text(full_path)

        logger.info(f"获取文档文本操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"获取文档文本操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def get_document_outline(filepath: str) -> Dict[str, Any]:
    """
    获取Word文档的结构大纲，包括段落和表格的结构信息。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）

    Returns:
        包含文档结构的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - outline: 文档结构大纲
        - summary: 结构统计摘要

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        get_document_outline(
            filepath="/path/to/document.docx"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行获取文档结构大纲操作
        result = get_doc_outline(full_path)

        logger.info(f"获取文档结构大纲操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"获取文档结构大纲操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def insert_header_near_text(
    filepath: str,
    target_text: str,
    header_title: str,
    position: str = 'after',
    header_style: str = 'Heading 1'
) -> Dict[str, Any]:
    """
    在包含目标文本的第一个段落之前或之后插入标题。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        target_text: 要查找的目标文本
        header_title: 要插入的标题文本
        position: 插入位置，'before' 或 'after'（默认 'after'）
        header_style: 标题样式名称（默认 'Heading 1'）

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - target_text: 目标文本
        - header_title: 插入的标题
        - position: 插入位置
        - header_style: 使用的标题样式
        - found: 是否找到目标文本

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        insert_header_near_text(
            filepath="/path/to/document.docx",
            target_text="第一章",
            header_title="章节概述",
            position="after",
            header_style="Heading 2"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行插入标题操作
        result = insert_header_near_text_func(full_path, target_text, header_title, position, header_style)

        logger.info(f"插入标题操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"插入标题操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def insert_line_or_paragraph_near_text(
    filepath: str,
    target_text: str,
    line_text: str,
    position: str = 'after',
    line_style: str = None
) -> Dict[str, Any]:
    """
    在包含目标文本的第一个段落之前或之后插入新的行或段落。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        target_text: 要查找的目标文本
        line_text: 要插入的行或段落文本
        position: 插入位置，'before' 或 'after'（默认 'after'）
        line_style: 段落样式名称，如果为None则使用目标段落的样式

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - target_text: 目标文本
        - line_text: 插入的文本
        - position: 插入位置
        - line_style: 使用的样式
        - found: 是否找到目标文本

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        insert_line_or_paragraph_near_text(
            filepath="/path/to/document.docx",
            target_text="结论",
            line_text="以上是详细分析。",
            position="before"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行插入段落操作
        result = insert_line_or_paragraph_near_text_func(full_path, target_text, line_text, position, line_style)

        logger.info(f"插入段落操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"插入段落操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def add_paragraph(
    filepath: str,
    text: str,
    style: str = None
) -> Dict[str, Any]:
    """
    向Word文档添加一个新段落。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        text: 段落文本内容
        style: 可选的段落样式名称

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - text: 添加的文本
        - style: 使用的样式
        - text_length: 文本长度
        - word_count: 词数

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        add_paragraph(
            filepath="/path/to/document.docx",
            text="这是一个新的段落，包含重要信息。",
            style="Normal"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行添加段落操作
        result = add_paragraph_func(full_path, text, style)

        logger.info(f"添加段落操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"添加段落操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def add_heading(
    filepath: str,
    text: str,
    level: int = 1
) -> Dict[str, Any]:
    """
    向Word文档添加一个新标题。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        text: 标题文本内容
        level: 标题级别（1-9，其中1是最高级别）

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - text: 添加的标题文本
        - level: 标题级别
        - style_used: 实际使用的样式
        - text_length: 文本长度
        - word_count: 词数

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        add_heading(
            filepath="/path/to/document.docx",
            text="第一章 概述",
            level=1
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行添加标题操作
        result = add_heading_func(full_path, text, level)

        logger.info(f"添加标题操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"添加标题操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def add_picture(
    filepath: str,
    image_path: str,
    width: float = None
) -> Dict[str, Any]:
    """
    向Word文档添加一张图片。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        image_path: 图片文件路径（必须是绝对路径）
        width: 可选的图片宽度（英寸），如果不指定则使用原始大小

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - image_path: 图片路径
        - width: 图片宽度（英寸）
        - image_size: 图片文件大小（KB）
        - image_format: 图片格式

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        add_picture(
            filepath="/path/to/document.docx",
            image_path="/path/to/image.png",
            width=5.0
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行添加图片操作
        result = add_picture_func(full_path, image_path, width)

        logger.info(f"添加图片操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"添加图片操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def add_table(
    filepath: str,
    rows: int,
    cols: int,
    data: Optional[List[List[str]]] = None
) -> Dict[str, Any]:
    """
    向Word文档添加一个表格。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        rows: 表格行数
        cols: 表格列数
        data: 可选的二维数据数组来填充表格

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - rows: 表格行数
        - cols: 表格列数
        - data_provided: 是否提供了数据
        - cells_filled: 填充的单元格数量

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        add_table(
            filepath="/path/to/document.docx",
            rows=3,
            cols=2,
            data=[["列1", "列2"], ["数据1", "数据2"], ["数据3", "数据4"]]
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行添加表格操作
        result = add_table_func(full_path, rows, cols, data)

        logger.info(f"添加表格操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"添加表格操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def add_page_break(filepath: str) -> Dict[str, Any]:
    """
    向Word文档添加一个分页符。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - page_break_added: 是否成功添加分页符

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        add_page_break(
            filepath="/path/to/document.docx"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行添加分页符操作
        result = add_page_break_func(full_path)

        logger.info(f"添加分页符操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"添加分页符操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def delete_paragraph(
    filepath: str,
    paragraph_index: int
) -> Dict[str, Any]:
    """
    从Word文档中删除指定的段落。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        paragraph_index: 要删除的段落索引（从0开始）

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - paragraph_index: 删除的段落索引
        - paragraph_text: 被删除段落的文本（前50个字符）
        - total_paragraphs_before: 删除前的段落总数
        - total_paragraphs_after: 删除后的段落总数

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        delete_paragraph(
            filepath="/path/to/document.docx",
            paragraph_index=2
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行删除段落操作
        result = delete_paragraph_func(full_path, paragraph_index)

        logger.info(f"删除段落操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"删除段落操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def create_custom_style(
    filepath: str,
    style_name: str,
    bold: bool = None,
    italic: bool = None,
    font_size: int = None,
    font_name: str = None,
    color: str = None,
    base_style: str = None
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

    Example:
        create_custom_style(
            filepath="/path/to/document.docx",
            style_name="重要提示",
            bold=True,
            color="red",
            font_size=14
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行创建自定义样式操作
        result = create_custom_style_func(full_path, style_name, bold, italic, font_size, font_name, color, base_style)

        logger.info(f"创建自定义样式操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"创建自定义样式操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def format_text(
    filepath: str,
    paragraph_index: int,
    start_pos: int,
    end_pos: int,
    bold: bool = None,
    italic: bool = None,
    underline: bool = None,
    color: str = None,
    font_size: int = None,
    font_name: str = None
) -> Dict[str, Any]:
    """
    格式化段落中指定范围的文本。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        paragraph_index: 段落索引（从0开始）
        start_pos: 文本开始位置
        end_pos: 文本结束位置
        bold: 是否加粗（True/False）
        italic: 是否斜体（True/False）
        underline: 是否下划线（True/False）
        color: 文字颜色（如'red', 'blue'等）
        font_size: 字体大小（点数）
        font_name: 字体名称

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - paragraph_index: 段落索引
        - target_text: 格式化的文本
        - format_applied: 应用的格式
        - start_pos: 开始位置
        - end_pos: 结束位置

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        format_text(
            filepath="/path/to/document.docx",
            paragraph_index=0,
            start_pos=0,
            end_pos=5,
            bold=True,
            color="red"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行格式化文本操作
        result = format_text_func(full_path, paragraph_index, start_pos, end_pos, bold, italic, underline, color, font_size, font_name)

        logger.info(f"格式化文本操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"格式化文本操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def format_table(
    filepath: str,
    table_index: int,
    has_header_row: Optional[bool] = None,
    border_style: Optional[str] = None,
    shading: Optional[List[List[str]]] = None
) -> Dict[str, Any]:
    """
    格式化Word文档中的表格，包括边框、底纹和结构。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        table_index: 表格索引（从0开始）
        has_header_row: 是否将第一行格式化为标题行
        border_style: 边框样式（'none', 'single', 'double', 'thick'）
        shading: 二维列表，指定每个单元格的背景色

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - table_index: 表格索引
        - formatting_applied: 应用的格式选项
        - table_size: 表格大小（行x列）

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        format_table(
            filepath="/path/to/document.docx",
            table_index=0,
            has_header_row=True,
            border_style="single",
            shading=[["lightgray", "white"], ["white", "lightgray"]]
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行格式化表格操作
        result = format_table_func(full_path, table_index, has_header_row, border_style, shading)

        logger.info(f"格式化表格操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"格式化表格操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def protect_document(
    filepath: str,
    password: str
) -> Dict[str, Any]:
    """
    为Word文档添加密码保护（简化版本）。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        password: 保护密码

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - protection_type: 保护类型
        - password_hash: 密码哈希（用于验证）
        - metadata_file: 元数据文件路径

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        protect_document(
            filepath="/path/to/document.docx",
            password="mypassword123"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行保护文档操作
        result = protect_document_func(full_path, password)

        logger.info(f"保护文档操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"保护文档操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def unprotect_document(
    filepath: str,
    password: str
) -> Dict[str, Any]:
    """
    解除Word文档的密码保护（简化版本）。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        password: 保护密码

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - was_protected: 是否之前被保护
        - metadata_removed: 是否移除了元数据文件

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        unprotect_document(
            filepath="/path/to/document.docx",
            password="mypassword123"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行解除保护操作
        result = unprotect_document_func(full_path, password)

        logger.info(f"解除文档保护操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"解除文档保护操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def add_footnote_to_document(
    filepath: str,
    paragraph_index: int,
    footnote_text: str
) -> Dict[str, Any]:
    """
    向Word文档的指定段落添加脚注。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        paragraph_index: 段落索引（从0开始）
        footnote_text: 脚注文本内容

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - paragraph_index: 段落索引
        - footnote_text: 脚注文本
        - footnote_number: 脚注编号
        - method_used: 使用的实现方法

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        add_footnote_to_document(
            filepath="/path/to/document.docx",
            paragraph_index=0,
            footnote_text="这是一个脚注说明。"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行添加脚注操作
        result = add_footnote_to_document_func(full_path, paragraph_index, footnote_text)

        logger.info(f"添加脚注操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"添加脚注操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def add_endnote_to_document(
    filepath: str,
    paragraph_index: int,
    endnote_text: str
) -> Dict[str, Any]:
    """
    向Word文档的指定段落添加尾注。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        paragraph_index: 段落索引（从0开始）
        endnote_text: 尾注文本内容

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - paragraph_index: 段落索引
        - endnote_text: 尾注文本
        - endnote_number: 尾注编号
        - endnote_symbol: 使用的尾注符号

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        add_endnote_to_document(
            filepath="/path/to/document.docx",
            paragraph_index=0,
            endnote_text="这是一个尾注说明。"
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行添加尾注操作
        result = add_endnote_to_document_func(full_path, paragraph_index, endnote_text)

        logger.info(f"添加尾注操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"添加尾注操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


@mcp.tool()
def customize_footnote_style(
    filepath: str,
    numbering_format: str = "1, 2, 3",
    start_number: int = 1,
    font_name: str = None,
    font_size: int = None
) -> Dict[str, Any]:
    """
    自定义Word文档中脚注的编号和格式。

    Args:
        filepath: Word 文档文件路径（.docx 格式，必须是绝对路径）
        numbering_format: 编号格式（"1, 2, 3", "i, ii, iii", "a, b, c", "*, **, ***"）
        start_number: 起始编号
        font_name: 可选的字体名称
        font_size: 可选的字体大小（点数）

    Returns:
        包含操作结果的字典，包括：
        - message: 操作结果消息
        - file_path: 文件路径
        - numbering_format: 编号格式
        - start_number: 起始编号
        - footnotes_updated: 更新的脚注数量
        - style_applied: 是否应用了字体样式

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
        ValidationError: 当参数验证失败时

    Example:
        customize_footnote_style(
            filepath="/path/to/document.docx",
            numbering_format="i, ii, iii",
            start_number=1,
            font_name="Arial",
            font_size=9
        )
    """
    try:
        # 获取完整文件路径
        full_path = get_word_path(filepath)

        # 执行自定义脚注样式操作
        result = customize_footnote_style_func(full_path, numbering_format, start_number, font_name, font_size)

        logger.info(f"自定义脚注样式操作成功完成: {full_path}")
        return result

    except (ValidationError, FileError, DocumentError) as e:
        logger.error(f"自定义脚注样式操作失败: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"未预期的错误: {str(e)}")
        raise DocumentError(f"未预期的错误: {str(e)}")


def main():
    """主入口函数"""
    mcp.run()


if __name__ == "__main__":
    main()