"""
获取小红书笔记内容工具
支持获取笔记的详细内容，包括标题、作者、发布时间和正文
"""

import logging
from typing import Dict, Any
from tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

class GetNoteContentTool(BaseTool):
    """获取小红书笔记内容工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_get_note_content",
            description="获取小红书笔记的详细内容，包括标题、作者、发布时间和正文内容"
        )
        self.adapter = adapter
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行获取笔记内容操作
        
        Args:
            arguments: 包含参数的字典
                - url: 小红书笔记URL (必需)
                - phone_number: 指定账号手机号 (可选)
        
        Returns:
            笔记内容结果
        """
        try:
            url = arguments["url"]
            phone_number = arguments.get("phone_number", None)  # 获取可选的phone_number参数
            
            # 参数验证
            if not url or not url.strip():
                return ToolResult(
                    success=False,
                    error="笔记URL不能为空"
                )
            
            # 验证URL格式
            if "xiaohongshu.com" not in url and "xhslink.com" not in url:
                return ToolResult(
                    success=False,
                    error="请提供有效的小红书笔记URL"
                )
            
            # 执行内容获取
            account_info = phone_number or "默认账号"
            self.logger.info(f"开始获取笔记内容: {url} (账号: {account_info})")
            
            result = await self.adapter.get_note_content(url.strip(), phone_number)
            
            if result.get("success"):
                note_data = result.get("data", {})
                
                if note_data:
                    # 格式化笔记内容
                    formatted_content = {
                        "笔记URL": note_data.get("url", url),
                        "标题": note_data.get("标题", "未知标题"),
                        "作者": note_data.get("作者", "未知作者"),
                        "发布时间": note_data.get("发布时间", "未知"),
                        "正文内容": note_data.get("内容", "未能获取内容"),
                        "内容长度": len(note_data.get("内容", "")) if note_data.get("内容") else 0,
                        "使用账号": account_info
                    }
                    
                    return ToolResult(
                        success=True,
                        data=formatted_content,
                        message=f"使用账号 {account_info} 成功获取笔记内容: {formatted_content['标题']}"
                    )
                else:
                    return ToolResult(
                        success=False,
                        error="获取到的笔记数据为空",
                        message=f"使用账号 {account_info} 请检查笔记URL是否正确或笔记是否可访问"
                    )
            else:
                error_message = result.get("message", "获取笔记内容失败，未知错误")
                return ToolResult(
                    success=False,
                    error=error_message,
                    message=f"使用账号 {account_info} 获取笔记内容时出现问题"
                )
        
        except Exception as e:
            account_info = arguments.get("phone_number", "默认账号")
            self.logger.error(f"获取笔记内容时出错 (账号: {account_info}): {str(e)}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"账号 {account_info} 的获取笔记内容操作执行失败"
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """
        获取工具的 JSON Schema
        
        Returns:
            工具参数的 JSON Schema
        """
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "小红书笔记URL，如：https://www.xiaohongshu.com/explore/...",
                    "minLength": 10,
                    "pattern": r".*(xiaohongshu\.com|xhslink\.com).*"
                },
                "phone_number": {
                    "type": "string",
                    "description": "指定获取内容账号的手机号（可选），如果不提供则使用当前默认账号",
                    "required": False
                }
            },
            "required": ["url"]
        }
    
    def _format_success_result(self, result: ToolResult) -> str:
        """格式化成功结果"""
        if not result.data:
            return f"✅ {self.name} 执行成功\n\n📝 {result.message}"
        
        data = result.data
        output = f"📄 笔记内容获取成功\n\n"
        output += f"🔗 URL: {data.get('笔记URL', 'N/A')}\n"
        output += f"📝 标题: {data.get('标题', 'N/A')}\n"
        output += f"👤 作者: {data.get('作者', 'N/A')}\n"
        output += f"📅 发布时间: {data.get('发布时间', 'N/A')}\n"
        output += f"📊 内容长度: {data.get('内容长度', 0)} 字符\n\n"
        
        content = data.get("正文内容", "")
        if content and content != "未能获取内容":
            # 显示内容摘要
            if len(content) > 200:
                output += f"📖 内容摘要:\n{content[:200]}...\n\n"
                output += f"💡 提示: 内容较长已截取前200字符显示\n"
            else:
                output += f"📖 完整内容:\n{content}\n"
        else:
            output += f"⚠️  未能获取到正文内容\n"
            output += f"💡 建议: 检查笔记是否为私密或需要登录访问\n"
        
        output += f"\n🕐 完成时间: {result.timestamp}"
        
        return output 