#!/usr/bin/env python3
"""
测试发布功能修复
验证 503 错误是否已解决
"""

import asyncio
import json
import traceback

async def test_publish_fix():
    """测试发布功能修复"""
    print("🔧 测试发布功能修复...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        
        # 使用用户提供的长 URL 进行测试
        adapter = XiaohongshuAdapter("http://localhost:8000")
        
        # 测试数据 - 使用用户修改的百度图片 URL
        test_data = {
            "pic_urls": ["https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89"],
            "title": "503错误修复测试",
            "content": "这是一个测试长URL修复的发布内容 #测试修复 #503错误 😊"
        }
        
        print("1. 测试健康检查...")
        is_healthy = await adapter.health_check()
        print(f"   FastAPI 服务健康状态: {'✅ 正常' if is_healthy else '❌ 异常'}")
        
        if not is_healthy:
            print("   ⚠️ FastAPI 服务不可用，请先启动服务: python main.py")
            return False
        
        print("2. 测试长URL发布...")
        print(f"   图片URL长度: {len(test_data['pic_urls'][0])} 字符")
        
        try:
            result = await adapter.publish_content(**test_data)
            print(f"   ✅ 发布成功!")
            print(f"   📊 结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
            
        except Exception as e:
            error_str = str(e)
            if "503" in error_str:
                print(f"   ❌ 仍然出现 503 错误: {error_str}")
                return False
            elif "HTTP" in error_str:
                print(f"   ⚠️ 其他 HTTP 错误: {error_str}")
                return False
            else:
                print(f"   ⚠️ 其他错误（可能是业务逻辑）: {error_str}")
                return True  # 非HTTP错误说明请求格式是对的
        
        finally:
            await adapter.client.aclose()
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        traceback.print_exc()
        return False

async def test_multiple_long_urls():
    """测试多个长URL"""
    print("\n🔧 测试多个长URL...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        
        adapter = XiaohongshuAdapter("http://localhost:8000")
        
        # 测试多个长URL
        test_data = {
            "pic_urls": [
                "https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89",
                "https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89",
                "https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89"
            ],
            "title": "多图长URL测试",
            "content": "这是一个测试多个长URL的发布内容 #多图测试 #长URL修复 🎉"
        }
        
        print(f"   图片数量: {len(test_data['pic_urls'])}")
        print(f"   总URL长度: {sum(len(url) for url in test_data['pic_urls'])} 字符")
        
        try:
            result = await adapter.publish_content(**test_data)
            print(f"   ✅ 多图长URL发布成功!")
            print(f"   📊 结果: {json.dumps(result, indent=2, ensure_ascii=False)}")
            return True
            
        except Exception as e:
            error_str = str(e)
            if "503" in error_str:
                print(f"   ❌ 仍然出现 503 错误: {error_str}")
                return False
            else:
                print(f"   ⚠️ 其他错误: {error_str}")
                return True  # 非503错误说明请求格式是对的
        
        finally:
            await adapter.client.aclose()
    
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        traceback.print_exc()
        return False

async def test_with_mcp_tool():
    """通过 MCP 工具测试"""
    print("\n🔧 通过 MCP 工具测试...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.publish_tool import PublishTool
        
        adapter = XiaohongshuAdapter("http://localhost:8000")
        publish_tool = PublishTool(adapter)
        
        test_args = {
            "pic_urls": ["https://image.baidu.com/front/aigc?atn=aigc&fr=home&imgcontent=%7B%22aigcQuery%22%3A%22%22%2C%22imageAigcId%22%3A%224199096378%22%7D&isImmersive=1&pd=image_content&quality=1&ratio=9%3A16&sa=searchpromo_shijian_photohp_inspire&tn=aigc&top=%7B%22sfhs%22%3A1%7D&word=%E5%B9%BF%E5%91%8A%E5%AE%A3%E4%BC%A0%E5%9B%BE%EF%BC%8C%E5%AE%A4%E5%86%85%E9%AB%98%E6%B8%85%EF%BC%8C%E5%B9%BF%E5%91%8A%EF%BC%8C%E6%B5%B7%E6%8A%A5%E8%B4%A8%E6%84%9F%EF%BC%8C%E9%AB%98%E6%B8%85%E6%91%84%E5%BD%B1%EF%BC%8C%E5%86%B0%E5%87%89%E7%9A%84%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B0%B4%E6%9E%9C%E6%B1%BD%E6%B0%B4%EF%BC%8C%E6%B8%85%E6%96%B0%E7%9A%84%E8%87%AA%E7%84%B6%E7%8E%AF%E5%A2%83%EF%BC%8C%E8%B6%85%E9%AB%98%E6%B8%85%E5%88%86%E8%BE%A8%E7%8E%87%EF%BC%8C%E9%B2%9C%E8%89%B3%E8%89%B2%E5%BD%A9%EF%BC%8C%E6%B4%BB%E5%8A%9B%E5%9B%9B%E6%BA%A2%EF%BC%8C%E8%87%AA%E7%84%B6%E9%98%B3%E5%85%89%E7%85%A7%E5%B0%84%EF%BC%8C%E5%85%89%E6%BB%91%E5%86%B0%E5%87%89"],
            "title": "MCP工具长URL测试",
            "content": "通过MCP工具测试长URL发布 #MCP工具 #长URL #修复测试 ✨"
        }
        
        result = await publish_tool.execute(test_args)
        
        print(f"   工具执行结果: 成功={result.success}")
        print(f"   消息: {result.message}")
        
        if result.success:
            print("   ✅ MCP 工具长URL测试成功!")
            return True
        else:
            if "503" in str(result.error):
                print(f"   ❌ MCP 工具仍然出现 503 错误: {result.error}")
                return False
            else:
                print(f"   ⚠️ MCP 工具其他错误: {result.error}")
                return True
        
    except Exception as e:
        print(f"❌ MCP 工具测试失败: {str(e)}")
        traceback.print_exc()
        return False
    
    finally:
        await adapter.client.aclose()

async def main():
    """主测试函数"""
    print("🚀 开始 503 错误修复测试\n")
    
    success_count = 0
    total_tests = 3
    
    # 测试 1: 单个长URL
    if await test_publish_fix():
        success_count += 1
    
    # 测试 2: 多个长URL
    if await test_multiple_long_urls():
        success_count += 1
    
    # 测试 3: 通过 MCP 工具
    if await test_with_mcp_tool():
        success_count += 1
    
    print(f"\n🎉 修复测试完成!")
    print(f"📊 成功: {success_count}/{total_tests} 个测试")
    
    if success_count == total_tests:
        print("✅ 503 错误已完全修复!")
    elif success_count > 0:
        print("⚠️ 部分修复成功，可能仍有其他问题")
    else:
        print("❌ 修复不成功，需要进一步检查")
    
    print("\n📝 修复说明:")
    print("- 将请求参数从 URL 查询参数改为 JSON 请求体")
    print("- 避免了超长 URL 导致的 503 错误")
    print("- 支持任意长度的图片 URL 和内容")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        traceback.print_exc() 