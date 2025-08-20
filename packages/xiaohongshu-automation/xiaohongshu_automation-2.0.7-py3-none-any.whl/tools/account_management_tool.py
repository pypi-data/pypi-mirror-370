"""
账号管理工具
支持多账号的添加、删除、切换和状态查询
"""

import logging
from typing import Dict, Any, List
import mcp.types as types
from .base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

class AccountManagementTool(BaseTool):
    """账号管理工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_account_management",
            description="管理多个小红书账号，支持添加、删除、切换和查询账号状态"
        )
        self.adapter = adapter
    
    def get_schema(self) -> Dict[str, Any]:
        """返回工具的参数schema"""
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["add", "list", "set_current", "remove", "status"],
                    "description": "操作类型：add(添加账号)、list(列出账号)、set_current(设置当前账号)、remove(删除账号)、status(查看状态)"
                },
                "phone_number": {
                    "type": "string",
                    "description": "手机号码（add、set_current、remove操作时必填）",
                    "pattern": "^1[3-9]\\d{9}$"
                }
            },
            "required": ["action"],
            "additionalProperties": False
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行账号管理操作
        
        Args:
            arguments: 包含操作类型和参数的字典
            
        Returns:
            ToolResult: 操作结果
        """
        try:
            action = arguments.get("action")
            phone_number = arguments.get("phone_number")
            
            logger.info(f"执行账号管理操作: {action}")
            
            if action == "add":
                if not phone_number:
                    return ToolResult(
                        success=False,
                        error="添加账号需要提供手机号码",
                        data=None
                    )
                return await self._add_account(phone_number)
                
            elif action == "list":
                return await self._list_accounts()
                
            elif action == "set_current":
                if not phone_number:
                    return ToolResult(
                        success=False,
                        error="设置当前账号需要提供手机号码",
                        data=None
                    )
                return await self._set_current_account(phone_number)
                
            elif action == "remove":
                if not phone_number:
                    return ToolResult(
                        success=False,
                        error="删除账号需要提供手机号码",
                        data=None
                    )
                return await self._remove_account(phone_number)
                
            elif action == "status":
                return await self._get_account_status()
                
            else:
                return ToolResult(
                    success=False,
                    error=f"不支持的操作类型: {action}",
                    data=None
                )
                
        except Exception as e:
            logger.error(f"账号管理操作失败: {str(e)}")
            return ToolResult(
                success=False,
                error=f"账号管理操作失败: {str(e)}",
                data=None
            )
    
    async def _add_account(self, phone_number: str) -> ToolResult:
        """添加账号"""
        try:
            result = await self.adapter.add_account(phone_number)
            
            if result:
                return ToolResult(
                    success=True,
                    data={
                        "message": f"账号 {phone_number} 添加成功",
                        "phone_number": phone_number,
                        "status": "added"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"账号 {phone_number} 添加失败",
                    data=None
                )
                
        except Exception as e:
            logger.error(f"添加账号失败: {str(e)}")
            return ToolResult(
                success=False,
                error=f"添加账号失败: {str(e)}",
                data=None
            )
    
    async def _list_accounts(self) -> ToolResult:
        """列出所有账号"""
        try:
            accounts_data = await self.adapter.list_accounts()
            
            if accounts_data:
                return ToolResult(
                    success=True,
                    data=accounts_data
                )
            else:
                return ToolResult(
                    success=True,
                    data={
                        "账号列表": [],
                        "总账号数": 0,
                        "当前默认账号": "未设置"
                    }
                )
                
        except Exception as e:
            logger.error(f"获取账号列表失败: {str(e)}")
            return ToolResult(
                success=False,
                error=f"获取账号列表失败: {str(e)}",
                data=None
            )
    
    async def _set_current_account(self, phone_number: str) -> ToolResult:
        """设置当前账号"""
        try:
            result = await self.adapter.set_current_account(phone_number)
            
            if result:
                return ToolResult(
                    success=True,
                    data={
                        "message": f"当前账号已设置为 {phone_number}",
                        "current_account": phone_number,
                        "status": "set"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"设置当前账号失败，账号 {phone_number} 可能不存在",
                    data=None
                )
                
        except Exception as e:
            logger.error(f"设置当前账号失败: {str(e)}")
            return ToolResult(
                success=False,
                error=f"设置当前账号失败: {str(e)}",
                data=None
            )
    
    async def _remove_account(self, phone_number: str) -> ToolResult:
        """删除账号"""
        try:
            result = await self.adapter.remove_account(phone_number)
            
            if result:
                return ToolResult(
                    success=True,
                    data={
                        "message": f"账号 {phone_number} 已删除",
                        "phone_number": phone_number,
                        "status": "removed"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"删除账号失败，账号 {phone_number} 可能不存在",
                    data=None
                )
                
        except Exception as e:
            logger.error(f"删除账号失败: {str(e)}")
            return ToolResult(
                success=False,
                error=f"删除账号失败: {str(e)}",
                data=None
            )
    
    async def _get_account_status(self) -> ToolResult:
        """获取所有账号状态"""
        try:
            status_data = await self.adapter.get_account_status()
            
            if status_data:
                return ToolResult(
                    success=True,
                    data=status_data
                )
            else:
                return ToolResult(
                    success=True,
                    data={
                        "所有账号状态": {},
                        "在线账号数": 0,
                        "总账号数": 0
                    }
                )
                
        except Exception as e:
            logger.error(f"获取账号状态失败: {str(e)}")
            return ToolResult(
                success=False,
                error=f"获取账号状态失败: {str(e)}",
                data=None
            )
    
    def _format_success_result(self, result: ToolResult) -> str:
        """格式化成功结果为可读文本"""
        if not result.success or not result.data:
            return "❌ 操作失败"
        
        data = result.data
        
        # 根据不同的操作类型格式化输出
        if "message" in data:
            # 单个操作结果
            output = f"✅ {data['message']}\n\n"
            
            if "phone_number" in data:
                output += f"📱 手机号: {data['phone_number']}\n"
            
            if "current_account" in data:
                output += f"🎯 当前账号: {data['current_account']}\n"
            
            return output
        
        elif "账号列表" in data:
            # 账号列表
            output = "📋 账号列表\n\n"
            output += f"📊 总账号数: {data.get('总账号数', 0)}\n"
            output += f"🎯 当前默认账号: {data.get('当前默认账号', '未设置')}\n\n"
            
            accounts = data.get("账号列表", [])
            if accounts:
                output += "📱 账号详情:\n"
                for i, account in enumerate(accounts, 1):
                    output += f"   {i}. {account}\n"
            else:
                output += "暂无账号\n"
            
            return output
        
        elif "所有账号状态" in data:
            # 账号状态
            output = "📈 账号状态报告\n\n"
            output += f"📊 总账号数: {data.get('总账号数', 0)}\n"
            output += f"🌐 在线账号数: {data.get('在线账号数', 0)}\n\n"
            
            all_status = data.get("所有账号状态", {})
            if all_status:
                output += "📱 详细状态:\n"
                for phone, status in all_status.items():
                    status_emoji = "✅" if status.get("status") == "healthy" else "⚠️"
                    output += f"   {status_emoji} {phone}: {status.get('status', '未知')}\n"
                    
                    if status.get("last_active"):
                        output += f"      上次活跃: {status['last_active']}\n"
                    
                    if status.get("cookie_status"):
                        output += f"      Cookie状态: {status['cookie_status']}\n"
                    
                    output += "\n"
            else:
                output += "暂无账号状态信息\n"
            
            return output
        
        else:
            # 通用格式
            return f"✅ 操作成功\n\n�� 结果: {str(data)}" 