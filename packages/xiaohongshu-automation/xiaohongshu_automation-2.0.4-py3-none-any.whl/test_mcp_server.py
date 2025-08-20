#!/usr/bin/env python3
"""
MCP 服务端测试脚本
用于验证 MCP 服务端框架是否正常工作
"""

import asyncio
import json
import logging
from adapters.xiaohongshu_adapter import XiaohongshuAdapter
from tools.tool_manager import ToolManager
from config import MCPConfig

# 配置日志
logging.basicConfig(
    level=getattr(logging, MCPConfig.LOG_LEVEL),
    format=MCPConfig.LOG_FORMAT
)
logger = logging.getLogger(__name__)

async def test_adapter():
    """测试适配器功能"""
    print("🧪 测试小红书适配器...")
    
    adapter = XiaohongshuAdapter(MCPConfig.FASTAPI_BASE_URL)
    
    try:
        # 测试健康检查
        print("1. 测试健康检查...")
        is_healthy = await adapter.health_check()
        print(f"   FastAPI 服务健康状态: {'✅ 正常' if is_healthy else '❌ 异常'}")
        
        # 测试监控状态
        print("2. 测试监控状态...")
        status = await adapter.get_monitor_status()
        print(f"   监控状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        # 测试发布历史
        print("3. 测试发布历史...")
        history = await adapter.get_publish_history()
        print(f"   发布历史记录数: {len(history)}")
        
        # 如果 FastAPI 服务正常，测试实际功能
        if is_healthy:
            print("4. 测试获取评论功能...")
            try:
                test_url = "https://www.xiaohongshu.com/explore/test"
                comments = await adapter.get_comments(test_url)
                print(f"   评论获取结果: {comments.get('status', 'unknown')}")
            except Exception as e:
                print(f"   评论获取测试失败（预期）: {str(e)}")
        
        print("✅ 适配器测试完成")
        
    except Exception as e:
        print(f"❌ 适配器测试失败: {str(e)}")
    
    finally:
        await adapter.client.aclose()

async def test_tool_manager():
    """测试工具管理器"""
    print("\n🔧 测试工具管理器...")
    
    try:
        adapter = XiaohongshuAdapter(MCPConfig.FASTAPI_BASE_URL)
        tool_manager = ToolManager(adapter)
        
        # 测试工具注册
        print("1. 测试工具注册...")
        tools = tool_manager.get_tool_list()
        print(f"   注册工具数量: {len(tools)}")
        for tool in tools:
            print(f"   • {tool.name}: {tool.description}")
        
        # 测试工具分类
        print("\n2. 测试工具分类...")
        categories = tool_manager.get_tools_by_category()
        for category, tool_names in categories.items():
            print(f"   📁 {category}: {', '.join(tool_names)}")
        
        # 测试工具信息
        print("\n3. 测试工具信息...")
        tool_info = tool_manager.get_tool_info()
        print(f"   工具信息条目: {len(tool_info)}")
        
        # 测试参数验证
        print("\n4. 测试参数验证...")
        try:
            # 测试发布工具参数验证
            publish_tool = tool_manager.get_tool("xiaohongshu_publish")
            valid_args = {
                "pic_urls": ["https://example.com/image.jpg"],
                "title": "测试标题",
                "content": "测试内容"
            }
            validated = publish_tool.validate_arguments(valid_args)
            print(f"   ✅ 参数验证通过: {len(validated)} 个参数")
            
            # 测试无效参数
            try:
                invalid_args = {"title": "只有标题"}
                publish_tool.validate_arguments(invalid_args)
                print("   ❌ 应该验证失败但没有")
            except ValueError as e:
                print(f"   ✅ 正确捕获验证错误: {str(e)}")
                
        except Exception as e:
            print(f"   ❌ 参数验证测试失败: {str(e)}")
        
        print("✅ 工具管理器测试完成")
        
        await adapter.client.aclose()
        
    except Exception as e:
        print(f"❌ 工具管理器测试失败: {str(e)}")

async def test_individual_tools():
    """测试单个工具功能"""
    print("\n🛠️ 测试单个工具...")
    
    try:
        adapter = XiaohongshuAdapter(MCPConfig.FASTAPI_BASE_URL)
        tool_manager = ToolManager(adapter)
        
        # 测试监控工具
        print("1. 测试监控工具...")
        try:
            monitor_tool = tool_manager.get_tool("xiaohongshu_monitor")
            result = await monitor_tool.execute({
                "include_history": True,
                "include_health": True,
                "history_limit": 5
            })
            
            if result.success:
                print(f"   ✅ 监控工具执行成功")
                print(f"   📊 健康评分: {result.data.get('health_score', {}).get('percentage', 'N/A')}%")
            else:
                print(f"   ❌ 监控工具执行失败: {result.error}")
                
        except Exception as e:
            print(f"   ❌ 监控工具测试异常: {str(e)}")
        
        # 测试评论工具（模拟）
        print("\n2. 测试评论获取工具...")
        try:
            comments_tool = tool_manager.get_tool("xiaohongshu_get_comments")
            
            # 测试参数验证
            try:
                comments_tool.validate_arguments({"url": "invalid-url"})
                print("   ❌ URL验证应该失败")
            except ValueError:
                print("   ✅ URL验证正确失败")
            
            # 测试有效URL格式
            valid_url = "https://www.xiaohongshu.com/explore/test123"
            validated = comments_tool.validate_arguments({"url": valid_url})
            print(f"   ✅ 有效URL验证通过: {validated['url']}")
            
        except Exception as e:
            print(f"   ❌ 评论工具测试异常: {str(e)}")
        
        # 测试发布工具参数验证
        print("\n3. 测试发布工具参数验证...")
        try:
            publish_tool = tool_manager.get_tool("xiaohongshu_publish")
            
            # 测试图片URL验证
            test_cases = [
                {
                    "pic_urls": ["https://example.com/image.jpg"],
                    "title": "测试标题",
                    "content": "这是一个测试内容 #测试 😊"
                },
                {
                    "pic_urls": ["https://imgur.com/test.png", "https://unsplash.com/photo.jpg"],
                    "title": "多图测试",
                    "content": "多图发布测试内容"
                }
            ]
            
            for i, test_case in enumerate(test_cases, 1):
                try:
                    validated = publish_tool.validate_arguments(test_case)
                    print(f"   ✅ 测试用例 {i} 验证通过")
                except Exception as e:
                    print(f"   ❌ 测试用例 {i} 验证失败: {str(e)}")
            
        except Exception as e:
            print(f"   ❌ 发布工具测试异常: {str(e)}")
        
        print("✅ 单个工具测试完成")
        
        await adapter.client.aclose()
        
    except Exception as e:
        print(f"❌ 单个工具测试失败: {str(e)}")

async def test_publish_mcp_function():
    """实际测试发布 MCP 函数的完整流程"""
    print("\n📝 实际测试发布 MCP 函数...")
    
    try:
        adapter = XiaohongshuAdapter(MCPConfig.FASTAPI_BASE_URL)
        tool_manager = ToolManager(adapter)
        
        # 测试用例数据
        test_cases = [
            {
                "name": "基础发布测试",
                "args": {
                    "pic_urls": ["https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89"],
                    "title": "MCP测试发布",
                    "content": "这是通过MCP服务端发布的测试内容 #MCP测试 #自动化 😊"
                }
            },
            {
                "name": "多图发布测试",
                "args": {
                    "pic_urls": [
                        "https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89",
                        "https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89",
                        "https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89"
                    ],
                    "title": "多图测试内容",
                    "content": "这是一个多图发布测试，包含多张图片和丰富的内容描述。\n\n✨ 特点：\n• 图片质量高\n• 内容丰富\n• 话题标签完整\n\n#多图发布 #测试内容 #小红书自动化 🎉"
                }
            },
            {
                "name": "优质内容测试",
                "args": {
                    "pic_urls": ["https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89"],
                    "title": "高质量内容创作指南",
                    "content": "📚 今天分享一些高质量内容创作的小技巧：\n\n1️⃣ 标题要吸引人\n2️⃣ 图片要清晰美观\n3️⃣ 内容要有价值\n4️⃣ 互动要及时\n\n希望对大家有帮助！有问题欢迎评论区交流 💬\n\n#内容创作 #小红书技巧 #干货分享 @小红书创作者 ✨"
                }
            }
        ]
        
        print(f"准备测试 {len(test_cases)} 个发布用例...")
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n--- 测试用例 {i}: {test_case['name']} ---")
            
            try:
                # 1. 参数验证测试
                print("1️⃣ 参数验证...")
                publish_tool = tool_manager.get_tool("xiaohongshu_publish")
                validated_args = publish_tool.validate_arguments(test_case['args'])
                print(f"   ✅ 参数验证通过: {len(validated_args)} 个参数")
                
                # 2. 内容质量预分析
                print("2️⃣ 内容质量预分析...")
                title = test_case['args']['title']
                content = test_case['args']['content']
                pic_count = len(test_case['args']['pic_urls'])
                
                # 简单的质量评估
                quality_score = 0
                if 5 <= len(title) <= 20:
                    quality_score += 20
                if 50 <= len(content) <= 500:
                    quality_score += 30
                if '#' in content:
                    quality_score += 20
                if any(emoji in content for emoji in ['😊', '✨', '🎉', '💬', '📚']):
                    quality_score += 15
                if '\n' in content:
                    quality_score += 15
                
                print(f"   📊 预估质量评分: {quality_score}/100")
                print(f"   📷 图片数量: {pic_count}")
                print(f"   📝 标题长度: {len(title)} 字")
                print(f"   📖 内容长度: {len(content)} 字")
                
                # 3. 通过工具管理器调用发布工具
                print("3️⃣ 执行发布工具...")
                start_time = asyncio.get_event_loop().time()
                
                # 使用 call_tool 方法（这会调用 safe_execute）
                result_content = await tool_manager.call_tool("xiaohongshu_publish", test_case['args'])
                
                end_time = asyncio.get_event_loop().time()
                execution_time = end_time - start_time
                
                print(f"   ⏱️ 执行时间: {execution_time:.2f}秒")
                
                # 4. 结果分析
                print("4️⃣ 结果分析...")
                if result_content and len(result_content) > 0:
                    result_text = result_content[0].text
                    print(f"   📄 结果长度: {len(result_text)} 字符")
                    
                    # 检查结果中的关键信息
                    if "✅" in result_text:
                        print("   ✅ 发布状态: 成功")
                    elif "❌" in result_text:
                        print("   ❌ 发布状态: 失败")
                    else:
                        print("   ❓ 发布状态: 未知")
                    
                    # 检查是否包含质量分析
                    if "质量评分" in result_text:
                        print("   📊 包含质量分析: ✅")
                    else:
                        print("   📊 包含质量分析: ❌")
                    
                    # 检查是否包含优化建议
                    if "优化" in result_text or "建议" in result_text:
                        print("   💡 包含优化建议: ✅")
                    else:
                        print("   💡 包含优化建议: ❌")
                    
                    # 显示部分结果内容
                    print("   📋 结果预览:")
                    preview_lines = result_text.split('\n')[:5]
                    for line in preview_lines:
                        if line.strip():
                            print(f"      {line}")
                    if len(result_text.split('\n')) > 5:
                        print("      ...")
                
                else:
                    print("   ❌ 未获取到结果内容")
                
                print(f"   ✅ 测试用例 {i} 完成")
                
            except Exception as e:
                print(f"   ❌ 测试用例 {i} 失败: {str(e)}")
                # 打印详细错误信息
                import traceback
                print(f"   🔍 详细错误: {traceback.format_exc()}")
        
        # 5. 测试错误处理
        print(f"\n--- 错误处理测试 ---")
        print("5️⃣ 测试错误参数处理...")
        
        error_test_cases = [
            {
                "name": "缺少必需参数",
                "args": {"title": "只有标题"}
            },
            {
                "name": "无效图片URL",
                "args": {
                    "pic_urls": ["invalid-url"],
                    "title": "测试",
                    "content": "测试内容"
                }
            },
            {
                "name": "空参数",
                "args": {}
            }
        ]
        
        for error_case in error_test_cases:
            try:
                print(f"\n   测试: {error_case['name']}")
                result_content = await tool_manager.call_tool("xiaohongshu_publish", error_case['args'])
                
                if result_content and len(result_content) > 0:
                    result_text = result_content[0].text
                    if "❌" in result_text and "错误" in result_text:
                        print(f"   ✅ 正确处理错误: {error_case['name']}")
                    else:
                        print(f"   ❓ 错误处理结果不明确: {error_case['name']}")
                else:
                    print(f"   ❌ 未获取到错误处理结果: {error_case['name']}")
                    
            except Exception as e:
                print(f"   ⚠️ 错误测试异常: {error_case['name']} - {str(e)}")
        
        print("\n✅ 发布 MCP 函数实际测试完成")
        
        await adapter.client.aclose()
        
    except Exception as e:
        print(f"❌ 发布 MCP 函数测试失败: {str(e)}")
        import traceback
        print(f"🔍 详细错误: {traceback.format_exc()}")

async def test_mcp_server():
    """测试 MCP 服务器集成"""
    print("\n🖥️ 测试 MCP 服务器集成...")
    
    try:
        from mcp_server import XiaohongshuMCPServer
        
        # 测试服务器初始化
        print("1. 测试服务器初始化...")
        server = XiaohongshuMCPServer()
        print("   ✅ MCP 服务器初始化成功")
        print(f"   📊 工具管理器已注册 {len(server.tool_manager.tools)} 个工具")
        
        # 测试工具列表获取
        print("\n2. 测试工具列表...")
        tools = server.tool_manager.get_tool_list()
        print(f"   📋 可用工具: {len(tools)} 个")
        for tool in tools:
            print(f"      • {tool.name}")
        
        # 测试配置
        print("\n3. 测试配置...")
        print(f"   🔧 服务器名称: {MCPConfig.SERVER_NAME}")
        print(f"   📝 版本: {MCPConfig.SERVER_VERSION}")
        print(f"   🌐 FastAPI URL: {MCPConfig.FASTAPI_BASE_URL}")
        
        print("✅ MCP 服务器集成测试完成")
        
    except Exception as e:
        print(f"❌ MCP 服务器集成测试失败: {str(e)}")

def test_config():
    """测试配置"""
    print("\n⚙️ 测试配置...")
    
    try:
        print(f"1. FastAPI 基础URL: {MCPConfig.FASTAPI_BASE_URL}")
        print(f"2. 服务器名称: {MCPConfig.SERVER_NAME}")
        print(f"3. 服务器版本: {MCPConfig.SERVER_VERSION}")
        print(f"4. 日志级别: {MCPConfig.LOG_LEVEL}")
        print(f"5. 超时设置: {MCPConfig.FASTAPI_TIMEOUT}秒")
        
        capabilities = MCPConfig.get_server_capabilities()
        print(f"6. 服务器能力: {json.dumps(capabilities, indent=2)}")
        
        adapter_config = MCPConfig.get_adapter_config()
        print(f"7. 适配器配置: {json.dumps(adapter_config, indent=2)}")
        
        print("✅ 配置测试完成")
        
    except Exception as e:
        print(f"❌ 配置测试失败: {str(e)}")

async def test_error_handling():
    """测试错误处理"""
    print("\n🚨 测试错误处理...")
    
    try:
        adapter = XiaohongshuAdapter("http://invalid-url:9999")  # 无效URL
        tool_manager = ToolManager(adapter)
        
        # 测试网络错误处理
        print("1. 测试网络错误处理...")
        try:
            result = await adapter.health_check()
            print(f"   健康检查结果: {'✅ 正常' if result else '❌ 异常'}")
        except Exception as e:
            print(f"   ✅ 正确捕获网络错误: {type(e).__name__}")
        
        # 测试工具调用错误处理
        print("\n2. 测试工具调用错误处理...")
        try:
            result = await tool_manager.call_tool("nonexistent_tool", {})
            print(f"   ❌ 应该抛出错误但没有")
        except Exception as e:
            print(f"   ✅ 正确处理不存在的工具: {type(e).__name__}")
        
        # 测试参数验证错误
        print("\n3. 测试参数验证错误...")
        try:
            publish_tool = tool_manager.get_tool("xiaohongshu_publish")
            result = await publish_tool.safe_execute({})  # 空参数
            # safe_execute 应该返回错误内容而不是抛出异常
            print(f"   ✅ 安全执行处理了参数错误")
        except Exception as e:
            print(f"   ❌ 安全执行应该不抛出异常: {str(e)}")
        
        print("✅ 错误处理测试完成")
        
        await adapter.client.aclose()
        
    except Exception as e:
        print(f"❌ 错误处理测试失败: {str(e)}")

async def main():
    """主测试函数"""
    print("🚀 开始 MCP 服务端第二阶段测试\n")
    
    # 测试配置
    test_config()
    
    # 测试适配器
    await test_adapter()
    
    # 测试工具管理器
    await test_tool_manager()
    
    # 测试单个工具
    await test_individual_tools()
    
    # 🆕 实际测试发布 MCP 函数
    await test_publish_mcp_function()
    
    # 测试 MCP 服务器集成
    await test_mcp_server()
    
    # 测试错误处理
    await test_error_handling()
    
    print("\n🎉 第二阶段测试完成！")
    print("\n📝 第二阶段改进总结:")
    print("✅ 实现了基础工具类和工具管理器")
    print("✅ 增强了参数验证和错误处理")
    print("✅ 优化了结果格式化和用户体验")
    print("✅ 添加了内容质量分析功能")
    print("✅ 实现了智能评论分析和回复优化")
    print("✅ 增加了系统健康评分机制")
    print("✅ 扩展了提示模板功能")
    print("✅ 完成了发布 MCP 函数的实际测试")
    
    print("\n📝 下一步:")
    print("1. 确保 FastAPI 服务正在运行 (python main.py)")
    print("2. 运行 MCP 服务端 (python mcp_server.py)")
    print("3. 在 AI 客户端中配置 MCP 服务端连接")
    print("4. 开始第三阶段：高级资源和提示模板实现")

if __name__ == "__main__":
    asyncio.run(main()) 