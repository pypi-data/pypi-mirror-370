"""Excel转Markdown MCP服务器

这个MCP服务器提供将Excel (.xlsx) 文件转换为Markdown格式的功能。
"""

import asyncio
import tempfile
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from markitdown import MarkItDown


# 创建MCP服务器实例
server = Server("excel-to-markdown-mcp")

# 初始化MarkItDown转换器
markitdown = MarkItDown()


@server.list_tools()
async def list_tools() -> list[Tool]:
    """列出可用的工具"""
    return [
        Tool(
            name="xlsx-to-markdown",
            description="将Excel (.xlsx) 文件转换为Markdown格式，支持多工作表和复杂表格结构",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "要转换的Excel文件的绝对路径 (.xlsx格式)"
                    },
                    "sheet_name": {
                        "type": "string",
                        "description": "指定要转换的工作表名称（可选，默认转换所有工作表）"
                    }
                },
                "required": ["filepath"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    """处理工具调用"""
    if name != "xlsx-to-markdown":
        raise ValueError(f"未知工具: {name}")

    filepath = arguments.get("filepath")
    sheet_name = arguments.get("sheet_name")
    
    if not filepath:
        raise ValueError("缺少必需参数: filepath")

    try:
        # 验证文件是否存在
        file_path = Path(filepath)
        if not file_path.exists():
            raise FileNotFoundError(f"文件不存在: {filepath}")

        # 验证文件是否为Excel格式
        valid_extensions = ['.xlsx', '.xls']
        if file_path.suffix.lower() not in valid_extensions:
            raise ValueError(f"文件必须是Excel格式 ({', '.join(valid_extensions)})")

        # 转换Excel到Markdown
        result = markitdown.convert(str(file_path))
        
        # 如果指定了工作表名称，添加到结果描述中
        description = "Excel转换成功！"
        if sheet_name:
            description += f" (指定工作表: {sheet_name})"
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.md', 
            delete=False, 
            encoding='utf-8'
        ) as temp_file:
            temp_file.write(result.text_content)
            temp_path = temp_file.name

        return [
            TextContent(
                type="text",
                text=f"{description}\n输出文件: {temp_path}"
            ),
            TextContent(
                type="text",
                text="转换后的Markdown内容:"
            ),
            TextContent(
                type="text",
                text=result.text_content
            )
        ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"错误: {str(e)}"
            )
        ]


async def async_main():
    """启动MCP服务器"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """入口点函数"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()