import json
import hashlib
import hmac
import base64
from datetime import datetime, timedelta
from pathlib import Path
import os
import platform
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LicenseManager:
    def __init__(self, license_file: str = None):
        """初始化许可证管理器
        
        Args:
            license_file: 许可证文件路径，如果为None则使用系统默认位置
        """
        if license_file is None:
            # 使用系统应用数据目录，避免软件更新时丢失
            self.license_file = self._get_license_file_path()
        else:
            self.license_file = Path(license_file)
        
        self.master_secret = "XHS_TOOLS_MASTER_SECRET_2024_SECURE_KEY"  # 用于验证真正的激活码
        
        # 确保许可证目录存在
        self.license_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.init_license_file()
    
    def _get_license_file_path(self) -> Path:
        """获取许可证文件的系统路径"""
        system = platform.system()
        app_name = "XiaohongshuTools"
        
        if system == "Windows":
            # Windows: %APPDATA%\XiaohongshuTools\license.json
            appdata = os.getenv('APPDATA', os.path.expanduser('~'))
            license_dir = Path(appdata) / app_name
        elif system == "Darwin":  # macOS
            # macOS: ~/Library/Application Support/XiaohongshuTools/license.json
            license_dir = Path.home() / "Library" / "Application Support" / app_name
        else:  # Linux and others
            # Linux: ~/.config/XiaohongshuTools/license.json
            config_dir = os.getenv('XDG_CONFIG_HOME', Path.home() / ".config")
            license_dir = Path(config_dir) / app_name
        
        license_file = license_dir / "license.json"
        return license_file
    
    def init_license_file(self):
        """初始化许可证文件"""
        if not self.license_file.exists():
            # 检查是否有旧的许可证文件需要迁移
            old_license_file = Path("license.json")
            if old_license_file.exists():
                logger.info("发现旧的许可证文件，正在迁移...")
                try:
                    # 迁移旧许可证文件
                    import shutil
                    shutil.copy2(old_license_file, self.license_file)
                    logger.info(f"许可证文件已迁移到: {self.license_file}")
                    
                    # 备份旧文件
                    backup_file = old_license_file.with_suffix('.backup')
                    shutil.move(old_license_file, backup_file)
                    logger.info(f"旧许可证文件已备份为: {backup_file}")
                    return
                except Exception as e:
                    logger.warning(f"迁移许可证文件失败: {e}")
            
            # 首次运行，创建试用期（7天）
            trial_expiry = datetime.now() + timedelta(days=7)
            license_data = {
                "expiry_date": trial_expiry.isoformat(),
                "license_type": "trial",
                "created_date": datetime.now().isoformat(),
                "activated_codes": [],
                "machine_id": self._get_machine_id(),
                "license_version": "2.0",  # 新版本标识
                "storage_location": str(self.license_file)
            }
            self._save_license(license_data)
            logger.info(f"初始化试用许可证，有效期至: {trial_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
            logger.info(f"许可证存储位置: {self.license_file}")
    
    def _get_machine_id(self) -> str:
        """获取机器唯一标识"""
        import platform
        machine_info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
        return hashlib.md5(machine_info.encode()).hexdigest()[:16]
    
    def _save_license(self, license_data: Dict[str, Any]):
        """保存许可证数据"""
        try:
            # 添加保存时间戳
            license_data["last_updated"] = datetime.now().isoformat()
            
            with open(self.license_file, 'w', encoding='utf-8') as f:
                json.dump(license_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存许可证文件失败: {e}")
            raise
    
    def _load_license(self) -> Optional[Dict[str, Any]]:
        """加载许可证数据"""
        try:
            if not self.license_file.exists():
                return None
            with open(self.license_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"读取许可证文件失败: {e}")
            return None
    
    def is_valid(self) -> bool:
        """检查许可证是否有效"""
        license_data = self._load_license()
        if not license_data:
            return False
        
        try:
            expiry_date = datetime.fromisoformat(license_data["expiry_date"])
            current_time = datetime.now()
            
            # 检查机器ID是否匹配
            stored_machine_id = license_data.get("machine_id", "")
            current_machine_id = self._get_machine_id()
            if stored_machine_id != current_machine_id:
                logger.warning("机器ID不匹配，许可证可能被非法复制")
                return False
            
            is_valid = current_time < expiry_date
            if not is_valid:
                logger.warning(f"许可证已过期: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return is_valid
        except Exception as e:
            logger.error(f"验证许可证时出错: {e}")
            return False
    
    def get_expiry_info(self) -> Dict[str, Any]:
        """获取有效期信息"""
        license_data = self._load_license()
        if not license_data:
            return {"valid": False, "message": "许可证文件不存在"}
        
        try:
            expiry_date = datetime.fromisoformat(license_data["expiry_date"])
            current_time = datetime.now()
            
            if current_time >= expiry_date:
                return {
                    "valid": False,
                    "expiry_date": expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
                    "license_type": license_data.get("license_type", "unknown"),
                    "message": "许可证已过期",
                    "storage_location": str(self.license_file)
                }
            
            remaining_time = expiry_date - current_time
            remaining_days = remaining_time.days
            
            return {
                "valid": True,
                "expiry_date": expiry_date.strftime('%Y-%m-%d %H:%M:%S'),
                "license_type": license_data.get("license_type", "unknown"),
                "remaining_days": remaining_days,
                "remaining_hours": remaining_time.seconds // 3600,
                "message": f"许可证有效，剩余 {remaining_days} 天",
                "storage_location": str(self.license_file),
                "license_version": license_data.get("license_version", "1.0")
            }
        except Exception as e:
            return {"valid": False, "message": f"读取许可证信息失败: {e}"}
    
    def _verify_master_activation_code(self, activation_code: str) -> Dict[str, Any]:
        """验证真正的激活码（由软件提供商生成）"""
        try:
            parts = activation_code.split('-')
            if len(parts) != 4:
                return {"success": False, "message": "激活码格式无效"}
            
            duration_type, machine_id_part, timestamp_str, signature = parts
            
            current_machine_id = self._get_machine_id()
            
            # 处理通用激活码
            if machine_id_part == "UNIVERSAL":
                code_data = f"{duration_type.lower()}|UNIVERSAL|{timestamp_str}|"
                expected_signature = hmac.new(
                    self.master_secret.encode(),
                    code_data.encode(),
                    hashlib.sha256
                ).hexdigest()[:20]
                
                if signature == expected_signature:
                    return {"success": True, "is_universal": True}
            
            # 处理机器专用激活码
            elif current_machine_id.startswith(machine_id_part):
                code_data = f"{duration_type.lower()}|{current_machine_id}|{timestamp_str}|"
                expected_signature = hmac.new(
                    self.master_secret.encode(),
                    code_data.encode(),
                    hashlib.sha256
                ).hexdigest()[:20]
                
                if signature == expected_signature:
                    return {"success": True, "is_universal": False}
            
            return {"success": False, "message": "激活码验证失败"}
            
        except Exception as e:
            return {"success": False, "message": f"激活码验证异常: {str(e)}"}
    
    def activate_with_code(self, activation_code: str) -> Dict[str, Any]:
        """使用激活码激活软件"""
        try:
            # 验证真正的激活码
            master_result = self._verify_master_activation_code(activation_code)
            if master_result["success"]:
                logger.info("使用正式激活码激活")
                return self._activate_with_master_code(activation_code, master_result["is_universal"])
            else:
                return {"success": False, "message": "激活码无效或已过期"}
            
        except Exception as e:
            logger.error(f"激活过程中出错: {e}")
            return {"success": False, "message": f"激活失败: {str(e)}"}
    
    def _activate_with_master_code(self, activation_code: str, is_universal: bool) -> Dict[str, Any]:
        """使用真正的激活码激活"""
        parts = activation_code.split('-')
        duration_type, machine_id_part, timestamp_str, signature = parts
        
        # 检查是否已使用过此激活码
        license_data = self._load_license()
        if license_data and activation_code in license_data.get("activated_codes", []):
            return {"success": False, "message": "此激活码已经使用过"}
        
        # 计算延长时间
        duration_map = {
            "WEEK": 7,
            "MONTH": 30,
            "QUARTER": 90,
            "YEAR": 365
        }
        extend_days = duration_map.get(duration_type.upper(), 0)
        if extend_days == 0:
            return {"success": False, "message": "激活码类型无效"}
        
        # 更新许可证
        if not license_data:
            license_data = {
                "created_date": datetime.now().isoformat(),
                "activated_codes": [],
                "machine_id": self._get_machine_id(),
                "license_version": "2.0"
            }
        
        # 计算新的过期时间
        current_expiry = datetime.fromisoformat(license_data.get("expiry_date", datetime.now().isoformat()))
        if current_expiry < datetime.now():
            new_expiry = datetime.now() + timedelta(days=extend_days)
        else:
            new_expiry = current_expiry + timedelta(days=extend_days)
        
        # 更新许可证数据
        license_data["expiry_date"] = new_expiry.isoformat()
        license_data["license_type"] = "activated"
        license_data["activated_codes"].append(activation_code)
        license_data["last_activation"] = datetime.now().isoformat()
        license_data["activation_source"] = "master" if not is_universal else "universal"
        
        self._save_license(license_data)
        
        logger.info(f"激活成功，新的过期时间: {new_expiry.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return {
            "success": True,
            "message": f"激活成功！许可证延长 {extend_days} 天",
            "new_expiry": new_expiry.strftime('%Y-%m-%d %H:%M:%S'),
            "extended_days": extend_days,
            "activation_type": "正式激活码"
        }
    
    def check_and_warn_expiry(self) -> Optional[str]:
        """检查并警告即将到期的许可证"""
        expiry_info = self.get_expiry_info()
        
        if not expiry_info["valid"]:
            return expiry_info["message"]
        
        remaining_days = expiry_info.get("remaining_days", 0)
        
        if remaining_days <= 3:
            return f"⚠️ 许可证将在 {remaining_days} 天后过期，请及时续期！"
        elif remaining_days <= 7:
            return f"📅 许可证将在 {remaining_days} 天后过期"
        
        return None
    
    def backup_license(self, backup_path: str = None) -> str:
        """备份许可证文件"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"license_backup_{timestamp}.json"
        
        try:
            import shutil
            shutil.copy2(self.license_file, backup_path)
            logger.info(f"许可证已备份到: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"备份许可证失败: {e}")
            raise
    
    def restore_license(self, backup_path: str) -> bool:
        """从备份恢复许可证"""
        try:
            import shutil
            backup_file = Path(backup_path)
            if not backup_file.exists():
                logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            shutil.copy2(backup_file, self.license_file)
            logger.info(f"许可证已从备份恢复: {backup_path}")
            return True
        except Exception as e:
            logger.error(f"恢复许可证失败: {e}")
            return False


if __name__ == "__main__":
    # 演示用法
    manager = LicenseManager()
    
    print("当前许可证状态:")
    expiry_info = manager.get_expiry_info()
    print(json.dumps(expiry_info, indent=2, ensure_ascii=False)) 