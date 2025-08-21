#!/usr/bin/env python3
"""
Markdown 转 Word MCP 服务器
提供 Markdown 转 Word 文档的功能，支持自定义模板
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

import asyncio
from mcp.server import NotificationOptions, Server
from mcp.types import Resource, Tool, TextContent

# 兼容不同版本的 mcp：有的版本提供 InitializationOptions，有的直接使用字符串签名
try:
    from mcp.server.models import InitializationOptions  # type: ignore
except Exception:  # pragma: no cover - 运行时兼容
    InitializationOptions = None  # type: ignore

from .converter import MarkdownToWordConverter
from .template_manager import TemplateManager
from .utils import validate_file_path, get_file_info

app = Server("md-to-word")

# 全局配置
config = {
    "default_template": "product_manual_black.docx",
    "output_dir": "./output",
    "max_file_size": 50 * 1024 * 1024,  # 50MB
    "supported_formats": [".md", ".markdown", ".txt"]
}

# 初始化转换器和模板管理器
converter = MarkdownToWordConverter()
template_manager = TemplateManager()


@app.list_resources()
async def handle_list_resources() -> List[Resource]:
    """列出可用的模板资源"""
    resources = []
    
    # 列出可用模板
    templates = template_manager.list_templates()
    for template in templates:
        resources.append(
            Resource(
                uri=f"template://{template['name']}",
                name=f"Word模板: {template['name']}",
                description=f"Word文档模板，大小: {template['size']} bytes",
                mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        )
    
    return resources


@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """读取资源内容"""
    if uri.startswith("template://"):
        template_name = uri.replace("template://", "")
        template_info = template_manager.get_template_info(template_name)
        if template_info:
            return json.dumps(template_info, ensure_ascii=False, indent=2)
    
    raise ValueError(f"未知的资源 URI: {uri}")


@app.list_tools()
async def handle_list_tools() -> List[Tool]:
    """列出可用工具"""
    return [
        Tool(
            name="convert_md_to_word",
            description="将 Markdown 文件转换为 Word 文档",
            inputSchema={
                "type": "object",
                "properties": {
                    "input_file": {
                        "type": "string",
                        "description": "输入的 Markdown 文件路径"
                    },
                    "output_file": {
                        "type": "string", 
                        "description": "输出的 Word 文件路径（可选）",
                        "default": "output.docx"
                    },
                    "template": {
                        "type": "string",
                        "description": "Word 模板文件路径（可选）",
                        "default": "product_manual_black.docx"
                    },
                    "title": {
                        "type": "string",
                        "description": "文档标题（可选）"
                    },
                    "author": {
                        "type": "string", 
                        "description": "文档作者（可选）"
                    }
                },
                "required": ["input_file"]
            }
        ),
        Tool(
            name="create_markdown_sample",
            description="创建示例 Markdown 文件",
            inputSchema={
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "输出文件名",
                        "default": "sample.md"
                    },
                    "content_type": {
                        "type": "string",
                        "description": "内容类型",
                        "enum": ["product_manual", "technical_doc", "user_guide", "custom"],
                        "default": "product_manual"
                    },
                    "custom_content": {
                        "type": "string",
                        "description": "自定义内容（当 content_type 为 custom 时）"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="list_templates",
            description="列出可用的 Word 模板",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="validate_markdown",
            description="验证 Markdown 文件格式和内容",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Markdown 文件路径"
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """处理工具调用"""
    try:
        if name == "convert_md_to_word":
            return await handle_convert_md_to_word(arguments)
        elif name == "create_markdown_sample":
            return await handle_create_markdown_sample(arguments)
        elif name == "list_templates":
            return await handle_list_templates(arguments)
        elif name == "validate_markdown":
            return await handle_validate_markdown(arguments)
        else:
            raise ValueError(f"未知工具: {name}")
            
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 错误: {str(e)}"
        )]


async def handle_convert_md_to_word(arguments: Dict[str, Any]) -> List[TextContent]:
    """处理 Markdown 转 Word 转换"""
    input_file = arguments.get("input_file")
    output_file = arguments.get("output_file", "output.docx")
    template = arguments.get("template", "product_manual_black.docx")
    title = arguments.get("title")
    author = arguments.get("author")
    
    # 验证输入文件
    if not validate_file_path(input_file):
        return [TextContent(
            type="text", 
            text=f"❌ 输入文件不存在或无法访问: {input_file}"
        )]
    
    # 检查文件大小
    file_info = get_file_info(input_file)
    if file_info["size"] > config["max_file_size"]:
        return [TextContent(
            type="text",
            text=f"❌ 文件太大: {file_info['size']} bytes (最大 {config['max_file_size']} bytes)"
        )]
    
    # 检查文件格式
    file_ext = Path(input_file).suffix.lower()
    if file_ext not in config["supported_formats"]:
        return [TextContent(
            type="text",
            text=f"❌ 不支持的文件格式: {file_ext} (支持: {', '.join(config['supported_formats'])})"
        )]
    
    # 执行转换
    try:
        result = converter.convert(
            input_file=input_file,
            output_file=output_file,
            template_path=template,
            title=title,
            author=author
        )
        
        return [TextContent(
            type="text",
            text=f"✅ 转换成功!\n\n" +
                 f"📁 输入文件: {result['input_file']}\n" +
                 f"📄 输出文件: {result['output_file']}\n" +
                 f"📊 文件大小: {result['size']} bytes\n" +
                 f"🎨 模板: {result.get('template', 'default')}\n" +
                 f"⏱️ 处理时间: {result.get('processing_time', 'N/A')} 秒"
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 转换失败: {str(e)}"
        )]


async def handle_create_markdown_sample(arguments: Dict[str, Any]) -> List[TextContent]:
    """创建示例 Markdown 文件"""
    filename = arguments.get("filename", "sample.md")
    content_type = arguments.get("content_type", "product_manual")
    custom_content = arguments.get("custom_content")
    
    try:
        result = converter.create_sample_markdown(
            filename=filename,
            content_type=content_type,
            custom_content=custom_content
        )
        
        return [TextContent(
            type="text",
            text=f"✅ 示例文件创建成功!\n\n" +
                 f"📁 文件: {result['filename']}\n" +
                 f"📊 大小: {result['size']} bytes\n" +
                 f"📝 类型: {result['content_type']}"
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 创建示例文件失败: {str(e)}"
        )]


async def handle_list_templates(arguments: Dict[str, Any]) -> List[TextContent]:
    """列出可用模板"""
    try:
        templates = template_manager.list_templates()
        
        if not templates:
            return [TextContent(
                type="text",
                text="📋 当前没有可用的模板文件"
            )]
        
        template_list = "\n".join([
            f"• {t['name']} ({t['size']} bytes)"
            for t in templates
        ])
        
        return [TextContent(
            type="text",
            text=f"📋 可用模板 ({len(templates)} 个):\n\n{template_list}"
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 获取模板列表失败: {str(e)}"
        )]


async def handle_validate_markdown(arguments: Dict[str, Any]) -> List[TextContent]:
    """验证 Markdown 文件"""
    file_path = arguments.get("file_path")
    
    if not validate_file_path(file_path):
        return [TextContent(
            type="text",
            text=f"❌ 文件不存在或无法访问: {file_path}"
        )]
    
    try:
        validation_result = converter.validate_markdown(file_path)
        
        status = "✅ 有效" if validation_result["is_valid"] else "❌ 无效"
        
        result_text = f"📋 Markdown 文件验证结果\n\n" +\
                     f"📁 文件: {file_path}\n" +\
                     f"📊 状态: {status}\n" +\
                     f"📏 大小: {validation_result['size']} bytes\n" +\
                     f"📄 行数: {validation_result.get('lines', 'N/A')}\n"
        
        if validation_result.get("warnings"):
            result_text += f"⚠️ 警告:\n" + "\n".join(
                f"  • {w}" for w in validation_result["warnings"]
            )
        
        if validation_result.get("errors"):
            result_text += f"❌ 错误:\n" + "\n".join(
                f"  • {e}" for e in validation_result["errors"]
            )
        
        return [TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"❌ 验证失败: {str(e)}"
        )]


async def main():
    """启动 MCP 服务器"""
    # 初始化配置
    template_manager.initialize()
    
    # 创建输出目录
    os.makedirs(config["output_dir"], exist_ok=True)
    
    # 运行服务器
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
          capabilities = app.get_capabilities(
              notification_options=NotificationOptions(),
              experimental_capabilities={}
          )

          # 新版：支持 InitializationOptions；旧版：使用 (name, version, capabilities)
          if InitializationOptions is not None:
              await app.run(
                  read_stream,
                  write_stream,
                  InitializationOptions(
                      server_name="md-to-word",
                      server_version="1.0.0",
                      capabilities=capabilities,
                  ),
              )
          else:
              await app.run(
                  read_stream,
                  write_stream,
                  "md-to-word",
                  "1.0.0",
                  capabilities,
              )


if __name__ == "__main__":
    asyncio.run(main())
