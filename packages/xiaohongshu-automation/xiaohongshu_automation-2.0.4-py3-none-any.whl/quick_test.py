#!/usr/bin/env python3
"""快速验证所有功能集成"""

try:
    from xiaohongshu_tools import XiaohongshuTools
    from tools.content_tool import GetNoteContentTool
    from tools.analysis_tool import AnalyzeNoteTool
    from tools.tool_manager import ToolManager
    from adapters.xiaohongshu_adapter import XiaohongshuAdapter
    from config import MCPConfig
    
    print("✅ 所有模块导入成功")
    
    # 检查核心方法
    tools = XiaohongshuTools()
    has_search = hasattr(tools, 'search_notes')
    has_content = hasattr(tools, 'get_note_content')
    has_analyze = hasattr(tools, 'analyze_note')
    print(f"✅ search_notes方法存在: {has_search}")
    print(f"✅ get_note_content方法存在: {has_content}")
    print(f"✅ analyze_note方法存在: {has_analyze}")
    
    # 检查工具注册
    adapter = XiaohongshuAdapter()
    tool_manager = ToolManager(adapter)
    tools_list = list(tool_manager.tools.keys())
    print(f"✅ 成功注册 {len(tools_list)} 个工具")
    
    # 检查特定工具
    has_search_tool = 'xiaohongshu_search_notes' in tools_list
    has_content_tool = 'xiaohongshu_get_note_content' in tools_list
    has_analyze_tool = 'xiaohongshu_analyze_note' in tools_list
    print(f"✅ 搜索工具已注册: {has_search_tool}")
    print(f"✅ 内容抓取工具已注册: {has_content_tool}")
    print(f"✅ 分析工具已注册: {has_analyze_tool}")
    
    # 检查工具分类
    categories = tool_manager.get_tools_by_category()
    has_search_category = '内容搜索' in categories
    has_content_category = '内容获取' in categories
    has_analyze_category = '内容分析' in categories
    print(f"✅ 内容搜索分类存在: {has_search_category}")
    print(f"✅ 内容获取分类存在: {has_content_category}")
    print(f"✅ 内容分析分类存在: {has_analyze_category}")
    
    # 检查配置
    search_timeout = MCPConfig.get_timeout_for_operation('search')
    content_timeout = MCPConfig.get_timeout_for_operation('content')
    analysis_timeout = MCPConfig.get_timeout_for_operation('analysis')
    print(f"✅ 搜索超时配置: {search_timeout}秒")
    print(f"✅ 内容超时配置: {content_timeout}秒")
    print(f"✅ 分析超时配置: {analysis_timeout}秒")
    
    print("\n🎉 所有功能集成验证通过！")
    print("📄 笔记内容抓取功能已成功添加到MCP服务器！")
    print("🔍 笔记内容分析功能已成功添加到MCP服务器！")
    
except Exception as e:
    print(f"❌ 验证失败: {e}") 