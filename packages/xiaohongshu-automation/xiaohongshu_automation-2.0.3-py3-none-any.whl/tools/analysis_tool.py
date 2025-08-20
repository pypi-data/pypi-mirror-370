"""
分析小红书笔记工具
支持分析笔记内容，提取关键信息和领域标签
"""

import logging
from typing import Dict, Any
from tools.base_tool import BaseTool, ToolResult

logger = logging.getLogger(__name__)

class AnalyzeNoteTool(BaseTool):
    """分析小红书笔记工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_analyze_note",
            description="分析小红书笔记内容，提取关键信息、领域标签和内容质量评估"
        )
        self.adapter = adapter
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行笔记分析操作
        
        Args:
            arguments: 包含参数的字典
                - url: 小红书笔记URL (必需)
        
        Returns:
            笔记分析结果
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
            
            # 执行笔记分析
            account_info = phone_number or "默认账号"
            self.logger.info(f"开始分析笔记: {url} (账号: {account_info})")
            
            result = await self.adapter.analyze_note(url.strip(), phone_number)
            
            if result.get("success"):
                analysis_data = result.get("data", {})
                
                if analysis_data:
                    # 格式化分析结果
                    formatted_analysis = {
                        "笔记URL": analysis_data.get("url", url),
                        "基础信息": analysis_data.get("基础信息", {}),
                        "内容摘要": analysis_data.get("内容", "")[:200] + "..." if len(analysis_data.get("内容", "")) > 200 else analysis_data.get("内容", ""),
                        "领域分析": analysis_data.get("领域分析", {}),
                        "关键词": analysis_data.get("关键词", []),
                        "分析指标": analysis_data.get("分析指标", {}),
                        "分析总结": self._generate_summary(analysis_data),
                        "使用账号": account_info
                    }
                    
                    return ToolResult(
                        success=True,
                        data=formatted_analysis,
                        message=f"使用账号 {account_info} 成功分析笔记内容: {analysis_data.get('基础信息', {}).get('标题', '未知标题')}"
                    )
                else:
                    return ToolResult(
                        success=False,
                        error="获取到的分析数据为空",
                        message=f"使用账号 {account_info} 请检查笔记URL是否正确或笔记是否可访问"
                    )
            else:
                error_message = result.get("message", "分析笔记失败，未知错误")
                return ToolResult(
                    success=False,
                    error=error_message,
                    message=f"使用账号 {account_info} 分析笔记时出现问题"
                )
        
        except Exception as e:
            account_info = arguments.get("phone_number", "默认账号")
            self.logger.error(f"分析笔记时出错 (账号: {account_info}): {str(e)}")
            return ToolResult(
                success=False,
                error=str(e),
                message=f"账号 {account_info} 的分析笔记操作执行失败"
            )
    
    def _generate_summary(self, analysis_data: Dict[str, Any]) -> str:
        """生成分析总结"""
        try:
            basic_info = analysis_data.get("基础信息", {})
            domain_analysis = analysis_data.get("领域分析", {})
            metrics = analysis_data.get("分析指标", {})
            
            summary_parts = []
            
            # 基础信息总结
            title = basic_info.get("标题", "未知标题")
            author = basic_info.get("作者", "未知作者")
            content_length = basic_info.get("内容长度", 0)
            
            summary_parts.append(f"这是一篇由 {author} 创作的笔记，标题为「{title}」")
            
            # 领域分析总结
            main_domains = domain_analysis.get("主要领域", [])
            if main_domains:
                summary_parts.append(f"主要涉及 {', '.join(main_domains)} 领域")
            
            # 内容质量总结
            content_quality = metrics.get("内容质量", "中")
            info_richness = metrics.get("信息丰富度", "中")
            domain_clarity = metrics.get("领域明确度", "中")
            
            summary_parts.append(f"内容质量{content_quality}，信息丰富度{info_richness}，领域明确度{domain_clarity}")
            
            # 字数统计
            if content_length > 0:
                summary_parts.append(f"全文约 {content_length} 字符")
            
            return "，".join(summary_parts) + "。"
            
        except Exception as e:
            logger.warning(f"生成分析总结时出错: {str(e)}")
            return "分析完成，详细信息请查看上方数据。"
    
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
                    "description": "指定分析账号的手机号（可选），如果不提供则使用当前默认账号",
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
        output = f"🔍 笔记分析完成\n\n"
        
        # 基础信息
        basic_info = data.get("基础信息", {})
        output += f"📄 **基础信息**\n"
        output += f"  🔗 URL: {data.get('笔记URL', 'N/A')}\n"
        output += f"  📝 标题: {basic_info.get('标题', 'N/A')}\n"
        output += f"  👤 作者: {basic_info.get('作者', 'N/A')}\n"
        output += f"  📅 发布时间: {basic_info.get('发布时间', 'N/A')}\n"
        output += f"  📊 内容长度: {basic_info.get('内容长度', 0)} 字符\n"
        output += f"  🔤 词汇数量: {basic_info.get('词汇数量', 0)} 个\n\n"
        
        # 领域分析
        domain_analysis = data.get("领域分析", {})
        main_domains = domain_analysis.get("主要领域", [])
        if main_domains:
            output += f"🎯 **领域分析**\n"
            output += f"  🏷️ 主要领域: {', '.join(main_domains)}\n"
            
            # 详细领域分析
            domain_details = domain_analysis.get("领域详情", {})
            if domain_details:
                output += f"  📈 领域详情:\n"
                for domain, details in list(domain_details.items())[:3]:  # 只显示前3个
                    score = details.get("score", 0)
                    keywords = details.get("keywords", [])
                    output += f"    • {domain}: 得分 {score} (关键词: {', '.join(keywords[:3])})\n"
            output += "\n"
        
        # 分析指标
        metrics = data.get("分析指标", {})
        if metrics:
            output += f"📊 **质量评估**\n"
            output += f"  🌟 内容质量: {metrics.get('内容质量', 'N/A')}\n"
            output += f"  💡 信息丰富度: {metrics.get('信息丰富度', 'N/A')}\n"
            output += f"  🎯 领域明确度: {metrics.get('领域明确度', 'N/A')}\n\n"
        
        # 关键词
        keywords = data.get("关键词", [])
        if keywords:
            output += f"🔑 **关键词** (前10个)\n"
            output += f"  {', '.join(keywords[:10])}\n\n"
        
        # 内容摘要
        content_summary = data.get("内容摘要", "")
        if content_summary and content_summary != "未能获取内容":
            output += f"📖 **内容摘要**\n"
            output += f"  {content_summary}\n\n"
        
        # 分析总结
        summary = data.get("分析总结", "")
        if summary:
            output += f"📋 **分析总结**\n"
            output += f"  {summary}\n\n"
        
        output += f"🕐 完成时间: {result.timestamp}"
        
        return output 