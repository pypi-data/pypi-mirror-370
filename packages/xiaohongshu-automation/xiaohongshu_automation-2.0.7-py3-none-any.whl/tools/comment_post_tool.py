"""
发布小红书评论工具
支持向指定笔记发布评论
"""

import logging
from typing import Dict, Any
from tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

class PostCommentTool(BaseTool):
    """发布小红书评论工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_post_comment",
            description="向指定的小红书笔记发布评论"
        )
        self.adapter = adapter
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行评论发布操作
        
        Args:
            arguments: 包含参数的字典
                - url: 小红书笔记URL (必需)
                - comment: 要发布的评论内容 (必需)
                - mentions: 可选的@提及用户名列表 (可选)
                - phone_number: 指定账号手机号 (可选)
        
        Returns:
            评论发布结果
        """
        try:
            url = arguments["url"]
            comment = arguments["comment"]
            mentions = arguments.get("mentions", None)  # 获取可选的mentions参数
            phone_number = arguments.get("phone_number", None)  # 获取可选的phone_number参数
            
            # 参数验证
            if not url or not url.strip():
                return ToolResult(
                    success=False,
                    error="笔记URL不能为空"
                )
            
            if not comment or not comment.strip():
                return ToolResult(
                    success=False,
                    error="评论内容不能为空"
                )
            
            # 验证URL格式
            if "xiaohongshu.com" not in url and "xhslink.com" not in url:
                return ToolResult(
                    success=False,
                    error="请提供有效的小红书笔记URL"
                )
            
            # 验证评论长度
            comment = comment.strip()
            if len(comment) > 500:
                return ToolResult(
                    success=False,
                    error="评论内容不能超过500字符"
                )
            
            if len(comment) < 2:
                return ToolResult(
                    success=False,
                    error="评论内容至少需要2个字符"
                )
            
            # 执行评论发布
            account_info = phone_number or "默认账号"
            self.logger.info(f"开始发布评论: {url} (账号: {account_info})")
            self.logger.info(f"评论内容: {comment}")
            if mentions:
                self.logger.info(f"@ 提及用户: {mentions}")
            
            result = await self.adapter.post_comment(url.strip(), comment, mentions, phone_number)
            
            if result.get("success"):
                # 格式化成功结果
                formatted_result = {
                    "笔记URL": url,
                    "评论内容": comment,
                    "使用账号": account_info,
                    "@ 提及用户": mentions or "无",
                    "发布时间": result.get("data", {}).get("timestamp", "未知"),
                    "发布状态": "成功"
                }
                
                return ToolResult(
                    success=True,
                    data=formatted_result,
                    message=f"使用账号 {account_info} 成功发布评论到笔记"
                )
            else:
                error_message = result.get("message", "发布评论失败，未知错误")
                return ToolResult(
                    success=False,
                    error=error_message,
                    message=f"使用账号 {account_info} 发布评论时出现问题"
                )
        
        except Exception as e:
            account_info = arguments.get("phone_number", "默认账号")
            self.logger.error(f"发布评论时出错 (账号: {account_info}): {str(e)}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"账号 {account_info} 的发布评论操作执行失败"
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
                "comment": {
                    "type": "string",
                    "description": "要发布的评论内容，建议简短自然，不超过500字符",
                    "minLength": 2,
                    "maxLength": 500
                },
                "mentions": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "可选的@提及用户名列表，例如: ['用户1', '用户2']",
                    "required": False
                },
                "phone_number": {
                    "type": "string",
                    "description": "指定发布评论账号的手机号（可选），如果不提供则使用当前默认账号",
                    "required": False
                }
            },
            "required": ["url", "comment"]
        }
    
    def _format_success_result(self, result: ToolResult) -> str:
        """格式化成功结果"""
        if not result.data:
            return f"✅ {self.name} 执行成功\n\n📝 {result.message}"
        
        data = result.data
        output = f"📤 评论发布成功\n\n"
        
        output += f"🔗 **笔记URL**: {data.get('笔记URL', 'N/A')}\n"
        output += f"💬 **评论内容**: {data.get('评论内容', 'N/A')}\n"
        output += f"⏰ **发布时间**: {data.get('发布时间', 'N/A')}\n"
        output += f"✅ **发布状态**: {data.get('发布状态', 'N/A')}\n\n"
        
        output += f"🎉 评论已成功发布到小红书笔记！\n"
        output += f"📱 您可以前往笔记页面查看评论是否显示\n\n"
        
        output += f"🕐 完成时间: {result.timestamp}"
        
        return output 