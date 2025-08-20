#!/usr/bin/env python3
"""
测试小红书搜索功能
"""

import asyncio
import logging
from adapters.xiaohongshu_adapter import XiaohongshuAdapter
from tools.search_tool import SearchNotesTool

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_search_tool():
    """测试搜索工具"""
    try:
        # 创建适配器和工具
        adapter = XiaohongshuAdapter()
        search_tool = SearchNotesTool(adapter)
        
        # 测试参数
        test_cases = [
            {"keywords": "美食", "limit": 3},
            {"keywords": "旅行", "limit": 5},
            {"keywords": "Python编程"},  # 使用默认limit
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'='*50}")
            print(f"测试用例 {i}: {test_case}")
            print(f"{'='*50}")
            
            # 执行搜索
            result = await search_tool.execute(test_case)
            
            # 格式化并打印结果
            if result.success:
                formatted_result = search_tool._format_success_result(result)
                print(formatted_result)
            else:
                print(f"❌ 搜索失败: {result.error}")
                if result.message:
                    print(f"📝 详细信息: {result.message}")
        
        await adapter.client.aclose()
        
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")

def main():
    """主函数"""
    print("🔍 开始测试小红书搜索功能...")
    asyncio.run(test_search_tool())
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    main() 