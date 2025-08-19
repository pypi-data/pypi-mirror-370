"""获取 Word 文档 XML 结构功能模块。"""

import logging
import os
from typing import Dict, Any
import xml.etree.ElementTree as ET

from docx import Document

from .exceptions import DocumentError, FileError

logger = logging.getLogger(__name__)


def get_document_xml(filepath: str) -> Dict[str, Any]:
    """
    获取 Word 文档的原始 XML 结构。

    Args:
        filepath: Word 文档文件路径

    Returns:
        包含 XML 结构信息的字典

    Raises:
        FileError: 当文件不存在或格式不支持时
        DocumentError: 当文档操作失败时
    """
    try:
        # 验证是否为绝对路径
        if not os.path.isabs(filepath):
            raise FileError(f"文件路径必须是绝对路径，当前路径: {filepath}。任何时候都必须使用绝对路径。")

        # 检查文件是否存在
        if not os.path.exists(filepath):
            raise FileError(f"文件不存在: {filepath}。请确认文件路径正确，任何时候都必须使用绝对路径。")

        if not filepath.lower().endswith('.docx'):
            raise FileError(f"不支持的文件格式，仅支持 .docx 文件: {filepath}。任何时候都必须使用绝对路径。")

        # 打开文档
        try:
            doc = Document(filepath)
        except Exception as e:
            raise DocumentError(f"无法打开文档 {filepath}: {str(e)}")

        # 获取文档的 XML 内容
        try:
            # 获取主文档的 XML
            document_xml = doc.element.xml

            # 解析 XML 以获取结构信息
            root = ET.fromstring(document_xml)

            # 提取 XML 结构信息
            xml_info = {
                "root_tag": root.tag,
                "namespaces": dict(root.attrib) if root.attrib else {},
                "child_elements": [],
                "raw_xml": document_xml
            }

            # 获取子元素信息
            for child in root:
                child_info = {
                    "tag": child.tag,
                    "attributes": dict(child.attrib) if child.attrib else {},
                    "text": child.text.strip() if child.text else None,
                    "child_count": len(list(child))
                }
                xml_info["child_elements"].append(child_info)

            # 统计信息
            stats = {
                "total_elements": len(list(root.iter())),
                "direct_children": len(list(root)),
                "xml_size": len(document_xml),
                "has_text_content": any(elem.text and elem.text.strip() for elem in root.iter())
            }

            logger.info(f"成功获取文档 {filepath} 的 XML 结构")

            return {
                "message": "成功获取文档 XML 结构",
                "file_path": filepath,
                "xml_structure": xml_info,
                "statistics": stats
            }

        except ET.ParseError as e:
            raise DocumentError(f"XML 解析失败: {str(e)}")
        except Exception as e:
            raise DocumentError(f"获取 XML 结构失败: {str(e)}")

    except (FileError, DocumentError) as e:
        logger.error(str(e))
        raise
    except Exception as e:
        logger.error(f"获取文档 XML 失败: {str(e)}")
        raise DocumentError(f"获取文档 XML 失败: {str(e)}")


def get_document_xml_summary(filepath: str) -> Dict[str, Any]:
    """
    获取 Word 文档 XML 的摘要信息（不包含完整 XML 内容）。

    Args:
        filepath: Word 文档文件路径

    Returns:
        包含 XML 摘要信息的字典
    """
    try:
        # 获取完整 XML 信息
        full_info = get_document_xml(filepath)

        # 移除大量的原始 XML 内容，只保留摘要
        summary_info = full_info.copy()

        # 只保留 XML 结构的摘要，不包含完整的原始 XML
        if "xml_structure" in summary_info:
            xml_structure = summary_info["xml_structure"].copy()

            # 移除完整的 raw_xml，只保留前500个字符作为预览
            if "raw_xml" in xml_structure:
                raw_xml = xml_structure["raw_xml"]
                if len(raw_xml) > 500:
                    xml_structure["raw_xml_preview"] = raw_xml[:500] + "..."
                    xml_structure["raw_xml_truncated"] = True
                else:
                    xml_structure["raw_xml_preview"] = raw_xml
                    xml_structure["raw_xml_truncated"] = False

                # 删除完整的 raw_xml
                del xml_structure["raw_xml"]

            # 限制子元素信息的数量
            if "child_elements" in xml_structure and len(xml_structure["child_elements"]) > 10:
                xml_structure["child_elements_preview"] = xml_structure["child_elements"][:10]
                xml_structure["child_elements_truncated"] = True
                xml_structure["total_child_elements"] = len(xml_structure["child_elements"])
                del xml_structure["child_elements"]
            else:
                xml_structure["child_elements_preview"] = xml_structure.get("child_elements", [])
                xml_structure["child_elements_truncated"] = False
                if "child_elements" in xml_structure:
                    del xml_structure["child_elements"]

            summary_info["xml_structure"] = xml_structure

        summary_info["message"] = "成功获取文档 XML 摘要"

        return summary_info

    except Exception as e:
        logger.error(f"获取文档 XML 摘要失败: {str(e)}")
        raise
