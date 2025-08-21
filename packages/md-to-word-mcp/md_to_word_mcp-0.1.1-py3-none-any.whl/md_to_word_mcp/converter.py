#!/usr/bin/env python3
"""
Markdown 转 Word 转换器
封装 pypandoc 功能，提供更友好的接口
"""

import os
import time
from pathlib import Path
from typing import Dict, Any, Optional

import pypandoc


class MarkdownToWordConverter:
    """
    Markdown 转 Word 转换器
    """
    
    def __init__(self):
        self.default_template = "product_manual_black.docx"
        self.sample_contents = {
            "product_manual": self._get_product_manual_content(),
            "technical_doc": self._get_technical_doc_content(),
            "user_guide": self._get_user_guide_content()
        }
    
    def convert(self, 
                input_file: str, 
                output_file: str = "output.docx",
                template_path: Optional[str] = None,
                title: Optional[str] = None,
                author: Optional[str] = None) -> Dict[str, Any]:
        """
        转换 Markdown 文件为 Word 文档
        
        Args:
            input_file: 输入的 Markdown 文件路径
            output_file: 输出的 Word 文件路径
            template_path: Word 模板文件路径
            title: 文档标题
            author: 文档作者
            
        Returns:
            转换结果信息
        """
        start_time = time.time()
        
        # 验证输入文件
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"输入文件不存在: {input_file}")
        
        # 确定模板路径
        if template_path:
            if not os.path.exists(template_path):
                raise FileNotFoundError(f"模板文件不存在: {template_path}")
        else:
            # 使用默认模板
            template_path = self.default_template
            if not os.path.exists(template_path):
                template_path = None
        
        # 准备 pandoc 参数
        extra_args = []
        if template_path:
            extra_args.append(f"--reference-doc={template_path}")
        
        if title:
            extra_args.extend(["--metadata", f"title={title}"])
            
        if author:
            extra_args.extend(["--metadata", f"author={author}"])
        
        try:
            # 执行转换
            pypandoc.convert_file(
                input_file,
                'docx',
                outputfile=output_file,
                extra_args=extra_args
            )
            
            # 获取输出文件信息
            output_size = os.path.getsize(output_file)
            processing_time = round(time.time() - start_time, 2)
            
            return {
                "input_file": input_file,
                "output_file": output_file,
                "template": template_path or "default",
                "size": output_size,
                "processing_time": processing_time,
                "title": title,
                "author": author
            }
            
        except Exception as e:
            raise RuntimeError(f"转换失败: {str(e)}")
    
    def create_sample_markdown(self, 
                             filename: str = "sample.md",
                             content_type: str = "product_manual",
                             custom_content: Optional[str] = None) -> Dict[str, Any]:
        """
        创建示例 Markdown 文件
        
        Args:
            filename: 输出文件名
            content_type: 内容类型
            custom_content: 自定义内容
            
        Returns:
            创建结果信息
        """
        if custom_content:
            content = custom_content
        elif content_type in self.sample_contents:
            content = self.sample_contents[content_type]
        else:
            raise ValueError(f"不支持的内容类型: {content_type}")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(content)
            
            file_size = os.path.getsize(filename)
            
            return {
                "filename": filename,
                "content_type": content_type,
                "size": file_size
            }
            
        except Exception as e:
            raise RuntimeError(f"创建文件失败: {str(e)}")
    
    def validate_markdown(self, file_path: str) -> Dict[str, Any]:
        """
        验证 Markdown 文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            验证结果
        """
        if not os.path.exists(file_path):
            return {
                "is_valid": False,
                "errors": [f"文件不存在: {file_path}"]
            }
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            file_size = os.path.getsize(file_path)
            line_count = len(content.splitlines())
            
            warnings = []
            errors = []
            
            # 检查文件内容
            if not content.strip():
                errors.append("文件为空")
            
            # 检查 Markdown 标记
            if not any(line.startswith('#') for line in content.splitlines()):
                warnings.append("没有发现标题标记 (#)")
            
            # 检查文件大小
            if file_size > 10 * 1024 * 1024:  # 10MB
                warnings.append(f"文件较大: {file_size} bytes")
            
            return {
                "is_valid": len(errors) == 0,
                "size": file_size,
                "lines": line_count,
                "warnings": warnings,
                "errors": errors
            }
            
        except Exception as e:
            return {
                "is_valid": False,
                "errors": [f"读取文件失败: {str(e)}"]
            }
    
    def _get_product_manual_content(self) -> str:
        """获取产品手册示例内容"""
        return """# 产品使用说明书

## 产品概述

产品名称: SuperConverter Pro  
版本: 2.0.1  
发布日期: 2024年1月

## 快速开始

### 安装步骤

1. 下载安装包
2. 运行安装程序
3. 按照向导完成安装
4. 启动应用程序

### 基本操作

#### 文件转换

1. 选择文件: 点击"选择文件"按钮
2. 选择格式: 从下拉菜单选择目标格式
3. 开始转换: 点击"转换"按钮

注意: 转换大文件可能需要较长时间

#### 批量处理

支持同时转换多个文件：

- 支持拖拽文件
- 支持文件夹选择
- 支持通配符匹配

## 常见问题

Q: 为什么转换失败？  
A: 请检查文件格式是否支持。

Q: 如何提高转换速度？  
A: 可以在设置中启用多线程处理。
"""
    
    def _get_technical_doc_content(self) -> str:
        """获取技术文档示例内容"""
        return """# 技术文档

## 项目概述

本项目是一个高性能的 Markdown 转 Word 工具。

## 架构设计

### 核心组件

- **Converter**: 转换引擎
- **TemplateManager**: 模板管理器
- **Utils**: 工具函数

### 数据流

```
Markdown 文件 → Parser → Converter → Word 文档
```

## API 参考

### convert()

转换 Markdown 文件为 Word 文档。

**参数:**
- `input_file`: 输入文件路径
- `output_file`: 输出文件路径
- `template_path`: 模板文件路径

**返回值:**
- 转换结果信息

## 配置说明

### 环境变量

- `MAX_FILE_SIZE`: 最大文件大小
- `OUTPUT_DIR`: 输出目录

### 配置文件

```json
{
  "default_template": "template.docx",
  "output_dir": "./output"
}
```
"""
    
    def _get_user_guide_content(self) -> str:
        """获取用户指南示例内容"""
        return """# 用户指南

欢迎使用 Markdown 转 Word 工具！

## 入门教程

### 第一步：准备文件

请准备一个 Markdown 文件，可以是 .md 或 .markdown 格式。

### 第二步：选择模板

可以选择预定义的模板，或使用自定义模板。

### 第三步：开始转换

点击转换按钮，等待转换完成。

## 高级用法

### 自定义模板

您可以创建自己的 Word 模板，并在转换时使用。

### 批量处理

支持一次处理多个文件，提高工作效率。

## 常见问题解答

**Q: 支持哪些文件格式？**

A: 支持 .md、.markdown、.txt 格式。

**Q: 转换后的文档在哪里？**

A: 默认保存在当前目录，也可以指定输出路径。

**Q: 如何自定义样式？**

A: 可以使用自己的 Word 模板文件来定制样式。

---

希望这个工具能够帮助您提高工作效率！
"""
