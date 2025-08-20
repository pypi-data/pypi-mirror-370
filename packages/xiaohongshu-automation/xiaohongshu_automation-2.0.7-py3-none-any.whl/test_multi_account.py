#!/usr/bin/env python3
"""
小红书多账号功能测试脚本
用于验证多账号管理和操作功能
"""

import requests
import time
import json
from typing import List, Dict, Any

class XHSMultiAccountTester:
    """小红书多账号功能测试器"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_account_management(self) -> Dict[str, Any]:
        """测试账号管理功能"""
        print("🧪 开始测试账号管理功能...")
        results = {}
        
        test_accounts = ["13800138000", "13900139000", "13700137000"]
        
        # 1. 测试添加账号
        print("1️⃣ 测试添加账号...")
        add_results = []
        for phone in test_accounts:
            try:
                response = self.session.post(f"{self.base_url}/account/add", json={
                    "phone_number": phone
                })
                result = response.json()
                add_results.append({"phone": phone, "result": result})
                print(f"   添加账号 {phone}: {'✅' if result.get('success') else '❌'}")
                time.sleep(1)
            except Exception as e:
                print(f"   添加账号 {phone} 失败: {str(e)}")
                add_results.append({"phone": phone, "error": str(e)})
        
        results["add_accounts"] = add_results
        
        # 2. 测试获取账号列表
        print("2️⃣ 测试获取账号列表...")
        try:
            response = self.session.get(f"{self.base_url}/account/list")
            list_result = response.json()
            results["list_accounts"] = list_result
            print(f"   账号列表: {list_result.get('accounts', [])}")
            print(f"   当前账号: {list_result.get('current_account', 'None')}")
        except Exception as e:
            print(f"   获取账号列表失败: {str(e)}")
            results["list_accounts"] = {"error": str(e)}
        
        # 3. 测试设置当前账号
        print("3️⃣ 测试设置当前账号...")
        if test_accounts:
            try:
                response = self.session.post(f"{self.base_url}/account/set_current", json={
                    "phone_number": test_accounts[0]
                })
                set_result = response.json()
                results["set_current"] = set_result
                print(f"   设置当前账号为 {test_accounts[0]}: {'✅' if set_result.get('success') else '❌'}")
            except Exception as e:
                print(f"   设置当前账号失败: {str(e)}")
                results["set_current"] = {"error": str(e)}
        
        return results
    
    def test_account_login(self, phone_number: str) -> Dict[str, Any]:
        """测试账号登录功能"""
        print(f"🔑 测试账号 {phone_number} 登录...")
        
        try:
            # 测试无验证码登录
            response = self.session.post(f"{self.base_url}/account/login", json={
                "phone_number": phone_number
            })
            result = response.json()
            print(f"   无验证码登录: {'✅' if result.get('success') else '❌'}")
            print(f"   登录消息: {result.get('message', 'N/A')}")
            return result
        except Exception as e:
            print(f"   登录失败: {str(e)}")
            return {"error": str(e)}
    
    def test_publish_content(self, phone_number: str = None) -> Dict[str, Any]:
        """测试发布内容功能"""
        account_info = phone_number or "默认账号"
        print(f"📝 测试 {account_info} 发布内容...")
        
        test_data = {
            "pic_urls": ["https://via.placeholder.com/800x600.jpg"],
            "title": f"多账号测试发布 - {account_info}",
            "content": f"这是使用账号 {account_info} 的测试发布内容。测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "labels": ["测试", "多账号"]
        }
        
        if phone_number:
            test_data["phone_number"] = phone_number
        
        try:
            response = self.session.post(f"{self.base_url}/publish", json=test_data)
            result = response.json()
            print(f"   发布结果: {'✅' if result.get('status') == 'success' else '❌'}")
            print(f"   使用账号: {result.get('account', 'N/A')}")
            if result.get('status') != 'success':
                print(f"   错误信息: {result.get('message', 'N/A')}")
            return result
        except Exception as e:
            print(f"   发布失败: {str(e)}")
            return {"error": str(e)}
    
    def test_search_notes(self, phone_number: str = None) -> Dict[str, Any]:
        """测试搜索笔记功能"""
        account_info = phone_number or "默认账号"
        print(f"🔍 测试 {account_info} 搜索笔记...")
        
        params = {
            "keywords": "美食",
            "limit": 5
        }
        
        if phone_number:
            params["phone_number"] = phone_number
        
        try:
            response = self.session.get(f"{self.base_url}/search_notes", params=params)
            result = response.json()
            print(f"   搜索结果: {'✅' if result.get('success') else '❌'}")
            print(f"   使用账号: {result.get('account', 'N/A')}")
            print(f"   找到笔记数: {len(result.get('data', []))}")
            return result
        except Exception as e:
            print(f"   搜索失败: {str(e)}")
            return {"error": str(e)}
    
    def test_batch_operations(self, accounts: List[str]) -> Dict[str, Any]:
        """测试批量操作功能"""
        print("🔄 测试批量操作功能...")
        batch_results = []
        
        for i, account in enumerate(accounts):
            print(f"   处理账号 {i+1}/{len(accounts)}: {account}")
            
            # 测试发布
            publish_result = self.test_publish_content(account)
            
            # 测试搜索
            search_result = self.test_search_notes(account)
            
            batch_results.append({
                "account": account,
                "publish": publish_result,
                "search": search_result
            })
            
            # 避免请求过于频繁
            time.sleep(2)
        
        return {"batch_results": batch_results}
    
    def run_comprehensive_test(self) -> Dict[str, Any]:
        """运行综合测试"""
        print("🚀 开始小红书多账号功能综合测试")
        print("=" * 60)
        
        all_results = {}
        
        # 1. 测试账号管理
        account_mgmt_results = self.test_account_management()
        all_results["account_management"] = account_mgmt_results
        
        time.sleep(2)
        
        # 2. 获取可用账号
        available_accounts = []
        try:
            response = self.session.get(f"{self.base_url}/account/list")
            list_result = response.json()
            available_accounts = list_result.get("accounts", [])
        except:
            available_accounts = ["13800138000"]  # 备用测试账号
        
        print(f"\n📋 可用测试账号: {available_accounts}")
        
        # 3. 测试账号登录
        login_results = []
        for account in available_accounts[:2]:  # 只测试前两个账号
            login_result = self.test_account_login(account)
            login_results.append({"account": account, "result": login_result})
            time.sleep(1)
        
        all_results["login_tests"] = login_results
        
        # 4. 测试单账号操作
        print("\n📱 测试单账号操作...")
        if available_accounts:
            test_account = available_accounts[0]
            single_account_results = {
                "publish": self.test_publish_content(test_account),
                "search": self.test_search_notes(test_account)
            }
            all_results["single_account_tests"] = single_account_results
        
        # 5. 测试默认账号操作（不指定phone_number）
        print("\n🎯 测试默认账号操作...")
        default_account_results = {
            "publish": self.test_publish_content(),
            "search": self.test_search_notes()
        }
        all_results["default_account_tests"] = default_account_results
        
        # 6. 测试批量操作
        if len(available_accounts) > 1:
            batch_results = self.test_batch_operations(available_accounts[:2])
            all_results["batch_tests"] = batch_results
        
        print("\n" + "=" * 60)
        print("✅ 综合测试完成")
        
        return all_results
    
    def save_test_results(self, results: Dict[str, Any], filename: str = None):
        """保存测试结果到文件"""
        if filename is None:
            filename = f"multi_account_test_results_{int(time.time())}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"📊 测试结果已保存到: {filename}")
        except Exception as e:
            print(f"❌ 保存测试结果失败: {str(e)}")

def main():
    """主函数"""
    print("🎯 小红书多账号功能测试工具")
    print("请确保服务已启动在 http://localhost:8000")
    
    # 等待用户确认
    input("按回车键开始测试...")
    
    # 创建测试器
    tester = XHSMultiAccountTester()
    
    try:
        # 运行综合测试
        results = tester.run_comprehensive_test()
        
        # 保存结果
        tester.save_test_results(results)
        
        # 输出简要总结
        print("\n📋 测试总结:")
        print(f"   账号管理测试: {'✅' if 'account_management' in results else '❌'}")
        print(f"   登录测试: {'✅' if 'login_tests' in results else '❌'}")
        print(f"   单账号操作测试: {'✅' if 'single_account_tests' in results else '❌'}")
        print(f"   默认账号测试: {'✅' if 'default_account_tests' in results else '❌'}")
        print(f"   批量操作测试: {'✅' if 'batch_tests' in results else '❌'}")
        
    except KeyboardInterrupt:
        print("\n❌ 测试被用户中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main() 