#!/usr/bin/env python3
"""独立的 Word 搜索替换服务器，不依赖 MCP 框架"""

import json
import sys
import os
from typing import Dict, Any

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from word_mcp.search_replace import search_and_replace_in_document
from word_mcp.exceptions import ValidationError, FileError, DocumentError, SearchReplaceError


def handle_search_and_replace(params: Dict[str, Any]) -> Dict[str, Any]:
    """处理搜索替换请求"""
    try:
        filepath = params.get('filepath')
        replacements = params.get('replacements')

        if not filepath:
            raise ValidationError("filepath 参数是必需的")

        if not replacements:
            raise ValidationError("replacements 参数是必需的")

        if not isinstance(replacements, dict):
            raise ValidationError("replacements 必须是字典类型")

        # 执行搜索替换
        result = search_and_replace_in_document(filepath, replacements)

        return {
            "success": True,
            "data": result
        }

    except (ValidationError, FileError, DocumentError, SearchReplaceError) as e:
        return {
            "success": False,
            "error": str(e),
            "error_type": type(e).__name__
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"未预期的错误: {str(e)}",
            "error_type": "UnexpectedError"
        }


def main():
    """主函数 - 简单的命令行接口"""
    print("🚀 Word MCP 独立服务器启动")
    print("输入 JSON 格式的请求，或输入 'quit' 退出")
    print("示例请求格式:")
    example = {
        "action": "search_and_replace",
        "params": {
            "filepath": "/path/to/document.docx",
            "replacements": {
                "%%name%%": "张三",
                "%%date%%": "2024-01-01"
            }
        }
    }
    print(json.dumps(example, ensure_ascii=False, indent=2))
    print("-" * 50)

    while True:
        try:
            user_input = input("\n请输入请求 > ").strip()

            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 再见!")
                break

            if not user_input:
                continue

            # 解析 JSON 请求
            try:
                request = json.loads(user_input)
            except json.JSONDecodeError as e:
                print(f"❌ JSON 格式错误: {e}")
                continue

            # 处理请求
            action = request.get('action')
            params = request.get('params', {})

            if action == 'search_and_replace':
                result = handle_search_and_replace(params)
                print("\n📋 响应:")
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print(f"❌ 不支持的操作: {action}")
                print("支持的操作: search_and_replace")

        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出")
            break
        except Exception as e:
            print(f"❌ 处理请求时出错: {e}")


if __name__ == "__main__":
    main()