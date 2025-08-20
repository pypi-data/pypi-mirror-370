#!/usr/bin/env python3
"""
笔记分析功能集成测试
验证从xiaohongshu_tools到MCP工具的完整流程
"""

def test_imports():
    """测试所有相关模块的导入"""
    print("🔍 测试模块导入...")
    
    try:
        from xiaohongshu_tools import XiaohongshuTools
        print("✅ xiaohongshu_tools.py 导入成功")
    except Exception as e:
        print(f"❌ xiaohongshu_tools.py 导入失败: {e}")
        return False
    
    try:
        from tools.analysis_tool import AnalyzeNoteTool
        print("✅ AnalyzeNoteTool 导入成功")
    except Exception as e:
        print(f"❌ AnalyzeNoteTool 导入失败: {e}")
        return False
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        print("✅ XiaohongshuAdapter 导入成功")
    except Exception as e:
        print(f"❌ XiaohongshuAdapter 导入失败: {e}")
        return False
    
    try:
        from tools.tool_manager import ToolManager
        print("✅ ToolManager 导入成功")
    except Exception as e:
        print(f"❌ ToolManager 导入失败: {e}")
        return False
    
    return True

def test_tool_registration():
    """测试工具注册"""
    print("\n🔧 测试工具注册...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.tool_manager import ToolManager
        
        adapter = XiaohongshuAdapter()
        tool_manager = ToolManager(adapter)
        
        tools = list(tool_manager.tools.keys())
        print(f"✅ 成功注册 {len(tools)} 个工具")
        
        if "xiaohongshu_analyze_note" in tools:
            print("✅ 分析工具已正确注册")
            return True
        else:
            print("❌ 分析工具未找到")
            print(f"已注册的工具: {tools}")
            return False
            
    except Exception as e:
        print(f"❌ 工具注册测试失败: {e}")
        return False

def test_analysis_tool_schema():
    """测试分析工具的Schema"""
    print("\n📋 测试分析工具Schema...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.analysis_tool import AnalyzeNoteTool
        
        adapter = XiaohongshuAdapter()
        analysis_tool = AnalyzeNoteTool(adapter)
        
        schema = analysis_tool.get_schema()
        print("✅ Schema获取成功")
        
        # 检查必需字段
        if "url" in schema.get("required", []):
            print("✅ url字段已设为必需")
        else:
            print("❌ url字段未设为必需")
            return False
        
        # 检查属性定义
        properties = schema.get("properties", {})
        if "url" in properties:
            print("✅ url属性已定义")
            
            # 检查URL模式匹配
            url_property = properties["url"]
            if "pattern" in url_property:
                print("✅ URL模式验证已设置")
                return True
            else:
                print("⚠️ URL模式验证未设置")
                return True
        else:
            print("❌ url属性定义缺失")
            return False
            
    except Exception as e:
        print(f"❌ Schema测试失败: {e}")
        return False

def test_xiaohongshu_tools_method():
    """测试xiaohongshu_tools中的analyze_note方法"""
    print("\n🛠️ 测试xiaohongshu_tools.analyze_note方法...")
    
    try:
        from xiaohongshu_tools import XiaohongshuTools
        
        # 检查方法是否存在
        tools = XiaohongshuTools()
        if hasattr(tools, 'analyze_note'):
            print("✅ analyze_note方法存在")
            
            # 检查方法签名
            import inspect
            sig = inspect.signature(tools.analyze_note)
            params = list(sig.parameters.keys())
            
            if 'url' in params:
                print("✅ 方法参数正确")
                return True
            else:
                print(f"❌ 方法参数不正确: {params}")
                return False
        else:
            print("❌ analyze_note方法不存在")
            return False
            
    except Exception as e:
        print(f"❌ xiaohongshu_tools方法测试失败: {e}")
        return False

def test_tool_categories():
    """测试工具分类"""
    print("\n📂 测试工具分类...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.tool_manager import ToolManager
        
        adapter = XiaohongshuAdapter()
        tool_manager = ToolManager(adapter)
        
        categories = tool_manager.get_tools_by_category()
        print(f"✅ 工具分类获取成功")
        
        if "内容分析" in categories:
            analysis_tools = categories["内容分析"]
            if "xiaohongshu_analyze_note" in analysis_tools:
                print("✅ 分析工具已正确分类")
                return True
            else:
                print("❌ 分析工具分类错误")
                print(f"内容分析分类中的工具: {analysis_tools}")
                return False
        else:
            print("❌ 内容分析分类不存在")
            print(f"可用分类: {list(categories.keys())}")
            return False
            
    except Exception as e:
        print(f"❌ 工具分类测试失败: {e}")
        return False

def test_config_integration():
    """测试配置集成"""
    print("\n⚙️ 测试配置集成...")
    
    try:
        from config import MCPConfig
        
        # 测试分析超时配置
        analysis_timeout = MCPConfig.get_timeout_for_operation("analysis")
        print(f"✅ 分析操作超时配置: {analysis_timeout}秒")
        
        # 测试适配器配置
        adapter_config = MCPConfig.get_adapter_config()
        if "analysis_timeout" in adapter_config:
            print("✅ 适配器配置包含分析超时设置")
            return True
        else:
            print("❌ 适配器配置缺少分析超时设置")
            return False
            
    except Exception as e:
        print(f"❌ 配置集成测试失败: {e}")
        return False

def test_api_endpoint():
    """测试FastAPI端点定义"""
    print("\n🌐 测试FastAPI端点...")
    
    try:
        import main
        from fastapi.routing import APIRoute
        
        # 检查是否存在analyze_note端点
        routes = main.app.routes
        analyze_route_found = False
        
        for route in routes:
            if isinstance(route, APIRoute) and route.path == "/analyze_note":
                analyze_route_found = True
                print("✅ analyze_note端点已定义")
                
                # 检查HTTP方法
                if "GET" in route.methods:
                    print("✅ 支持GET方法")
                    return True
                else:
                    print("❌ 不支持GET方法")
                    return False
        
        if not analyze_route_found:
            print("❌ analyze_note端点未找到")
            return False
            
    except Exception as e:
        print(f"❌ API端点测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始笔记分析功能集成测试\n")
    
    tests = [
        ("模块导入", test_imports),
        ("工具注册", test_tool_registration),
        ("工具Schema", test_analysis_tool_schema),
        ("核心方法", test_xiaohongshu_tools_method),
        ("工具分类", test_tool_categories),
        ("配置集成", test_config_integration),
        ("API端点", test_api_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"{'='*50}")
        print(f"测试: {test_name}")
        print(f"{'='*50}")
        
        if test_func():
            passed += 1
            print(f"✅ {test_name} 测试通过")
        else:
            print(f"❌ {test_name} 测试失败")
    
    print(f"\n{'='*50}")
    print(f"测试结果: {passed}/{total} 通过")
    print(f"{'='*50}")
    
    if passed == total:
        print("🎉 所有测试通过！笔记分析功能集成成功！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关配置")
        return False

if __name__ == "__main__":
    main() 