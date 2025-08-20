"""
HTML模板加载器
用于加载和处理HTML模板文件
"""

import os
from pathlib import Path

def load_template(template_name: str, **kwargs) -> str:
    """
    加载HTML模板文件并替换变量
    
    Args:
        template_name: 模板文件名（不包含路径）
        **kwargs: 要替换的变量键值对
    
    Returns:
        处理后的HTML内容
    """
    template_path = Path("templates") / template_name
    
    if not template_path.exists():
        raise FileNotFoundError(f"模板文件未找到: {template_path}")
    
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 替换模板变量
    for key, value in kwargs.items():
        placeholder = "{" + key + "}"
        content = content.replace(placeholder, str(value))
    
    return content

def template_exists(template_name: str) -> bool:
    """
    检查模板文件是否存在
    
    Args:
        template_name: 模板文件名
    
    Returns:
        是否存在
    """
    template_path = Path("templates") / template_name
    return template_path.exists() 