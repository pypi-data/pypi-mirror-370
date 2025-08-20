#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试30秒登录等待功能
"""

import requests
import time

def test_login_wait():
    """测试30秒登录等待功能"""
    print("🧪 测试30秒登录等待功能")
    print("=" * 50)
    
    try:
        # 删除现有账号（如果存在）
        print("1. 清理现有账号...")
        response = requests.delete("http://localhost:8000/account/remove?phone_number=test_login_wait")
        print(f"   删除结果: {response.status_code}")
        
        # 添加新账号，这会触发cookies检查
        print("2. 添加账号 test_login_wait...")
        print("   这将会触发登录状态检查")
        print("   如果检测到未登录，系统会等待30秒让你手动登录")
        
        start_time = time.time()
        response = requests.post("http://localhost:8000/account/add?phone_number=test_login_wait", timeout=60)
        end_time = time.time()
        
        print(f"   响应时间: {end_time - start_time:.1f} 秒")
        print(f"   状态码: {response.status_code}")
        print(f"   响应内容: {response.text}")
        
        # 检查账号状态
        print("3. 检查账号状态...")
        response = requests.get("http://localhost:8000/account/status")
        print(f"   账号状态: {response.json()}")
        
        print("\n✅ 测试完成!")
        print("💡 如果系统检测到未登录状态，你应该看到30秒的等待时间")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")

if __name__ == "__main__":
    test_login_wait() 