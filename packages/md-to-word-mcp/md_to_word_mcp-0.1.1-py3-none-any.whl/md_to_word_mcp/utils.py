#!/usr/bin/env python3
"""
工具函数
提供各种工具函数
"""

import os
from pathlib import Path
from typing import Dict, Any, Tuple


def validate_file_path(file_path: str) -> bool:
    """
    验证文件路径是否有效
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否有效
    """
    if not file_path:
        return False
    
    try:
        path = Path(file_path)
        return path.exists() and path.is_file()
    except Exception:
        return False


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        文件信息
    """
    if not validate_file_path(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")
    
    path = Path(file_path)
    stat = path.stat()
    
    return {
        "name": path.name,
        "path": str(path.absolute()),
        "size": stat.st_size,
        "extension": path.suffix.lower(),
        "modified": stat.st_mtime,
        "is_readable": os.access(path, os.R_OK)
    }


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 字节数
        
    Returns:
        格式化后的大小
    """
    if size_bytes == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def ensure_directory(directory_path: str) -> bool:
    """
    确保目录存在
    
    Args:
        directory_path: 目录路径
        
    Returns:
        是否成功
    """
    try:
        Path(directory_path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception:
        return False


def get_safe_filename(filename: str) -> str:
    """
    获取安全的文件名（移除不安全字符）
    
    Args:
        filename: 原始文件名
        
    Returns:
        安全的文件名
    """
    import re
    
    # 移除不安全字符
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # 限制长度
    if len(safe_filename) > 100:
        name, ext = os.path.splitext(safe_filename)
        safe_filename = name[:100-len(ext)] + ext
    
    return safe_filename


def generate_unique_filename(base_path: str, filename: str) -> str:
    """
    生成唯一的文件名（如果文件已存在）
    
    Args:
        base_path: 基础路径
        filename: 文件名
        
    Returns:
        唯一的文件名
    """
    base_dir = Path(base_path)
    name, ext = os.path.splitext(filename)
    
    counter = 1
    new_filename = filename
    
    while (base_dir / new_filename).exists():
        new_filename = f"{name}_{counter}{ext}"
        counter += 1
    
    return new_filename


def validate_markdown_content(content: str) -> Tuple[bool, list, list]:
    """
    验证 Markdown 内容
    
    Args:
        content: Markdown 内容
        
    Returns:
        (是否有效, 错误列表, 警告列表)
    """
    errors = []
    warnings = []
    
    if not content.strip():
        errors.append("内容为空")
        return False, errors, warnings
    
    lines = content.splitlines()
    
    # 检查是否有标题
    has_heading = any(line.strip().startswith('#') for line in lines)
    if not has_heading:
        warnings.append("没有发现标题标记 (#)")
    
    # 检查是否有内容
    content_lines = [line for line in lines if line.strip()]
    if len(content_lines) < 3:
        warnings.append("内容较少，可能不是完整的文档")
    
    # 检查编码问题
    try:
        content.encode('utf-8')
    except UnicodeEncodeError:
        errors.append("字符编码问题")
    
    is_valid = len(errors) == 0
    return is_valid, errors, warnings


def clean_temp_files(temp_dir: str = "./temp") -> int:
    """
    清理临时文件
    
    Args:
        temp_dir: 临时文件目录
        
    Returns:
        清理的文件数量
    """
    temp_path = Path(temp_dir)
    
    if not temp_path.exists():
        return 0
    
    cleaned_count = 0
    
    try:
        for file_path in temp_path.iterdir():
            if file_path.is_file():
                file_path.unlink()
                cleaned_count += 1
    except Exception:
        pass
    
    return cleaned_count


def get_supported_formats() -> Dict[str, list]:
    """
    获取支持的文件格式
    
    Returns:
        支持的格式列表
    """
    return {
        "input": [".md", ".markdown", ".txt"],
        "output": [".docx"],
        "template": [".docx", ".dotx"]
    }
