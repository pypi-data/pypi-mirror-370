#!/usr/bin/env python3
"""Office Word MCP Server 命令行入口"""

import asyncio
import typer
from pathlib import Path

def get_version() -> str:
    """读取版本号 - 尝试多种方式"""
    try:
        # 方法1：尝试从 importlib.metadata 获取版本（推荐方式）
        try:
            import importlib.metadata
            return importlib.metadata.version("office-word-mcp-uvx-server")
        except (ImportError, importlib.metadata.PackageNotFoundError):
            pass

        # 方法2：尝试从项目根目录的 VERSION 文件读取
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        version_file = project_root / "VERSION"
        if version_file.exists():
            with open(version_file, 'r', encoding='utf-8') as f:
                return f.read().strip()

        # 方法3：尝试从安装包的相对路径读取
        for parent in [current_dir.parent, current_dir.parent.parent, current_dir.parent.parent.parent]:
            version_file = parent / "VERSION"
            if version_file.exists():
                with open(version_file, 'r', encoding='utf-8') as f:
                    return f.read().strip()

        return "0.3.2"  # 默认版本号
    except Exception:
        return "0.3.2"

def version_callback(value: bool):
    if value:
        version = get_version()
        typer.echo(f"Office Word MCP Server v{version}")
        raise typer.Exit()

app = typer.Typer(
    help=f"""Office Word MCP Server v{get_version()}

🏢 Word 文档操作 MCP 服务器
一个基于 FastMCP 框架的 Word 文档操作服务器，允许 AI 代理创建、读取和修改 Word 文档，无需安装 Microsoft Word。

🚀 技术栈:
  • FastMCP: 2.10.6 - MCP 服务器框架
  • python-docx: 0.8.11+ - Word 文档操作库
  • Python: >= 3.11

✨ 已实现的 24 项功能:

📝 文档操作基础功能 (4项):
  • create_document            - 创建新的 Word 文档
  • get_document_info          - 获取文档信息
  • get_document_text          - 提取文档文本
  • get_document_outline       - 获取文档结构

✏️ 内容插入功能 (5项):
  • insert_header_near_text    - 在指定文本附近插入标题
  • insert_line_or_paragraph_near_text - 在指定文本附近插入段落
  • add_paragraph              - 添加新段落
  • add_heading                - 添加新标题
  • add_picture                - 添加图片

📊 表格和格式功能 (6项):
  • add_table                  - 添加表格
  • add_page_break             - 添加分页符
  • delete_paragraph           - 删除段落
  • create_custom_style        - 创建自定义样式
  • format_text                - 格式化文本
  • format_table               - 格式化表格

🔒 文档保护功能 (2项):
  • protect_document           - 文档密码保护
  • unprotect_document         - 解除文档保护

📋 脚注和尾注功能 (3项):
  • add_footnote_to_document   - 添加脚注
  • add_endnote_to_document    - 添加尾注
  • customize_footnote_style   - 自定义脚注样式

🔍 搜索和替换功能 (4项):
  • search_and_replace         - 搜索并替换文本
  • find_text_in_document      - 查找文本位置
  • get_document_xml           - 获取文档XML结构
  • get_paragraph_text_from_document - 获取段落文本

⚠️ 重要提醒:
  • 所有文件路径必须使用绝对路径
  • 支持 .docx 格式的 Word 文档
  • 需要 Python 3.11 或更高版本

🌐 项目地址: https://pypi.org/project/office-word-mcp-uvx-server/
📖 技术支持: FastMCP 框架 - https://gofastmcp.com
""",
    add_completion=False
)

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", "-V",
        callback=version_callback,
        is_eager=True,
        help="显示版本信息并退出"
    )
):
    """Office Word MCP Server - Word 文档操作服务器

    默认启动 stdio 模式，可以使用子命令选择其他模式。
    """
    # 如果没有子命令，默认启动 stdio 模式
    if ctx.invoked_subcommand is None:
        stdio()

@app.command()
def stdio():
    """启动 Word MCP Server (默认 stdio 模式)"""
    version = get_version()
    print(f"🚀 Office Word MCP Server v{version} - STDIO 模式启动")
    print("=" * 60)
    print("📝 支持 24 项 Word 文档操作功能")
    print("🔗 等待 MCP 客户端连接...")
    print("按 Ctrl+C 退出")
    print()

    try:
        from .server import mcp
        mcp.run()
    except KeyboardInterrupt:
        print("\n👋 关闭服务器...")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("✅ 服务已停止")

@app.command()
def standalone():
    """启动独立搜索替换服务器"""
    version = get_version()
    print(f"🚀 Word MCP 独立服务器 v{version} 启动")
    print("=" * 50)
    print("仅支持搜索替换功能的独立服务器")
    print("按 Ctrl+C 退出")
    print()

    try:
        from .standalone_server import main as standalone_main
        standalone_main()
    except KeyboardInterrupt:
        print("\n👋 关闭服务器...")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("✅ 服务已停止")

# 默认行为在 main() 回调中处理

if __name__ == "__main__":
    app()