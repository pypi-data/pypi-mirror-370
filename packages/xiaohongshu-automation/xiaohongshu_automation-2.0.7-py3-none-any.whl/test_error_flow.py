#!/usr/bin/env python3
"""
测试图片下载失败时的错误传递链路
"""

import asyncio
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tools.publish_tool import PublishTool
from adapters.xiaohongshu_adapter import XiaohongshuAdapter

async def test_image_download_failure():
    """测试图片下载失败的情况"""
    
    # 创建适配器和发布工具
    adapter = XiaohongshuAdapter("http://localhost:8000")
    publish_tool = PublishTool(adapter)
    
    # 测试参数 - 包含无效的图片URL
    test_args = {
        "pic_urls": [
            "https://invalid-domain-that-does-not-exist.com/image1.jpg",
            "https://httpstat.us/404/image2.jpg"  # 404错误
        ],
        "title": "测试标题",
        "content": "测试内容",
        "labels": ["#测试"]
    }
    
    print("开始测试图片下载失败的错误传递...")
    
    try:
        result = await publish_tool.execute(test_args)
        
        print(f"测试结果:")
        print(f"  Success: {result.success}")
        print(f"  Message: {result.message}")
        print(f"  Error: {result.error}")
        
        if result.success:
            print("❌ 测试失败：预期应该返回失败，但返回了成功")
            return False
        else:
            print("✅ 测试成功：正确返回了失败状态")
            print(f"错误信息: {result.error}")
            return True
            
    except Exception as e:
        print(f"❌ 测试过程中发生异常: {str(e)}")
        return False
    
    finally:
        await adapter.client.aclose()

if __name__ == "__main__":
    result = asyncio.run(test_image_download_failure())
    if result:
        print("\n🎉 错误传递链路测试通过")
    else:
        print("\n💥 错误传递链路测试失败")
        sys.exit(1) 