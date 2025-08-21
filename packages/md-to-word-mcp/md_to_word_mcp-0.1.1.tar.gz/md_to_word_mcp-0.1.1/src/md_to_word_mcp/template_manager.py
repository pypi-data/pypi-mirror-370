#!/usr/bin/env python3
"""
模板管理器
管理 Word 文档模板
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional


class TemplateManager:
    """
    Word 模板管理器
    """
    
    def __init__(self, template_dir: str = "."):
        self.template_dir = Path(template_dir)
        self.supported_extensions = [".docx", ".dotx"]
    
    def initialize(self):
        """
        初始化模板管理器
        """
        # 确保模板目录存在
        self.template_dir.mkdir(parents=True, exist_ok=True)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """
        列出所有可用模板
        
        Returns:
            模板信息列表
        """
        templates = []
        
        for ext in self.supported_extensions:
            for template_file in self.template_dir.glob(f"*{ext}"):
                if template_file.is_file():
                    templates.append({
                        "name": template_file.name,
                        "path": str(template_file),
                        "size": template_file.stat().st_size,
                        "extension": ext,
                        "modified": template_file.stat().st_mtime
                    })
        
        # 按修改时间排序
        templates.sort(key=lambda x: x["modified"], reverse=True)
        
        return templates
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        获取模板详细信息
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板信息或 None
        """
        templates = self.list_templates()
        
        for template in templates:
            if template["name"] == template_name:
                return template
        
        return None
    
    def get_template_path(self, template_name: str) -> Optional[str]:
        """
        获取模板文件路径
        
        Args:
            template_name: 模板名称
            
        Returns:
            模板路径或 None
        """
        template_info = self.get_template_info(template_name)
        
        if template_info:
            return template_info["path"]
        
        return None
    
    def validate_template(self, template_path: str) -> Dict[str, Any]:
        """
        验证模板文件
        
        Args:
            template_path: 模板文件路径
            
        Returns:
            验证结果
        """
        template_file = Path(template_path)
        
        result = {
            "is_valid": False,
            "path": template_path,
            "errors": [],
            "warnings": []
        }
        
        # 检查文件是否存在
        if not template_file.exists():
            result["errors"].append(f"模板文件不存在: {template_path}")
            return result
        
        # 检查文件扩展名
        if template_file.suffix.lower() not in self.supported_extensions:
            result["errors"].append(
                f"不支持的模板格式: {template_file.suffix} "
                f"(支持: {', '.join(self.supported_extensions)})"
            )
            return result
        
        # 检查文件大小
        file_size = template_file.stat().st_size
        if file_size == 0:
            result["errors"].append("模板文件为空")
            return result
        
        if file_size > 100 * 1024 * 1024:  # 100MB
            result["warnings"].append(f"模板文件较大: {file_size} bytes")
        
        # 检查文件是否可读
        try:
            with open(template_file, 'rb') as f:
                # 读取文件头部分验证格式
                header = f.read(8)
                if not header.startswith(b'PK'):  # ZIP 格式的标志
                    result["warnings"].append("模板文件格式可能不正确")
        except Exception as e:
            result["errors"].append(f"无法读取模板文件: {str(e)}")
            return result
        
        # 如果没有错误，模板有效
        if not result["errors"]:
            result["is_valid"] = True
            result["size"] = file_size
            result["name"] = template_file.name
        
        return result
    
    def add_template(self, source_path: str, template_name: Optional[str] = None) -> Dict[str, Any]:
        """
        添加新模板
        
        Args:
            source_path: 源模板文件路径
            template_name: 新模板名称（可选）
            
        Returns:
            添加结果
        """
        source_file = Path(source_path)
        
        # 验证源文件
        validation_result = self.validate_template(source_path)
        if not validation_result["is_valid"]:
            return {
                "success": False,
                "errors": validation_result["errors"]
            }
        
        # 确定目标文件名
        if template_name:
            # 确保扩展名正确
            if not template_name.endswith(source_file.suffix):
                template_name += source_file.suffix
        else:
            template_name = source_file.name
        
        target_path = self.template_dir / template_name
        
        try:
            # 复制模板文件
            import shutil
            shutil.copy2(source_path, target_path)
            
            return {
                "success": True,
                "template_name": template_name,
                "template_path": str(target_path),
                "size": target_path.stat().st_size
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [f"复制模板文件失败: {str(e)}"]
            }
    
    def remove_template(self, template_name: str) -> Dict[str, Any]:
        """
        删除模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            删除结果
        """
        template_info = self.get_template_info(template_name)
        
        if not template_info:
            return {
                "success": False,
                "errors": [f"模板不存在: {template_name}"]
            }
        
        try:
            template_file = Path(template_info["path"])
            template_file.unlink()
            
            return {
                "success": True,
                "template_name": template_name
            }
            
        except Exception as e:
            return {
                "success": False,
                "errors": [f"删除模板失败: {str(e)}"]
            }
    
    def get_default_template(self) -> Optional[str]:
        """
        获取默认模板路径
        
        Returns:
            默认模板路径或 None
        """
        # 查找常见的默认模板名称
        default_names = [
            "product_manual_black.docx",
            "default.docx",
            "template.docx",
            "reference.docx"
        ]
        
        for name in default_names:
            template_path = self.get_template_path(name)
            if template_path:
                return template_path
        
        # 如果没有找到，返回第一个可用模板
        templates = self.list_templates()
        if templates:
            return templates[0]["path"]
        
        return None
