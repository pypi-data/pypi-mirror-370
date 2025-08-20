#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小红书自动化工具包发布脚本
使用 uv 构建并上传到 PyPI
"""

import subprocess
import sys
import os
import shutil
import platform
from pathlib import Path

# Windows 编码设置
if platform.system() == "Windows":
    import locale
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')

def run_command(cmd, description):
    """运行命令并处理错误"""
    print(f"🔄 {description}...")
    try:
        # 在Windows上设置编码
        env = os.environ.copy()
        if platform.system() == "Windows":
            env['PYTHONIOENCODING'] = 'utf-8'
        
        result = subprocess.run(
            cmd, 
            shell=True, 
            check=True, 
            capture_output=True, 
            text=True,
            encoding='utf-8',
            env=env
        )
        print(f"✅ {description} 成功")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败: {e}")
        if e.stderr:
            print(f"错误信息: {e.stderr}")
        return False

def remove_directory(path):
    """跨平台删除目录"""
    if Path(path).exists():
        try:
            shutil.rmtree(path)
            print(f"✅ 删除 {path} 成功")
        except Exception as e:
            print(f"⚠️ 删除 {path} 失败: {e}")

def main():
    """主发布流程"""
    print("🚀 开始发布小红书自动化工具包...")
    
    # 确保在项目根目录
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # 1. 清理之前的构建
    print("🧹 清理之前的构建文件...")
    remove_directory("dist")
    remove_directory("build")
    
    # 2. 运行测试（可选，跳过有编码问题的测试）
    print("🧪 跳过测试（编码问题）...")
    print("⚠️ 建议在发布前手动运行测试")
    
    # 3. 构建包
    if not run_command("uv build", "构建包"):
        print("❌ 构建失败，退出")
        sys.exit(1)
    
    # 4. 检查构建的包
    print("📦 检查构建的包...")
    dist_path = Path("dist")
    if dist_path.exists():
        dist_files = list(dist_path.glob("*"))
        for file in dist_files:
            if file.is_file():
                size_kb = file.stat().st_size / 1024
                print(f"  - {file.name} ({size_kb:.1f} KB)")
    
    # 5. 询问是否上传到 PyPI
    try:
        upload_choice = input("\n🔽 是否上传到 PyPI? (y/N): ").lower().strip()
    except (UnicodeDecodeError, UnicodeEncodeError):
        upload_choice = input("\n是否上传到 PyPI? (y/N): ").lower().strip()
    
    if upload_choice in ['y', 'yes']:
        # 检查是否安装了 twine
        try:
            result = subprocess.run(
                ["twine", "--version"], 
                check=True, 
                capture_output=True,
                encoding='utf-8'
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("📥 安装 twine...")
            if not run_command("uv pip install twine", "安装 twine"):
                print("❌ 安装 twine 失败")
                sys.exit(1)
        
        # 上传到 PyPI
        print("🌐 上传到 PyPI...")
        print("📝 请确保已设置 PyPI 凭据")
        print("💡 建议使用 TestPyPI 进行测试: twine upload --repository testpypi dist/*")
        
        # 使用环境变量避免 rich 的编码问题
        env = os.environ.copy()
        env['TWINE_PROGRESS_BAR'] = 'off'  # 禁用进度条
        if platform.system() == "Windows":
            env['PYTHONIOENCODING'] = 'utf-8'
        
        try:
            result = subprocess.run(
                "twine upload dist/*", 
                shell=True, 
                check=True,
                env=env,
                encoding='utf-8'
            )
            print("🎉 成功发布到 PyPI!")
            print("📖 用户现在可以使用以下命令安装:")
            print("   pip install xiaohongshu-automation")
        except subprocess.CalledProcessError as e:
            print("❌ 上传失败")
            print("💡 可能的解决方案:")
            print("  1. 检查 PyPI 凭据")
            print("  2. 确保包名未被占用")
            print("  3. 先上传到 TestPyPI 测试: twine upload --repository testpypi dist/*")
            return False
    
    else:
        print("📦 本地构建完成，文件位于 dist/ 目录")
        print("💡 如需手动上传，使用: twine upload dist/*")
        print("💡 测试上传，使用: twine upload --repository testpypi dist/*")
    
    print("\n✨ 发布流程完成!")
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ 用户取消操作")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1) 