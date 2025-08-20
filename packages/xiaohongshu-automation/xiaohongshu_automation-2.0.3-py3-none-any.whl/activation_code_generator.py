#!/usr/bin/env python3
"""
激活码生成工具 - 仅供软件提供商使用
用于生成真正的激活码，包含更强的安全验证
"""

import hashlib
import hmac
import argparse
import json
import os
from datetime import datetime
import getpass
import sys

class ActivationCodeGenerator:
    def __init__(self):
        # 更强的密钥，实际使用时应该从安全的地方获取
        self.master_secret = "XHS_TOOLS_MASTER_SECRET_2024_SECURE_KEY"
        self.vendor_key = "VENDOR_AUTHORIZATION_KEY_2024"
        
    def authenticate_vendor(self):
        """验证软件提供商身份"""
        print("🔐 软件提供商身份验证")
        print("-" * 40)
        
        # 简单的密码验证（实际应用中应该使用更强的身份验证）
        vendor_password = getpass.getpass("请输入软件提供商密码: ")
        expected_hash = hashlib.sha256(f"{vendor_password}{self.vendor_key}".encode()).hexdigest()
        
        # 预设的正确密码哈希（实际应用中应该存储在安全的地方）
        correct_hash = hashlib.sha256(f"vendor123{self.vendor_key}".encode()).hexdigest()
        
        if expected_hash != correct_hash:
            print("❌ 身份验证失败！")
            return False
        
        print("✅ 身份验证成功！")
        return True
    
    def generate_activation_code(self, duration_type: str, target_machine_id: str = None, 
                               customer_info: str = "", notes: str = "") -> dict:
        """生成真正的激活码
        
        Args:
            duration_type: 'week', 'month', 'year'
            target_machine_id: 目标机器ID，如果为None则生成通用激活码
            customer_info: 客户信息
            notes: 备注信息
        """
        timestamp = int(datetime.now().timestamp())
        
        # 如果没有指定机器ID，生成一个特殊标记
        if target_machine_id is None:
            target_machine_id = "UNIVERSAL"
        
        # 创建激活码数据（不包含客户信息在签名中）
        if target_machine_id == "UNIVERSAL":
            code_data = f"{duration_type}|UNIVERSAL|{timestamp}|"
        else:
            code_data = f"{duration_type}|{target_machine_id}|{timestamp}|"
        
        # 使用更强的签名方法
        signature = hmac.new(
            self.master_secret.encode(),
            code_data.encode(),
            hashlib.sha256
        ).hexdigest()[:20]  # 使用20位签名增强安全性
        
        # 生成激活码
        if target_machine_id == "UNIVERSAL":
            activation_code = f"{duration_type.upper()}-UNIVERSAL-{timestamp}-{signature}"
        else:
            activation_code = f"{duration_type.upper()}-{target_machine_id[:8]}-{timestamp}-{signature}"
        
        # 记录生成信息
        generation_record = {
            "activation_code": activation_code,
            "duration_type": duration_type,
            "target_machine_id": target_machine_id,
            "customer_info": customer_info,
            "notes": notes,
            "generated_at": datetime.now().isoformat(),
            "generated_by": "vendor_tool",
            "valid_days": self._get_duration_days(duration_type)
        }
        
        return generation_record
    
    def _get_duration_days(self, duration_type: str) -> int:
        """获取持续时间天数"""
        duration_map = {
            "week": 7,
            "month": 30,
            "quarter": 90,  # 季度
            "year": 365
        }
        return duration_map.get(duration_type.lower(), 0)
    
    def batch_generate_codes(self, batch_config: dict) -> list:
        """批量生成激活码"""
        results = []
        
        for config in batch_config.get("codes", []):
            result = self.generate_activation_code(
                duration_type=config.get("duration", "month"),
                target_machine_id=config.get("machine_id"),
                customer_info=config.get("customer", ""),
                notes=config.get("notes", "")
            )
            results.append(result)
        
        return results
    
    def save_generation_record(self, records: list, filename: str = None):
        """保存生成记录"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"activation_codes_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump({
                    "generated_at": datetime.now().isoformat(),
                    "total_codes": len(records),
                    "codes": records
                }, f, indent=2, ensure_ascii=False)
            
            print(f"✅ 激活码记录已保存到: {filename}")
            return filename
        except Exception as e:
            print(f"❌ 保存记录失败: {e}")
            return None
    
    def verify_activation_code(self, activation_code: str) -> dict:
        """验证激活码的有效性（不激活，仅验证）"""
        try:
            parts = activation_code.split('-')
            if len(parts) != 4:
                return {"valid": False, "message": "激活码格式无效"}
            
            duration_type, machine_part, timestamp_str, signature = parts
            
            # 重构数据进行验证
            if machine_part == "UNIVERSAL":
                code_data = f"{duration_type.lower()}|UNIVERSAL|{timestamp_str}|"
            else:
                # 对于特定机器的激活码，需要完整的机器ID才能验证
                return {"valid": True, "message": "需要在目标机器上验证", "type": "machine_specific"}
            
            expected_signature = hmac.new(
                self.master_secret.encode(),
                code_data.encode(),
                hashlib.sha256
            ).hexdigest()[:20]
            
            if signature != expected_signature:
                return {"valid": False, "message": "激活码签名验证失败"}
            
            # 解析时间戳
            generated_time = datetime.fromtimestamp(int(timestamp_str))
            duration_days = self._get_duration_days(duration_type)
            
            return {
                "valid": True,
                "duration_type": duration_type,
                "duration_days": duration_days,
                "generated_time": generated_time.strftime("%Y-%m-%d %H:%M:%S"),
                "machine_type": "通用激活码" if machine_part == "UNIVERSAL" else "机器专用",
                "message": "激活码验证成功"
            }
            
        except Exception as e:
            return {"valid": False, "message": f"验证失败: {str(e)}"}

def main():
    parser = argparse.ArgumentParser(
        description="激活码生成工具 - 仅供软件提供商使用",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python activation_code_generator.py --generate month --customer "张三公司"
  python activation_code_generator.py --generate year --machine cf7e1584 --customer "VIP用户"
  python activation_code_generator.py --batch batch_config.json
  python activation_code_generator.py --verify MONTH-12345678-1234567890-abcdef123456
        """
    )
    
    parser.add_argument("--generate", "-g", type=str, 
                       choices=["week", "month", "quarter", "year"],
                       help="生成指定类型的激活码")
    parser.add_argument("--machine", "-m", type=str,
                       help="目标机器ID（留空生成通用激活码）")
    parser.add_argument("--customer", "-c", type=str, default="",
                       help="客户信息")
    parser.add_argument("--notes", "-n", type=str, default="",
                       help="备注信息")
    parser.add_argument("--batch", "-b", type=str,
                       help="批量生成，指定配置文件路径")
    parser.add_argument("--verify", "-v", type=str,
                       help="验证激活码有效性")
    parser.add_argument("--output", "-o", type=str,
                       help="输出文件名")
    
    args = parser.parse_args()
    
    if not any(vars(args).values()):
        parser.print_help()
        return
    
    generator = ActivationCodeGenerator()
    
    # 验证软件提供商身份
    if not generator.authenticate_vendor():
        sys.exit(1)
    
    try:
        if args.verify:
            # 验证激活码
            print(f"\n🔍 验证激活码: {args.verify}")
            result = generator.verify_activation_code(args.verify)
            print(json.dumps(result, indent=2, ensure_ascii=False))
            
        elif args.batch:
            # 批量生成
            print(f"\n📦 批量生成激活码...")
            with open(args.batch, 'r', encoding='utf-8') as f:
                batch_config = json.load(f)
            
            results = generator.batch_generate_codes(batch_config)
            print(f"✅ 成功生成 {len(results)} 个激活码")
            
            # 保存记录
            filename = generator.save_generation_record(results, args.output)
            
            # 显示生成的激活码
            for record in results:
                print(f"\n🎫 {record['duration_type'].upper()}激活码:")
                print(f"   代码: {record['activation_code']}")
                print(f"   客户: {record['customer_info']}")
                print(f"   有效期: {record['valid_days']} 天")
                
        elif args.generate:
            # 单个生成
            print(f"\n🎫 生成 {args.generate.upper()} 激活码...")
            
            result = generator.generate_activation_code(
                duration_type=args.generate,
                target_machine_id=args.machine,
                customer_info=args.customer,
                notes=args.notes
            )
            
            print(f"✅ 激活码生成成功!")
            print(f"🔑 激活码: {result['activation_code']}")
            print(f"📋 类型: {result['duration_type']} ({result['valid_days']} 天)")
            print(f"🖥️ 目标机器: {result['target_machine_id']}")
            print(f"👤 客户信息: {result['customer_info']}")
            print(f"📝 备注: {result['notes']}")
            print(f"⏰ 生成时间: {result['generated_at']}")
            
            # 保存记录
            generator.save_generation_record([result], args.output)
    
    except Exception as e:
        print(f"❌ 操作失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 