#!/usr/bin/env python3
"""
测试超时改进和诊断功能
"""

import asyncio
import logging
from tools.tool_manager import ToolManager
from adapters.xiaohongshu_adapter import XiaohongshuAdapter
from config import MCPConfig

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("timeout_test")

async def test_timeout_improvements():
    """测试超时改进功能"""
    
    print("🔧 测试超时改进和诊断功能")
    print("=" * 50)
    
    # 初始化适配器和工具管理器
    adapter = XiaohongshuAdapter(MCPConfig.FASTAPI_BASE_URL)
    tool_manager = ToolManager(adapter)
    
    print(f"📊 当前配置:")
    config = MCPConfig.get_adapter_config()
    for key, value in config.items():
        print(f"   • {key}: {value}")
    print()
    
    print(f"🔧 注册的工具数量: {len(tool_manager.tools)}")
    categories = tool_manager.get_tools_by_category()
    for category, tools in categories.items():
        print(f"   📁 {category}: {', '.join(tools)}")
    print()
    
    # 测试超时诊断工具
    print("🔍 测试超时诊断工具...")
    try:
        result = await tool_manager.call_tool(
            "xiaohongshu_timeout_diagnostic",
            {
                "include_network_test": True,
                "include_performance_test": True,
                "test_endpoints": ["health", "publish", "comments"]
            }
        )
        
        print("✅ 超时诊断工具调用成功")
        print(f"📄 结果长度: {len(result[0].text)} 字符")
        
        # 显示结果的前部分
        result_text = result[0].text
        lines = result_text.split('\n')
        print("📋 诊断结果预览:")
        for i, line in enumerate(lines[:20]):  # 显示前20行
            print(f"   {line}")
        if len(lines) > 20:
            print(f"   ... 还有 {len(lines) - 20} 行")
        print()
        
    except Exception as e:
        print(f"❌ 超时诊断工具测试失败: {str(e)}")
        print()
    
    # 测试改进的发布工具（应该给出更好的错误信息）
    print("📝 测试改进的发布工具错误处理...")
    try:
        result = await tool_manager.call_tool(
            "xiaohongshu_publish",
            {
                "pic_urls": ["https://example.com/test.jpg"],
                "title": "超时测试",
                "content": "测试改进的超时处理和错误信息"
            }
        )
        
        result_text = result[0].text
        print("📋 发布工具响应:")
        lines = result_text.split('\n')
        for line in lines[:15]:  # 显示前15行
            print(f"   {line}")
        print()
        
    except Exception as e:
        print(f"❌ 发布工具测试失败: {str(e)}")
        print()
    
    # 测试监控工具
    print("📊 测试监控工具...")
    try:
        result = await tool_manager.call_tool(
            "xiaohongshu_monitor",
            {
                "include_history": True,
                "include_health": True,
                "history_limit": 5
            }
        )
        
        print("✅ 监控工具调用成功")
        result_text = result[0].text
        lines = result_text.split('\n')
        print("📋 监控结果预览:")
        for line in lines[:15]:  # 显示前15行
            print(f"   {line}")
        print()
        
    except Exception as e:
        print(f"❌ 监控工具测试失败: {str(e)}")
        print()
    
    await adapter.client.aclose()

async def test_configuration_variations():
    """测试不同配置下的超时行为"""
    
    print("⚙️ 测试不同操作的超时配置")
    print("=" * 50)
    
    operations = ["publish", "comments", "monitor", "health_check"]
    
    for operation in operations:
        timeout = MCPConfig.get_timeout_for_operation(operation)
        print(f"   • {operation}: {timeout}秒")
    
    print()

def display_timeout_recommendations():
    """显示超时配置建议"""
    
    print("💡 超时配置建议")
    print("=" * 50)
    
    recommendations = [
        {
            "场景": "本地开发",
            "配置": {
                "FASTAPI_TIMEOUT": "30",
                "PUBLISH_TIMEOUT": "60", 
                "COMMENTS_TIMEOUT": "30",
                "HEALTH_CHECK_TIMEOUT": "5"
            }
        },
        {
            "场景": "生产环境",
            "配置": {
                "FASTAPI_TIMEOUT": "60",
                "PUBLISH_TIMEOUT": "120",
                "COMMENTS_TIMEOUT": "60", 
                "HEALTH_CHECK_TIMEOUT": "10"
            }
        },
        {
            "场景": "网络较慢",
            "配置": {
                "FASTAPI_TIMEOUT": "90",
                "PUBLISH_TIMEOUT": "180",
                "COMMENTS_TIMEOUT": "90",
                "HEALTH_CHECK_TIMEOUT": "15"
            }
        }
    ]
    
    for rec in recommendations:
        print(f"📌 {rec['场景']}:")
        for key, value in rec["配置"].items():
            print(f"   export {key}={value}")
        print()

async def main():
    """主测试函数"""
    
    print("🚀 超时改进测试套件")
    print("=" * 60)
    print()
    
    await test_configuration_variations()
    await test_timeout_improvements()
    display_timeout_recommendations()
    
    print("✅ 超时改进测试完成！")
    print()
    print("📝 总结:")
    print("   • 添加了操作特定的超时配置")
    print("   • 实现了智能重试机制")
    print("   • 提供了详细的错误诊断")
    print("   • 创建了专门的超时诊断工具")
    print("   • 优化了错误信息和用户体验")

if __name__ == "__main__":
    asyncio.run(main()) 