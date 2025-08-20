#!/usr/bin/env python3
"""
测试小红书笔记分析功能
"""

import asyncio
import logging
from adapters.xiaohongshu_adapter import XiaohongshuAdapter
from tools.analysis_tool import AnalyzeNoteTool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_analysis_tool():
    """测试分析工具"""
    try:
        # 创建适配器和工具
        adapter = XiaohongshuAdapter()
        analysis_tool = AnalyzeNoteTool(adapter)
        
        # 测试参数 - 使用实际的小红书笔记URL进行测试
        test_cases = [
            {
                "url": "https://www.xiaohongshu.com/explore/67b94551000000002902b506",
                "description": "测试分析具体笔记内容"
            },
            {
                "url": "https://www.xiaohongshu.com/explore/invalid_url",
                "description": "测试无效URL处理"
            },
            {
                "url": "",
                "description": "测试空URL处理"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"测试用例 {i}: {test_case['description']}")
            print(f"URL: {test_case['url']}")
            print(f"{'='*60}")
            
            # 执行分析
            result = await analysis_tool.execute(test_case)
            
            # 格式化并打印结果
            if result.success:
                formatted_result = analysis_tool._format_success_result(result)
                print(formatted_result)
            else:
                print(f"❌ 分析失败: {result.error}")
                if result.message:
                    print(f"📝 详细信息: {result.message}")
        
        await adapter.client.aclose()
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")

async def test_integration():
    """测试完整集成流程"""
    try:
        print(f"\n{'='*60}")
        print("测试完整集成流程")
        print(f"{'='*60}")
        
        # 创建适配器
        adapter = XiaohongshuAdapter()
        
        # 测试适配器直接调用
        test_url = "https://www.xiaohongshu.com/explore/67b94551000000002902b506"
        result = await adapter.analyze_note(test_url)
        
        if result.get("success"):
            data = result.get("data", {})
            basic_info = data.get("基础信息", {})
            domain_analysis = data.get("领域分析", {})
            
            print("✅ 适配器直接调用成功")
            print(f"📝 标题: {basic_info.get('标题', 'N/A')}")
            print(f"👤 作者: {basic_info.get('作者', 'N/A')}")
            print(f"📅 发布时间: {basic_info.get('发布时间', 'N/A')}")
            print(f"🎯 主要领域: {', '.join(domain_analysis.get('主要领域', []))}")
            print(f"📊 内容长度: {basic_info.get('内容长度', 0)} 字符")
            
            # 显示分析指标
            metrics = data.get("分析指标", {})
            if metrics:
                print(f"🌟 内容质量: {metrics.get('内容质量', 'N/A')}")
                print(f"💡 信息丰富度: {metrics.get('信息丰富度', 'N/A')}")
                print(f"🎯 领域明确度: {metrics.get('领域明确度', 'N/A')}")
        else:
            print(f"❌ 适配器调用失败: {result.get('message', '未知错误')}")
        
        await adapter.client.aclose()
        
    except Exception as e:
        logger.error(f"集成测试过程中出错: {str(e)}")

def main():
    """主函数"""
    print("🔍 开始测试小红书笔记分析功能...")
    
    # 运行工具测试
    asyncio.run(test_analysis_tool())
    
    # 运行集成测试
    asyncio.run(test_integration())
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    main() 