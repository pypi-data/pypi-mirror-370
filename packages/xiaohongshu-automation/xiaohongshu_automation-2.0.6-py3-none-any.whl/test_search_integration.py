#!/usr/bin/env python3
"""
搜索功能集成测试
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
        from tools.search_tool import SearchNotesTool
        print("✅ SearchNotesTool 导入成功")
    except Exception as e:
        print(f"❌ SearchNotesTool 导入失败: {e}")
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
        
        if "xiaohongshu_search_notes" in tools:
            print("✅ 搜索工具已正确注册")
            return True
        else:
            print("❌ 搜索工具未找到")
            print(f"已注册的工具: {tools}")
            return False
            
    except Exception as e:
        print(f"❌ 工具注册测试失败: {e}")
        return False

def test_search_tool_schema():
    """测试搜索工具的Schema"""
    print("\n📋 测试搜索工具Schema...")
    
    try:
        from adapters.xiaohongshu_adapter import XiaohongshuAdapter
        from tools.search_tool import SearchNotesTool
        
        adapter = XiaohongshuAdapter()
        search_tool = SearchNotesTool(adapter)
        
        schema = search_tool.get_schema()
        print("✅ Schema获取成功")
        
        # 检查必需字段
        if "keywords" in schema.get("required", []):
            print("✅ keywords字段已设为必需")
        else:
            print("❌ keywords字段未设为必需")
            return False
        
        # 检查属性定义
        properties = schema.get("properties", {})
        if "keywords" in properties and "limit" in properties:
            print("✅ 所有必需属性已定义")
            return True
        else:
            print("❌ 属性定义不完整")
            return False
            
    except Exception as e:
        print(f"❌ Schema测试失败: {e}")
        return False

def test_xiaohongshu_tools_method():
    """测试xiaohongshu_tools中的search_notes方法"""
    print("\n🛠️ 测试xiaohongshu_tools.search_notes方法...")
    
    try:
        from xiaohongshu_tools import XiaohongshuTools
        
        # 检查方法是否存在
        tools = XiaohongshuTools()
        if hasattr(tools, 'search_notes'):
            print("✅ search_notes方法存在")
            
            # 检查方法签名
            import inspect
            sig = inspect.signature(tools.search_notes)
            params = list(sig.parameters.keys())
            
            if 'keywords' in params and 'limit' in params:
                print("✅ 方法参数正确")
                return True
            else:
                print(f"❌ 方法参数不正确: {params}")
                return False
        else:
            print("❌ search_notes方法不存在")
            return False
            
    except Exception as e:
        print(f"❌ xiaohongshu_tools方法测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始搜索功能集成测试\n")
    
    tests = [
        ("模块导入", test_imports),
        ("工具注册", test_tool_registration),
        ("工具Schema", test_search_tool_schema),
        ("核心方法", test_xiaohongshu_tools_method),
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
        print("🎉 所有测试通过！搜索功能集成成功！")
        return True
    else:
        print("⚠️ 部分测试失败，请检查相关配置")
        return False

if __name__ == "__main__":
    main() 