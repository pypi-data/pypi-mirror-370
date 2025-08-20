"""
静态文件管理器
用于处理静态资源文件，支持开发环境和打包后环境
"""

import os
import sys
from pathlib import Path
from typing import Optional
import mimetypes

def _get_static_file_path(file_path: str) -> Optional[Path]:
    """
    获取静态文件的绝对路径，支持开发环境和打包后环境
    
    Args:
        file_path: 相对于static目录的文件路径
        
    Returns:
        静态文件的绝对路径，如果找不到则返回 None
    """
    # 方法1: 优先尝试相对于当前文件的路径（开发环境）
    current_dir = Path(__file__).parent
    static_file_path = current_dir / "static" / file_path
    
    if static_file_path.exists():
        return static_file_path
    
    # 方法2: 尝试相对于工作目录的路径
    static_file_path = Path("static") / file_path
    if static_file_path.exists():
        return static_file_path
    
    # 方法3: 尝试从系统路径中寻找
    possible_paths = [
        Path.cwd() / "static" / file_path,
        Path(__file__).parent.parent / "static" / file_path,
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None

def _get_static_content_from_resources(file_path: str) -> Optional[bytes]:
    """
    尝试使用 importlib.resources 从包中读取静态文件内容
    
    Args:
        file_path: 相对于static目录的文件路径
        
    Returns:
        文件内容的字节数据，如果失败则返回 None
    """
    try:
        # Python 3.9+ 的新 API
        try:
            from importlib.resources import files
            # 尝试多种包名
            package_names = ["xiaohongshu_automation", ".", __name__.split('.')[0] if '.' in __name__ else __name__]
            
            for package_name in package_names:
                try:
                    file_content = (files(package_name) / "static" / file_path).read_bytes()
                    return file_content
                except Exception:
                    continue
        except (ImportError, AttributeError):
            # Python 3.7-3.8 的兼容 API
            import importlib.resources as resources
            try:
                file_content = resources.read_binary("xiaohongshu_automation.static", file_path.replace('/', '.'))
                return file_content
            except Exception:
                pass
    except Exception:
        pass
    
    return None

def get_static_file_content(file_path: str) -> Optional[tuple[bytes, str]]:
    """
    获取静态文件内容和MIME类型
    
    Args:
        file_path: 相对于static目录的文件路径
        
    Returns:
        (文件内容字节数据, MIME类型) 或 None
    """
    content = None
    
    # 首先尝试从包资源中读取
    content = _get_static_content_from_resources(file_path)
    
    if content is None:
        # 尝试从文件系统读取
        static_path = _get_static_file_path(file_path)
        if static_path:
            try:
                with open(static_path, "rb") as f:
                    content = f.read()
            except Exception:
                pass
    
    if content is None:
        return None
    
    # 获取MIME类型
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is None:
        # 设置默认MIME类型
        ext = Path(file_path).suffix.lower()
        mime_type_map = {
            '.js': 'application/javascript',
            '.css': 'text/css',
            '.html': 'text/html',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
        }
        mime_type = mime_type_map.get(ext, 'application/octet-stream')
    
    return content, mime_type

def static_file_exists(file_path: str) -> bool:
    """
    检查静态文件是否存在
    
    Args:
        file_path: 相对于static目录的文件路径
    
    Returns:
        是否存在
    """
    # 先检查是否能从包资源中读取
    if _get_static_content_from_resources(file_path) is not None:
        return True
    
    # 再检查文件系统
    return _get_static_file_path(file_path) is not None