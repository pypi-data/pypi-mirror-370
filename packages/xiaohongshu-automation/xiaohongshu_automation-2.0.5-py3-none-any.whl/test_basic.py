#!/usr/bin/env python3
"""
基础测试脚本
逐步检查导入和功能
"""

import sys
import traceback

def test_basic_imports():
    """测试基础导入"""
    print("🔍 测试基础导入...")
    
    try:
        import asyncio
        print("✅ asyncio 导入成功")
    except Exception as e:
        print(f"❌ asyncio 导入失败: {e}")
        return False
    
    try:
        import json
        print("✅ json 导入成功")
    except Exception as e:
        print(f"❌ json 导入失败: {e}")
        return False
    
    try:
        import httpx
        print("✅ httpx 导入成功")
    except Exception as e:
        print(f"❌ httpx 导入失败: {e}")
        return False
    
    return True

def test_adapter_import():
    """测试适配器导入"""
    print("\n🔍 测试适配器导入...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        print("✅ XiaohongshuAdapter 导入成功")
        
        # 测试实例化
        adapter = XiaohongshuAdapter("http://localhost:8000")
        print("✅ XiaohongshuAdapter 实例化成功")
        
        return True
    except Exception as e:
        print(f"❌ 适配器导入失败: {e}")
        traceback.print_exc()
        return False

def test_tools_import():
    """测试工具导入"""
    print("\n🔍 测试工具导入...")
    
    try:
        from tools.base_tool import BaseTool, ToolResult
        print("✅ BaseTool 导入成功")
    except Exception as e:
        print(f"❌ BaseTool 导入失败: {e}")
        traceback.print_exc()
        return False
    
    try:
        from tools.publish_tool import PublishTool
        print("✅ PublishTool 导入成功")
    except Exception as e:
        print(f"❌ PublishTool 导入失败: {e}")
        traceback.print_exc()
        return False
    
    return True

async def test_adapter_basic():
    """测试适配器基础功能"""
    print("\n🔍 测试适配器基础功能...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        
        adapter = XiaohongshuAdapter("http://localhost:8000")
        
        # 测试健康检查
        print("测试健康检查...")
        is_healthy = await adapter.health_check()
        print(f"健康状态: {'✅ 正常' if is_healthy else '❌ 异常'}")
        
        # 测试监控状态
        print("测试监控状态...")
        status = await adapter.get_monitor_status()
        print(f"监控状态: {status}")
        
        await adapter.client.aclose()
        print("✅ 适配器基础功能测试完成")
        
        return True
    except Exception as e:
        print(f"❌ 适配器基础功能测试失败: {e}")
        traceback.print_exc()
        return False

async def test_publish_tool_basic():
    """测试发布工具基础功能"""
    print("\n🔍 测试发布工具基础功能...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.publish_tool import PublishTool
        
        adapter = XiaohongshuAdapter("http://localhost:8000")
        publish_tool = PublishTool(adapter)
        
        # 测试 Schema
        print("测试工具 Schema...")
        schema = publish_tool.get_schema()
        print(f"Schema 类型: {schema.get('type')}")
        print(f"必需参数: {schema.get('required', [])}")
        
        # 测试参数验证
        print("测试参数验证...")
        test_args = {
            "pic_urls": ["https://picsum.photos/800/600"],
            "title": "测试标题",
            "content": "测试内容 #测试"
        }
        
        validated = publish_tool.validate_arguments(test_args)
        print(f"参数验证通过: {len(validated)} 个参数")
        
        await adapter.client.aclose()
        print("✅ 发布工具基础功能测试完成")
        
        return True
    except Exception as e:
        print(f"❌ 发布工具基础功能测试失败: {e}")
        traceback.print_exc()
        return False

async def main():
    """主测试函数"""
    print("🚀 开始基础测试\n")
    
    # 测试基础导入
    if not test_basic_imports():
        print("❌ 基础导入测试失败，停止测试")
        return
    
    # 测试适配器导入
    if not test_adapter_import():
        print("❌ 适配器导入测试失败，停止测试")
        return
    
    # 测试工具导入
    if not test_tools_import():
        print("❌ 工具导入测试失败，停止测试")
        return
    
    # 测试适配器基础功能
    if not await test_adapter_basic():
        print("❌ 适配器基础功能测试失败")
    
    # 测试发布工具基础功能
    if not await test_publish_tool_basic():
        print("❌ 发布工具基础功能测试失败")
    
    print("\n🎉 基础测试完成！")

if __name__ == "__main__":
    try:
        import asyncio
        asyncio.run(main())
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        traceback.print_exc() 