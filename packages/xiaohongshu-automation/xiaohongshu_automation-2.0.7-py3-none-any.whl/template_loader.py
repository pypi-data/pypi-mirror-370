"""
HTML模板加载器
用于加载和处理HTML模板文件
"""

import os
import sys
from pathlib import Path

# 内嵌的默认模板内容作为备用方案
EMBEDDED_TEMPLATES = {
    "activate.html": """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>小红书自动化工具 - 许可证激活</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; }
        .container { max-width: 600px; background: white; padding: 2rem; border-radius: 15px; box-shadow: 0 20px 40px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 2rem; }
        .header h1 { color: #333; font-size: 1.8rem; margin-bottom: 0.5rem; }
        .header p { color: #666; }
        .status-section { background: #f8f9fa; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; border-left: 4px solid {status_color}; }
        .status-title { font-size: 1.1rem; font-weight: 600; color: #333; margin-bottom: 1rem; }
        .status-row { display: flex; justify-content: space-between; margin-bottom: 0.5rem; }
        .status-label { font-weight: 500; color: #555; }
        .status-value { color: #333; font-weight: 600; }
        .form-section { margin-bottom: 1.5rem; }
        .form-group { margin-bottom: 1rem; }
        .form-group label { display: block; margin-bottom: 0.5rem; font-weight: 500; color: #333; }
        .form-control { width: 100%; padding: 0.75rem; border: 2px solid #e1e5e9; border-radius: 8px; font-size: 1rem; transition: border-color 0.3s; }
        .form-control:focus { outline: none; border-color: #667eea; }
        .btn { background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 0.75rem 2rem; border-radius: 8px; font-size: 1rem; cursor: pointer; transition: transform 0.2s; }
        .btn:hover { transform: translateY(-2px); }
        .machine-info { background: #e9ecef; padding: 1rem; border-radius: 8px; margin-top: 1rem; font-size: 0.9rem; color: #6c757d; }
        #result { margin-top: 1rem; padding: 1rem; border-radius: 8px; display: none; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 小红书自动化工具</h1>
            <p>许可证激活管理中心</p>
        </div>
        
        <div class="status-section">
            <div class="status-title">📊 当前许可证状态</div>
            <div class="status-row">
                <span class="status-label">🔍 状态:</span>
                <span class="status-value" style="color: {status_color};">{license_status}</span>
            </div>
            <div class="status-row">
                <span class="status-label">🏷️ 类型:</span>
                <span class="status-value">{license_type}</span>
            </div>
            {expiry_rows}
        </div>
        
        <div class="form-section">
            <div class="form-group">
                <label for="activation_code">🔑 激活码</label>
                <input type="text" id="activation_code" class="form-control" placeholder="请输入激活码">
            </div>
            <button onclick="activateLicense()" class="btn">激活许可证</button>
        </div>
        
        <div id="result"></div>
        
        <div class="machine-info">
            <strong>🖥️ 机器标识:</strong> {machine_id}<br>
            <small>激活时需要此机器标识，请联系软件提供商获取激活码</small>
        </div>
    </div>
    
    <script>
        async function activateLicense() {
            const code = document.getElementById('activation_code').value.trim();
            const resultDiv = document.getElementById('result');
            
            if (!code) {
                showResult('请输入激活码', 'error');
                return;
            }
            
            showResult('正在激活许可证...', 'info');
            
            try {
                const response = await fetch('/license/activate', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ activation_code: code })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showResult(`激活成功！${data.message}`, 'success');
                    setTimeout(() => location.reload(), 2000);
                } else {
                    showResult(`激活失败：${data.message}`, 'error');
                }
            } catch (error) {
                showResult(`激活过程中发生错误：${error.message}`, 'error');
            }
        }
        
        function showResult(message, type) {
            const resultDiv = document.getElementById('result');
            resultDiv.textContent = message;
            resultDiv.className = type;
            resultDiv.style.display = 'block';
        }
        
        document.getElementById('activation_code').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                activateLicense();
            }
        });
    </script>
</body>
</html>"""
}

def _get_template_content_from_resources(template_name: str) -> str:
    """
    尝试使用 importlib.resources 从包中读取模板内容
    
    Args:
        template_name: 模板文件名
        
    Returns:
        模板内容，如果失败则返回 None
    """
    try:
        # Python 3.9+ 的新 API
        try:
            from importlib.resources import files
            # 尝试多种包名
            package_names = ["xiaohongshu_automation", ".", __name__.split('.')[0] if '.' in __name__ else __name__]
            
            for package_name in package_names:
                try:
                    template_content = (files(package_name) / "templates" / template_name).read_text(encoding="utf-8")
                    return template_content
                except Exception:
                    continue
        except (ImportError, AttributeError):
            # Python 3.7-3.8 的兼容 API
            import importlib.resources as resources
            package_names = ["xiaohongshu_automation.templates", "templates"]
            
            for package_name in package_names:
                try:
                    template_content = resources.read_text(package_name, template_name)
                    return template_content
                except Exception:
                    continue
    except Exception:
        pass
    
    return None

def _get_template_path(template_name: str) -> Path:
    """
    获取模板文件的绝对路径，支持开发环境和打包后环境
    
    Args:
        template_name: 模板文件名
        
    Returns:
        模板文件的绝对路径
    """
    # 方法1: 优先尝试相对于当前文件的路径（开发环境）
    current_dir = Path(__file__).parent
    template_path = current_dir / "templates" / template_name
    
    if template_path.exists():
        return template_path
    
    # 方法2: 尝试相对于工作目录的路径
    template_path = Path("templates") / template_name
    if template_path.exists():
        return template_path
    
    # 方法3: 尝试从系统路径中寻找
    possible_paths = [
        Path.cwd() / "templates" / template_name,
        Path(__file__).parent.parent / "templates" / template_name,
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    raise FileNotFoundError(f"模板文件未找到: {template_name}，尝试过的路径: {[str(p) for p in [current_dir / 'templates' / template_name, template_path] + possible_paths]}")

def load_template(template_name: str, **kwargs) -> str:
    """
    加载HTML模板文件并替换变量
    
    Args:
        template_name: 模板文件名（不包含路径）
        **kwargs: 要替换的变量键值对
    
    Returns:
        处理后的HTML内容
    """
    content = None
    
    # 首先尝试从包资源中读取（适用于打包后的环境）
    content = _get_template_content_from_resources(template_name)
    
    if content is None:
        # 如果从包资源读取失败，尝试从文件系统读取
        try:
            template_path = _get_template_path(template_name)
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
        except FileNotFoundError:
            # 最后备用方案：使用内嵌模板
            content = EMBEDDED_TEMPLATES.get(template_name)
            if content is None:
                raise FileNotFoundError(f"模板文件未找到: {template_name}，已尝试所有方法")
    
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
    # 先检查是否能从包资源中读取
    if _get_template_content_from_resources(template_name) is not None:
        return True
    
    # 再检查文件系统
    try:
        _get_template_path(template_name)
        return True
    except FileNotFoundError:
        # 最后检查内嵌模板
        return template_name in EMBEDDED_TEMPLATES 