#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
账号管理功能测试脚本
测试账号添加、状态监控、历史记录等功能
"""

import requests
import json
import time
import sys
from datetime import datetime

# 服务器配置
BASE_URL = "http://localhost:8000"

class AccountManagementTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
        
    def print_separator(self, title):
        """打印分隔线"""
        print("\n" + "="*60)
        print(f"🔧 {title}")
        print("="*60)
    
    def test_server_status(self):
        """测试服务器状态"""
        self.print_separator("服务器状态检查")
        try:
            response = self.session.get(f"{self.base_url}/")
            if response.status_code == 200:
                data = response.json()
                print("✅ 服务器正常运行")
                print(f"📱 应用: {data.get('app')}")
                print(f"🔖 版本: {data.get('version')}")
                print(f"📊 当前账号数: {data.get('account_info', {}).get('total_accounts', 0)}")
                return True
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ 无法连接服务器: {str(e)}")
            return False
    
    def test_add_account(self, phone_number):
        """测试添加账号"""
        self.print_separator(f"添加账号: {phone_number}")
        try:
            response = self.session.post(
                f"{self.base_url}/account/add",
                json={"phone_number": phone_number}
            )
            data = response.json()
            if data.get("success"):
                print(f"✅ 账号 {phone_number} 添加成功")
                print(f"📝 消息: {data.get('message')}")
                return True
            else:
                print(f"❌ 添加失败: {data.get('message')}")
                return False
        except Exception as e:
            print(f"❌ 添加账号异常: {str(e)}")
            return False
    
    def test_get_accounts_status(self):
        """测试获取账号状态"""
        self.print_separator("账号状态监控")
        try:
            response = self.session.get(f"{self.base_url}/account/status")
            data = response.json()
            if data.get("success"):
                status_data = data.get("all_accounts_status", {})
                print(f"📊 找到 {len(status_data)} 个账号")
                
                for phone, status in status_data.items():
                    print(f"\n📱 账号: {phone}")
                    print(f"   状态: {status.get('status')}")
                    print(f"   浏览器: {status.get('browser_status')}")
                    print(f"   发布数: {status.get('publish_count', 0)}")
                    print(f"   评论数: {status.get('comment_count', 0)}")
                    print(f"   Cookie: {'存在' if status.get('cookie_exists') else '不存在'}")
                    
                    # 计算心跳时间差
                    heartbeat_diff = status.get('heartbeat_diff', 0)
                    if heartbeat_diff < 60:
                        heartbeat_status = f"{heartbeat_diff:.0f}秒前"
                    elif heartbeat_diff < 3600:
                        heartbeat_status = f"{heartbeat_diff/60:.0f}分钟前"
                    else:
                        heartbeat_status = f"{heartbeat_diff/3600:.1f}小时前"
                    print(f"   心跳: {heartbeat_status}")
                
                return True
            else:
                print(f"❌ 获取状态失败: {data.get('message')}")
                return False
        except Exception as e:
            print(f"❌ 获取状态异常: {str(e)}")
            return False
    
    def test_update_heartbeat(self, phone_number=None):
        """测试更新心跳"""
        target = phone_number or "所有账号"
        self.print_separator(f"更新心跳: {target}")
        try:
            url = f"{self.base_url}/account/heartbeat"
            if phone_number:
                url += f"?phone_number={phone_number}"
            
            response = self.session.post(url)
            data = response.json()
            if data.get("success"):
                print(f"✅ {data.get('message')}")
                if 'updated_accounts' in data:
                    print(f"📝 更新的账号: {', '.join(data['updated_accounts'])}")
                return True
            else:
                print(f"❌ 更新失败: {data.get('message')}")
                return False
        except Exception as e:
            print(f"❌ 更新心跳异常: {str(e)}")
            return False
    
    def test_get_history(self, phone_number=None, history_type="all", limit=10):
        """测试获取历史记录"""
        target = phone_number or "所有账号"
        self.print_separator(f"历史记录查询: {target} ({history_type})")
        try:
            params = {
                "history_type": history_type,
                "limit": limit
            }
            if phone_number:
                params["phone_number"] = phone_number
            
            response = self.session.get(
                f"{self.base_url}/account/history",
                params=params
            )
            data = response.json()
            if data.get("success"):
                if phone_number:
                    history = data.get("history", [])
                    print(f"📊 找到 {len(history)} 条记录")
                    for record in history[:5]:  # 只显示前5条
                        type_icon = "📝" if record.get("type") == "publish" else "💬"
                        status_icon = "✅" if record.get("success") else "❌"
                        content = record.get("title") or record.get("comment", "")
                        print(f"   {type_icon} {record.get('timestamp')} - {content[:30]}... {status_icon}")
                else:
                    all_history = data.get("all_accounts_history", {})
                    total_count = data.get("total_count", 0)
                    print(f"📊 总共找到 {total_count} 条记录，涉及 {len(all_history)} 个账号")
                    for phone, history in all_history.items():
                        if history:
                            print(f"   📱 {phone}: {len(history)} 条记录")
                
                return True
            else:
                print(f"❌ 获取历史失败: {data.get('message')}")
                return False
        except Exception as e:
            print(f"❌ 获取历史异常: {str(e)}")
            return False
    
    def test_simulate_operations(self, phone_number):
        """模拟操作以生成历史记录"""
        self.print_separator(f"模拟操作: {phone_number}")
        try:
            # 模拟发布操作（这里只是演示，实际不会真正发布）
            print("📝 模拟发布操作...")
            from xiaohongshu_tools import multi_account_manager
            
            account = multi_account_manager.get_account(phone_number)
            
            # 手动添加一些测试历史记录
            account.record_publish(
                "测试标题", 
                "这是一个测试内容，用于演示历史记录功能", 
                ["test_image.jpg"], 
                "模拟发布成功"
            )
            
            account.record_comment(
                "https://test.xiaohongshu.com/note/test123",
                "这是一条测试评论",
                "模拟评论成功"
            )
            
            print("✅ 模拟操作完成，已添加测试历史记录")
            return True
            
        except Exception as e:
            print(f"❌ 模拟操作失败: {str(e)}")
            return False
    
    def test_set_default_account(self, phone_number):
        """测试设置默认账号"""
        self.print_separator(f"设置默认账号: {phone_number}")
        try:
            response = self.session.post(
                f"{self.base_url}/account/set_default",
                params={"phone_number": phone_number}
            )
            data = response.json()
            if data.get("success"):
                print(f"✅ 账号 {phone_number} 设为默认账号成功")
                print(f"📝 当前默认账号: {data.get('current_account')}")
                return True
            else:
                print(f"❌ 设置默认账号失败: {data.get('message')}")
                return False
        except Exception as e:
            print(f"❌ 设置默认账号异常: {str(e)}")
            return False

    def test_remove_account(self, phone_number):
        """测试删除账号"""
        self.print_separator(f"删除账号: {phone_number}")
        try:
            response = self.session.delete(
                f"{self.base_url}/account/remove",
                params={"phone_number": phone_number}
            )
            data = response.json()
            if data.get("success"):
                print(f"✅ 账号 {phone_number} 删除成功")
                print(f"📝 消息: {data.get('message')}")
                return True
            else:
                print(f"❌ 删除失败: {data.get('message')}")
                return False
        except Exception as e:
            print(f"❌ 删除账号异常: {str(e)}")
            return False
    
    def run_full_test(self):
        """运行完整测试流程"""
        print("🌹 小红书账号管理功能测试")
        print(f"⏰ 开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 测试手机号
        test_phone_1 = "13800138001"
        test_phone_2 = "13800138002"
        
        success_count = 0
        total_tests = 0
        
        # 1. 服务器状态检查
        total_tests += 1
        if self.test_server_status():
            success_count += 1
        
        # 2. 添加测试账号
        total_tests += 1
        if self.test_add_account(test_phone_1):
            success_count += 1
        
        total_tests += 1
        if self.test_add_account(test_phone_2):
            success_count += 1
        
        # 3. 获取账号状态
        total_tests += 1
        if self.test_get_accounts_status():
            success_count += 1
        
        # 4. 模拟操作生成历史
        total_tests += 1
        if self.test_simulate_operations(test_phone_1):
            success_count += 1
        
        # 5. 更新心跳
        total_tests += 1
        if self.test_update_heartbeat(test_phone_1):
            success_count += 1
        
        # 6. 获取历史记录
        total_tests += 1
        if self.test_get_history(test_phone_1):
            success_count += 1
        
        total_tests += 1
        if self.test_get_history(history_type="publish"):
            success_count += 1
        
        # 7. 设置默认账号
        total_tests += 1
        if self.test_set_default_account(test_phone_2):
            success_count += 1
        
        # 8. 再次检查状态（验证默认账号设置）
        total_tests += 1
        if self.test_get_accounts_status():
            success_count += 1
        
        # 9. 清理测试账号
        total_tests += 1
        if self.test_remove_account(test_phone_1):
            success_count += 1
        
        total_tests += 1
        if self.test_remove_account(test_phone_2):
            success_count += 1
        
        # 测试结果总结
        self.print_separator("测试结果总结")
        print(f"📊 总测试数: {total_tests}")
        print(f"✅ 成功数: {success_count}")
        print(f"❌ 失败数: {total_tests - success_count}")
        print(f"📈 成功率: {success_count/total_tests*100:.1f}%")
        
        if success_count == total_tests:
            print("\n🎉 所有测试通过！账号管理功能正常！")
            print("\n💡 使用提示:")
            print("   1. 访问 http://localhost:8000/account/manage 查看网页界面")
            print("   2. 查看 ACCOUNT_MANAGEMENT_GUIDE.md 了解详细使用方法")
            print("   3. 使用 API 接口进行程序化管理")
        else:
            print("\n⚠️ 部分测试失败，请检查日志排查问题")
        
        return success_count == total_tests

def main():
    """主函数"""
    print("正在启动账号管理功能测试...")
    
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("使用方法:")
            print("  python test_account_management.py           # 运行完整测试")
            print("  python test_account_management.py --help    # 显示帮助")
            return
    
    tester = AccountManagementTester()
    
    try:
        success = tester.run_full_test()
        exit_code = 0 if success else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️ 测试被用户中断")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 测试过程发生异常: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 