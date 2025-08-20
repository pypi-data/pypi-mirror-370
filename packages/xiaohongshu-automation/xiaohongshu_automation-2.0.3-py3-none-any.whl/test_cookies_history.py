#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试cookies历史记录功能
"""

import requests
import json
import time
import os

# 服务器配置
BASE_URL = "http://localhost:8000"

def test_cookies_history():
    """测试cookies历史记录功能"""
    print("🧪 测试cookies历史记录功能")
    print("="*50)
    
    try:
        # 1. 测试获取cookies历史记录
        print("1️⃣ 测试获取cookies历史记录...")
        response = requests.get(f"{BASE_URL}/account/cookies_history")
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success"):
                print(f"✅ 成功获取cookies历史记录")
                print(f"📊 发现 {len(data.get('phone_numbers', []))} 个历史账号")
                
                for cookie_file in data.get('cookies_files', []):
                    phone = cookie_file['phone_number']
                    size = cookie_file['file_size_kb']
                    count = cookie_file['cookies_count']
                    active = cookie_file['is_active']
                    status = "✅ 已激活" if active else "❌ 未激活"
                    
                    print(f"   📱 {phone}: {size}KB, {count}个cookies, {status}")
                
            else:
                print(f"❌ 获取失败: {data.get('message', '未知错误')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
    
    print("\n" + "="*50)
    
    # 2. 测试从cookies添加账号（如果有未激活的账号）
    try:
        print("2️⃣ 测试从cookies添加账号...")
        
        # 获取历史记录
        response = requests.get(f"{BASE_URL}/account/cookies_history")
        if response.status_code == 200:
            data = response.json()
            inactive_accounts = [
                cookie['phone_number'] for cookie in data.get('cookies_files', [])
                if not cookie.get('is_active') and cookie['phone_number'] != 'default'
            ]
            
            if inactive_accounts:
                test_phone = inactive_accounts[0]
                print(f"尝试添加账号: {test_phone}")
                
                add_response = requests.post(
                    f"{BASE_URL}/account/add_from_cookies",
                    params={"phone_number": test_phone}
                )
                
                if add_response.status_code == 200:
                    add_data = add_response.json()
                    if add_data.get("success"):
                        print(f"✅ 成功从cookies添加账号: {test_phone}")
                    else:
                        print(f"❌ 添加失败: {add_data.get('message')}")
                else:
                    print(f"❌ HTTP错误: {add_response.status_code}")
            else:
                print("ℹ️ 没有找到未激活的账号，跳过测试")
        
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")
    
    print("\n" + "="*50)

def test_account_management_page():
    """测试账号管理页面"""
    print("3️⃣ 测试账号管理页面...")
    
    try:
        response = requests.get(f"{BASE_URL}/account/manage")
        
        if response.status_code == 200:
            html_content = response.text
            
            # 检查是否包含关键元素
            checks = [
                ("cookies历史记录区域", "Cookies历史记录" in html_content),
                ("loadCookiesHistory函数", "loadCookiesHistory" in html_content),
                ("addAccountFromCookies函数", "addAccountFromCookies" in html_content),
                ("cookies-history-grid CSS类", "cookies-history-grid" in html_content),
            ]
            
            all_passed = True
            for check_name, result in checks:
                status = "✅ 通过" if result else "❌ 失败"
                print(f"   {status} {check_name}")
                if not result:
                    all_passed = False
            
            if all_passed:
                print(f"✅ 账号管理页面包含所有必要元素")
            else:
                print(f"❌ 账号管理页面缺少某些元素")
        else:
            print(f"❌ 无法访问管理页面: {response.status_code}")
    
    except Exception as e:
        print(f"❌ 测试异常: {str(e)}")

def print_instructions():
    """打印使用说明"""
    print("\n" + "🎯 功能说明" + "="*40)
    print("✨ 新增功能：Cookies历史记录")
    print("📍 作用：从cookies文件夹中读取历史登录账号信息")
    print("🎨 界面：在/account/manage页面新增历史记录区域")
    print("🚀 操作：点击'查看历史账号'按钮可展示所有历史账号")
    print("⚡ 快捷：点击'快速添加'按钮可直接添加历史账号")
    print("📊 信息：显示文件大小、cookies数量、最后修改时间")
    print("🏷️ 状态：区分已激活和未激活账号")
    print("\n" + "🔗 相关接口" + "="*40)
    print("GET  /account/cookies_history     - 获取cookies历史记录")
    print("POST /account/add_from_cookies    - 从cookies添加账号")
    print("GET  /account/manage              - 账号管理页面（含历史记录）")
    print("\n" + "💡 使用建议" + "="*40)
    print("1. 首次使用时点击'查看历史账号'按钮")
    print("2. 选择需要的历史账号点击'快速添加'")
    print("3. 添加成功后会自动刷新状态")
    print("4. 已激活的账号会显示'已在使用中'")
    print("="*60)

if __name__ == "__main__":
    print("🌹 小红书Cookies历史记录功能测试")
    print("="*60)
    print("🔧 开始测试...")
    print()
    
    test_cookies_history()
    test_account_management_page()
    print_instructions()
    
    print("\n🎉 测试完成！")
    print("💻 请访问 http://localhost:8000/account/manage 查看新功能") 