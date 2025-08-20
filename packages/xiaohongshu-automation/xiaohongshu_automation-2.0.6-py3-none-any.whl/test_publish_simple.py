#!/usr/bin/env python3
"""
简化的发布功能测试脚本
不依赖 MCP 模块，直接测试核心功能
"""

import asyncio
import json
import logging
import sys
import traceback
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_adapter_basic():
    """测试适配器基础功能"""
    print("🧪 测试适配器基础功能...")
    
    try:
        # 导入适配器
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        
        adapter = XiaohongshuAdapter("http://localhost:8000")
        
        # 测试健康检查
        print("1. 测试健康检查...")
        is_healthy = await adapter.health_check()
        print(f"   FastAPI 服务健康状态: {'✅ 正常' if is_healthy else '❌ 异常'}")
        
        # 测试监控状态
        print("2. 测试监控状态...")
        status = await adapter.get_monitor_status()
        print(f"   监控状态: {json.dumps(status, indent=2, ensure_ascii=False)}")
        
        # 如果服务正常，测试发布功能
        if is_healthy:
            print("3. 测试发布功能...")
            test_data = {
                "pic_urls": ["https://picsum.photos/800/600?random=1"],
                "title": "测试发布",
                "content": "这是一个测试发布内容 #测试 😊"
            }
            
            try:
                result = await adapter.publish_content(**test_data)
                print(f"   发布结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            except Exception as e:
                print(f"   发布测试失败（可能是预期的）: {str(e)}")
        
        await adapter.client.aclose()
        print("✅ 适配器基础测试完成")
        
    except Exception as e:
        print(f"❌ 适配器测试失败: {str(e)}")
        traceback.print_exc()

async def test_publish_tool_direct():
    """直接测试发布工具"""
    print("\n🔧 直接测试发布工具...")
    
    try:
        # 导入工具
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.publish_tool import PublishTool
        
        adapter = XiaohongshuAdapter("http://localhost:8000")
        publish_tool = PublishTool(adapter)
        
        # 测试工具 Schema
        print("1. 测试工具 Schema...")
        schema = publish_tool.get_schema()
        print(f"   Schema 类型: {schema.get('type')}")
        print(f"   必需参数: {schema.get('required', [])}")
        print(f"   参数数量: {len(schema.get('properties', {}))}")
        
        # 测试参数验证
        print("\n2. 测试参数验证...")
        test_cases = [
            {
                "name": "有效参数",
                "args": {
                    "pic_urls": ["https://picsum.photos/800/600?random=1"],
                    "title": "测试标题",
                    "content": "测试内容 #测试 😊"
                },
                "should_pass": True
            },
            {
                "name": "缺少必需参数",
                "args": {"title": "只有标题"},
                "should_pass": False
            },
            {
                "name": "空参数",
                "args": {},
                "should_pass": False
            }
        ]
        
        for test_case in test_cases:
            try:
                validated = publish_tool.validate_arguments(test_case["args"])
                if test_case["should_pass"]:
                    print(f"   ✅ {test_case['name']}: 验证通过")
                else:
                    print(f"   ❌ {test_case['name']}: 应该失败但通过了")
            except ValueError as e:
                if not test_case["should_pass"]:
                    print(f"   ✅ {test_case['name']}: 正确失败 - {str(e)}")
                else:
                    print(f"   ❌ {test_case['name']}: 不应该失败 - {str(e)}")
        
        # 测试工具执行
        print("\n3. 测试工具执行...")
        test_args = {
            "pic_urls": ["https://picsum.photos/800/600?random=1"],
            "title": "工具测试发布",
            "content": "这是通过工具直接测试的发布内容\n\n包含多行文本和表情符号 😊\n\n#工具测试 #发布测试"
        }
        
        try:
            result = await publish_tool.execute(test_args)
            print(f"   执行结果: 成功={result.success}")
            print(f"   消息: {result.message}")
            if result.data:
                print(f"   数据类型: {type(result.data)}")
                if isinstance(result.data, dict):
                    print(f"   数据键: {list(result.data.keys())}")
            if result.error:
                print(f"   错误: {result.error}")
        except Exception as e:
            print(f"   执行异常: {str(e)}")
            traceback.print_exc()
        
        await adapter.client.aclose()
        print("✅ 发布工具直接测试完成")
        
    except Exception as e:
        print(f"❌ 发布工具测试失败: {str(e)}")
        traceback.print_exc()

async def test_content_analysis():
    """测试内容分析功能"""
    print("\n📊 测试内容分析功能...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.publish_tool import PublishTool
        
        adapter = XiaohongshuAdapter("http://localhost:8000")
        publish_tool = PublishTool(adapter)
        
        # 测试内容质量分析
        test_contents = [
            {
                "title": "简单标题",
                "content": "简单内容",
                "expected_score": "低"
            },
            {
                "title": "优质内容分享",
                "content": "这是一个包含丰富内容的分享\n\n包含多个段落\n包含话题 #测试\n包含表情 😊\n\n内容长度适中，结构清晰",
                "expected_score": "高"
            },
            {
                "title": "中等质量内容",
                "content": "这是一个中等长度的内容，包含一些基本元素 #中等测试",
                "expected_score": "中"
            }
        ]
        
        for i, test_content in enumerate(test_contents, 1):
            print(f"\n{i}. 测试内容: {test_content['title']}")
            
            # 调用内容质量分析方法
            analysis = publish_tool._analyze_content_quality(
                test_content["title"], 
                test_content["content"]
            )
            
            print(f"   标题长度: {analysis['title_length']}")
            print(f"   内容长度: {analysis['content_length']}")
            print(f"   质量评分: {analysis['quality_score']}/100")
            print(f"   包含话题: {'✅' if analysis['has_hashtags'] else '❌'}")
            print(f"   包含表情: {'✅' if analysis['has_emojis'] else '❌'}")
            print(f"   多段落: {'✅' if analysis['paragraph_count'] > 1 else '❌'}")
            print(f"   预期评分: {test_content['expected_score']}")
        
        await adapter.client.aclose()
        print("\n✅ 内容分析功能测试完成")
        
    except Exception as e:
        print(f"❌ 内容分析测试失败: {str(e)}")
        traceback.print_exc()

async def test_url_validation():
    """测试URL验证功能"""
    print("\n🔗 测试URL验证功能...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.publish_tool import PublishTool
        
        adapter = XiaohongshuAdapter("http://localhost:8000")
        publish_tool = PublishTool(adapter)
        
        # 测试URL验证
        test_urls = [
            {
                "urls": ["https://picsum.photos/800/600"],
                "name": "有效图片URL",
                "should_pass": True
            },
            {
                "urls": ["https://example.com/image.jpg", "https://test.com/photo.png"],
                "name": "多个有效URL",
                "should_pass": True
            },
            {
                "urls": ["invalid-url"],
                "name": "无效URL",
                "should_pass": False
            },
            {
                "urls": ["https://example.com/notimage.txt"],
                "name": "非图片URL",
                "should_pass": True  # 应该通过但有警告
            }
        ]
        
        for test_case in test_urls:
            print(f"\n测试: {test_case['name']}")
            try:
                validated = publish_tool._validate_urls(test_case["urls"])
                if test_case["should_pass"]:
                    print(f"   ✅ 验证通过: {len(validated)} 个URL")
                else:
                    print(f"   ❌ 应该失败但通过了")
            except ValueError as e:
                if not test_case["should_pass"]:
                    print(f"   ✅ 正确失败: {str(e)}")
                else:
                    print(f"   ❌ 不应该失败: {str(e)}")
        
        await adapter.client.aclose()
        print("\n✅ URL验证功能测试完成")
        
    except Exception as e:
        print(f"❌ URL验证测试失败: {str(e)}")
        traceback.print_exc()

async def main():
    """主测试函数"""
    print("🚀 开始简化的发布功能测试\n")
    
    # 测试适配器基础功能
    await test_adapter_basic()
    
    # 直接测试发布工具
    await test_publish_tool_direct()
    
    # 测试内容分析功能
    await test_content_analysis()
    
    # 测试URL验证功能
    await test_url_validation()
    
    print("\n🎉 简化测试完成！")
    print("\n📝 测试总结:")
    print("✅ 测试了适配器基础功能")
    print("✅ 测试了发布工具的参数验证")
    print("✅ 测试了工具执行流程")
    print("✅ 测试了内容质量分析")
    print("✅ 测试了URL验证功能")
    
    print("\n📝 下一步:")
    print("1. 确保 FastAPI 服务正在运行 (python main.py)")
    print("2. 运行完整的 MCP 服务端测试")
    print("3. 在 AI 客户端中配置和测试 MCP 连接")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        traceback.print_exc() 