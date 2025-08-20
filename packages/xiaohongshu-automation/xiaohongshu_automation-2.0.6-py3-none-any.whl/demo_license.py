#!/usr/bin/env python3
"""
许可证系统演示脚本
展示许可证管理系统的功能和用法
"""

import json
import time
from license_manager import LicenseManager
from datetime import datetime

def print_section(title):
    """打印章节标题"""
    print("\n" + "="*60)
    print(f"🔍 {title}")
    print("="*60)

def print_license_info(manager):
    """打印许可证信息"""
    expiry_info = manager.get_expiry_info()
    print("\n📋 许可证状态:")
    print("-" * 40)
    
    if expiry_info["valid"]:
        print(f"✅ 状态: 有效")
        print(f"📅 有效期至: {expiry_info['expiry_date']}")
        print(f"⏰ 剩余时间: {expiry_info['remaining_days']} 天")
        print(f"🏷️ 许可证类型: {expiry_info['license_type']}")
    else:
        print(f"❌ 状态: {expiry_info['message']}")
        if 'expiry_date' in expiry_info:
            print(f"📅 过期时间: {expiry_info['expiry_date']}")
    
    print(f"🖥️ 机器ID: {manager._get_machine_id()}")
    print(f"📁 存储位置: {expiry_info.get('storage_location', 'N/A')}")
    
    # 检查即将过期提醒
    warning = manager.check_and_warn_expiry()
    if warning:
        print(f"\n⚠️ {warning}")
    
    print("-" * 40)

def demo_license_system():
    """演示许可证系统功能"""
    
    print("🎬 许可证管理系统演示")
    print("版本: 2.0.0 (无演示激活码版本)")
    
    # 1. 初始化许可证管理器
    print_section("初始化许可证管理器")
    manager = LicenseManager()
    print(f"✅ 许可证管理器初始化完成")
    print(f"📁 许可证文件位置: {manager.license_file}")
    
    # 2. 查看当前许可证状态
    print_section("查看当前许可证状态")
    print_license_info(manager)
    
    # 3. 显示机器信息
    print_section("机器信息")
    machine_id = manager._get_machine_id()
    print(f"🖥️ 机器ID: {machine_id}")
    print("📝 说明: 请将此机器ID提供给软件提供商以获取专用激活码")
    
    # 4. 测试激活码格式验证
    print_section("激活码格式测试")
    
    # 测试无效格式
    invalid_codes = [
        "INVALID-FORMAT",
        "MONTH-12345678-123456789",  # 缺少签名
        "WRONG-12345678-1234567890-abcdef123456789012",  # 错误类型
        ""
    ]
    
    for code in invalid_codes:
        print(f"\n🧪 测试无效激活码: {code}")
        result = manager.activate_with_code(code)
        if result["success"]:
            print(f"   ✅ {result['message']}")
        else:
            print(f"   ❌ {result['message']}")
    
    # 5. 演示真实激活码激活（如果用户提供）
    print_section("真实激活码测试")
    print("💡 可以输入真实的激活码进行测试（直接回车跳过）:")
    print("   格式示例: MONTH-UNIVERSAL-1749061547-a63d68d0f99d1a327045")
    
    user_input = input("请输入激活码 (直接回车跳过): ").strip()
    
    if user_input:
        print(f"\n🔑 测试激活码: {user_input}")
        result = manager.activate_with_code(user_input)
        
        if result["success"]:
            print(f"✅ 激活成功!")
            print(f"📝 {result['message']}")
            print(f"📅 新的有效期: {result['new_expiry']}")
            print(f"⏰ 延长天数: {result['extended_days']} 天")
            print(f"🎫 激活类型: {result.get('activation_type', '正式激活码')}")
            
            # 显示激活后的状态
            print("\n📋 激活后状态:")
            print_license_info(manager)
        else:
            print(f"❌ 激活失败: {result['message']}")
    else:
        print("⏩ 跳过激活码测试")
    
    # 6. 备份和恢复功能演示
    print_section("备份和恢复功能")
    
    try:
        # 备份许可证
        backup_file = manager.backup_license()
        print(f"✅ 许可证已备份到: {backup_file}")
        
        # 测试恢复功能（实际上不会改变现有数据，因为我们恢复的是同样的数据）
        print(f"🔄 测试从备份恢复功能...")
        restore_success = manager.restore_license(backup_file)
        if restore_success:
            print(f"✅ 许可证恢复成功")
        else:
            print(f"❌ 许可证恢复失败")
        
        # 清理临时备份文件
        import os
        os.remove(backup_file)
        print(f"🗑️ 临时备份文件已清理")
        
    except Exception as e:
        print(f"❌ 备份/恢复测试失败: {e}")
    
    # 7. 系统集成建议
    print_section("系统集成建议")
    print("🔧 集成建议:")
    print("   1. 在应用启动时调用 manager.is_valid() 检查许可证")
    print("   2. 使用中间件在每个API请求前验证许可证")
    print("   3. 提供网页激活界面: /activate")
    print("   4. 提供API激活接口: POST /license/activate")
    print("   5. 定期调用 manager.check_and_warn_expiry() 提醒用户")
    print("   6. 在关键功能前再次验证许可证状态")
    
    # 8. 许可证详细信息
    print_section("许可证详细信息")
    license_data = manager._load_license()
    if license_data:
        print("📄 许可证详情:")
        print(f"   创建时间: {license_data.get('created_date', 'N/A')}")
        print(f"   最后激活: {license_data.get('last_activation', 'N/A')}")
        print(f"   已使用激活码数量: {len(license_data.get('activated_codes', []))}")
        print(f"   许可证版本: {license_data.get('license_version', '1.0')}")
        print(f"   激活来源: {license_data.get('activation_source', 'N/A')}")
        print(f"   存储位置: {license_data.get('storage_location', manager.license_file)}")
    
    print_section("演示完成")
    print("✅ 许可证系统演示完成!")
    print("📖 更多信息请查看文档:")
    print("   - LICENSE_USAGE.md: 用户使用指南")
    print("   - ACTIVATION_CODE_GUIDE.md: 软件提供商指南")
    print("🌐 网页界面:")
    print("   - 许可证激活: http://localhost:8000/activate")
    print("   - API 文档: http://localhost:8000/docs")
    print("="*60)

if __name__ == "__main__":
    try:
        demo_license_system()
    except KeyboardInterrupt:
        print("\n\n👋 演示被用户中断")
    except Exception as e:
        print(f"\n❌ 演示过程中发生错误: {e}")
        import traceback
        traceback.print_exc() 