#!/usr/bin/env python3
"""
小红书多账号功能使用示例
演示如何使用多账号进行批量操作
"""

import requests
import time
import json
from typing import List

class XHSMultiAccountExample:
    """小红书多账号功能示例"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    def setup_accounts(self, phone_numbers: List[str]):
        """设置多个账号"""
        print("🚀 开始设置多个账号...")
        
        for phone in phone_numbers:
            try:
                response = requests.post(f"{self.base_url}/account/add", json={
                    "phone_number": phone
                })
                result = response.json()
                if result.get("success"):
                    print(f"✅ 账号 {phone} 添加成功")
                else:
                    print(f"❌ 账号 {phone} 添加失败: {result.get('message')}")
            except Exception as e:
                print(f"❌ 账号 {phone} 添加异常: {str(e)}")
            
            time.sleep(1)  # 避免请求过快
    
    def login_accounts(self, phone_numbers: List[str]):
        """登录多个账号"""
        print("\n🔑 开始登录多个账号...")
        
        for phone in phone_numbers:
            try:
                response = requests.post(f"{self.base_url}/account/login", json={
                    "phone_number": phone
                })
                result = response.json()
                if result.get("success"):
                    print(f"✅ 账号 {phone} 登录成功")
                else:
                    print(f"❌ 账号 {phone} 登录失败: {result.get('message')}")
            except Exception as e:
                print(f"❌ 账号 {phone} 登录异常: {str(e)}")
            
            time.sleep(1)
    
    def batch_publish(self, phone_numbers: List[str], base_content: dict):
        """批量发布内容到多个账号"""
        print("\n📝 开始批量发布内容...")
        
        results = []
        for i, phone in enumerate(phone_numbers):
            try:
                # 为每个账号定制内容
                content_data = base_content.copy()
                content_data["title"] = f"{base_content['title']} - 账号{i+1}"
                content_data["content"] = f"{base_content['content']}\n\n发布账号: {phone}"
                content_data["phone_number"] = phone
                
                response = requests.post(f"{self.base_url}/publish", json=content_data)
                result = response.json()
                
                if result.get("status") == "success":
                    print(f"✅ 账号 {phone} 发布成功")
                    results.append({"phone": phone, "success": True, "urls": result.get("urls")})
                else:
                    print(f"❌ 账号 {phone} 发布失败: {result.get('message')}")
                    results.append({"phone": phone, "success": False, "error": result.get("message")})
                
            except Exception as e:
                print(f"❌ 账号 {phone} 发布异常: {str(e)}")
                results.append({"phone": phone, "success": False, "error": str(e)})
            
            # 账号间延迟，避免操作过快
            time.sleep(5)
        
        return results
    
    def batch_search(self, phone_numbers: List[str], keywords: str):
        """批量搜索笔记"""
        print(f"\n🔍 开始使用多个账号搜索: {keywords}")
        
        results = []
        for phone in phone_numbers:
            try:
                response = requests.get(f"{self.base_url}/search_notes", params={
                    "keywords": keywords,
                    "limit": 5,
                    "phone_number": phone
                })
                result = response.json()
                
                if result.get("success"):
                    count = len(result.get("data", []))
                    print(f"✅ 账号 {phone} 搜索成功，找到 {count} 条笔记")
                    results.append({"phone": phone, "success": True, "count": count})
                else:
                    print(f"❌ 账号 {phone} 搜索失败: {result.get('message')}")
                    results.append({"phone": phone, "success": False, "error": result.get("message")})
                
            except Exception as e:
                print(f"❌ 账号 {phone} 搜索异常: {str(e)}")
                results.append({"phone": phone, "success": False, "error": str(e)})
            
            time.sleep(2)
        
        return results
    
    def show_account_status(self):
        """显示账号状态"""
        print("\n📊 账号状态概览:")
        
        try:
            response = requests.get(f"{self.base_url}/account/list")
            result = response.json()
            
            if result.get("success"):
                accounts = result.get("accounts", [])
                current = result.get("current_account")
                
                print(f"   总账号数: {len(accounts)}")
                print(f"   当前账号: {current}")
                print(f"   账号列表: {', '.join(accounts)}")
            else:
                print("   获取账号状态失败")
                
        except Exception as e:
            print(f"   获取账号状态异常: {str(e)}")

def main():
    """主函数 - 演示多账号功能"""
    print("🎯 小红书多账号功能使用示例")
    print("=" * 50)
    
    # 配置示例账号（请替换为真实的手机号）
    example_accounts = [
        "13800138000",  # 替换为真实手机号
        "13900139000",  # 替换为真实手机号
        "13700137000"   # 替换为真实手机号
    ]
    
    # 示例发布内容
    example_content = {
        "pic_urls": [
            "https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Image1",
            "https://via.placeholder.com/800x600/4ECDC4/FFFFFF?text=Image2"
        ],
        "title": "多账号测试发布",
        "content": """这是一个多账号功能测试内容。

🌟 功能特点：
- 支持多账号管理
- 批量内容发布
- 账号间完全隔离
- 向后兼容单账号模式

测试时间: """ + time.strftime('%Y-%m-%d %H:%M:%S'),
        "labels": ["多账号", "测试", "自动化"]
    }
    
    # 创建示例实例
    example = XHSMultiAccountExample()
    
    try:
        # 1. 设置账号
        example.setup_accounts(example_accounts)
        
        # 2. 显示账号状态
        example.show_account_status()
        
        # 3. 登录账号
        example.login_accounts(example_accounts)
        
        # 4. 批量发布内容
        print("\n" + "=" * 50)
        print("开始批量发布演示（请确认继续）...")
        input("按回车键继续发布，或 Ctrl+C 取消...")
        
        publish_results = example.batch_publish(example_accounts, example_content)
        
        # 5. 批量搜索
        search_results = example.batch_search(example_accounts, "美食")
        
        # 6. 总结结果
        print("\n" + "=" * 50)
        print("📋 操作总结:")
        
        # 发布结果统计
        publish_success = sum(1 for r in publish_results if r.get("success"))
        print(f"   发布成功: {publish_success}/{len(example_accounts)}")
        
        # 搜索结果统计  
        search_success = sum(1 for r in search_results if r.get("success"))
        print(f"   搜索成功: {search_success}/{len(example_accounts)}")
        
        # 保存详细结果
        detailed_results = {
            "timestamp": time.strftime('%Y-%m-%d %H:%M:%S'),
            "accounts": example_accounts,
            "publish_results": publish_results,
            "search_results": search_results
        }
        
        filename = f"multi_account_example_results_{int(time.time())}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)
        
        print(f"   详细结果已保存到: {filename}")
        
    except KeyboardInterrupt:
        print("\n❌ 操作被用户取消")
    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
    
    print("\n✅ 多账号功能演示完成")

if __name__ == "__main__":
    # 安全提示
    print("⚠️  使用前请注意:")
    print("1. 确保小红书服务已启动 (python main.py)")
    print("2. 替换示例中的手机号为真实账号")
    print("3. 确保账号已完成登录授权")
    print("4. 注意操作频率，避免触发平台限制")
    print()
    
    confirm = input("确认要继续演示吗？(y/N): ")
    if confirm.lower() in ['y', 'yes']:
        main()
    else:
        print("演示已取消") 