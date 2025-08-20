#!/usr/bin/env python3
"""
许可证管理命令行工具
用于查看许可证状态、激活软件等操作
"""

import argparse
import json
import sys
from license_manager import LicenseManager
from datetime import datetime

def print_banner():
    """打印程序横幅"""
    print("\n" + "="*60)
    print("🔑 小红书自动化工具 - 许可证管理器")
    print("="*60)

def print_license_status(manager: LicenseManager):
    """打印许可证状态"""
    expiry_info = manager.get_expiry_info()
    
    print("\n📋 许可证状态:")
    print("-" * 40)
    
    if expiry_info["valid"]:
        print(f"✅ 状态: 有效")
        print(f"📅 有效期至: {expiry_info['expiry_date']}")
        print(f"⏰ 剩余时间: {expiry_info['remaining_days']} 天 {expiry_info.get('remaining_hours', 0)} 小时")
        print(f"🏷️ 许可证类型: {expiry_info['license_type']}")
        
        # 检查即将过期提醒
        warning = manager.check_and_warn_expiry()
        if warning:
            print(f"\n⚠️ {warning}")
    else:
        print(f"❌ 状态: {expiry_info['message']}")
        if 'expiry_date' in expiry_info:
            print(f"📅 过期时间: {expiry_info['expiry_date']}")
    
    print(f"🖥️ 机器ID: {manager._get_machine_id()}")
    print(f"📁 存储位置: {expiry_info.get('storage_location', 'N/A')}")
    print("-" * 40)

def activate_license(manager: LicenseManager, activation_code: str):
    """激活许可证"""
    print(f"\n🔑 正在激活许可证...")
    print(f"激活码: {activation_code}")
    
    result = manager.activate_with_code(activation_code)
    
    if result["success"]:
        print(f"\n✅ 激活成功!")
        print(f"📝 {result['message']}")
        print(f"📅 新的有效期: {result['new_expiry']}")
        print(f"⏰ 延长天数: {result['extended_days']} 天")
        print(f"🎫 激活类型: {result.get('activation_type', '正式激活码')}")
    else:
        print(f"\n❌ 激活失败!")
        print(f"📝 {result['message']}")
    
    return result["success"]

def main():
    parser = argparse.ArgumentParser(
        description="小红书自动化工具许可证管理器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python license_cli.py --status          查看许可证状态
  python license_cli.py --activate CODE   使用激活码激活
  python license_cli.py --info           显示详细信息
  python license_cli.py --backup         备份许可证
        """
    )
    
    parser.add_argument("--status", "-s", action="store_true", 
                       help="显示许可证状态")
    parser.add_argument("--activate", "-a", type=str, 
                       help="使用激活码激活许可证")
    parser.add_argument("--info", "-i", action="store_true",
                       help="显示详细的许可证信息")
    parser.add_argument("--json", "-j", action="store_true",
                       help="以JSON格式输出（配合其他选项使用）")
    parser.add_argument("--backup", "-b", type=str, nargs='?', const='auto',
                       help="备份许可证文件")
    parser.add_argument("--restore", "-r", type=str,
                       help="从备份恢复许可证")
    
    args = parser.parse_args()
    
    # 如果没有提供任何参数，显示状态
    if not any(vars(args).values()):
        args.status = True
    
    try:
        manager = LicenseManager()
        
        if not args.json:
            print_banner()
        
        if args.status or args.info:
            if args.json:
                expiry_info = manager.get_expiry_info()
                warning = manager.check_and_warn_expiry()
                result = {
                    "license_info": expiry_info,
                    "warning": warning,
                    "machine_id": manager._get_machine_id()
                }
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                print_license_status(manager)
                
                if args.info:
                    # 显示更详细的信息
                    license_data = manager._load_license()
                    if license_data:
                        print("\n📄 详细信息:")
                        print("-" * 40)
                        print(f"创建时间: {license_data.get('created_date', 'N/A')}")
                        print(f"最后激活: {license_data.get('last_activation', 'N/A')}")
                        print(f"已使用激活码数量: {len(license_data.get('activated_codes', []))}")
                        print(f"许可证版本: {license_data.get('license_version', '1.0')}")
                        print(f"激活来源: {license_data.get('activation_source', 'N/A')}")
                        print("-" * 40)
        
        elif args.activate:
            if args.json:
                result = manager.activate_with_code(args.activate)
                print(json.dumps(result, indent=2, ensure_ascii=False))
            else:
                success = activate_license(manager, args.activate)
                if success:
                    print("\n📋 激活后状态:")
                    print_license_status(manager)
                sys.exit(0 if success else 1)
        
        elif args.backup:
            backup_path = None if args.backup == 'auto' else args.backup
            backup_file = manager.backup_license(backup_path)
            if args.json:
                print(json.dumps({"success": True, "backup_file": backup_file}, ensure_ascii=False))
            else:
                print(f"✅ 许可证已备份到: {backup_file}")
        
        elif args.restore:
            success = manager.restore_license(args.restore)
            if args.json:
                print(json.dumps({"success": success}, ensure_ascii=False))
            else:
                if success:
                    print(f"✅ 许可证已从备份恢复: {args.restore}")
                else:
                    print(f"❌ 恢复许可证失败")
            sys.exit(0 if success else 1)
    
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作")
        sys.exit(1)
    except Exception as e:
        error_msg = f"❌ 发生错误: {str(e)}"
        if args.json:
            print(json.dumps({"error": error_msg}, ensure_ascii=False))
        else:
            print(f"\n{error_msg}")
        sys.exit(1)

if __name__ == "__main__":
    main() 