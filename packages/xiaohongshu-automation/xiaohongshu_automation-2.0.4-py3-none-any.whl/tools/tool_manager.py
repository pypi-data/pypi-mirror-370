"""
工具管理器
统一管理所有 MCP 工具的注册和调用
"""

import logging
from typing import Dict, List, Any
import mcp.types as types
from tools.base_tool import BaseTool
from tools.publish_tool import PublishTool
from tools.comments_tool import GetCommentsTool, ReplyCommentsTool
from tools.monitor_tool import MonitorTool
from tools.timeout_diagnostic_tool import TimeoutDiagnosticTool
from tools.search_tool import SearchNotesTool
from tools.content_tool import GetNoteContentTool
from tools.analysis_tool import AnalyzeNoteTool
from tools.comment_post_tool import PostCommentTool
from tools.account_management_tool import AccountManagementTool

logger = logging.getLogger(__name__)

class ToolManager:
    """MCP 工具管理器"""
    
    def __init__(self, adapter):
        self.adapter = adapter
        self.tools: Dict[str, BaseTool] = {}
        self._register_tools()
    
    def _register_tools(self):
        """注册所有工具"""
        try:
            # 注册发布工具
            publish_tool = PublishTool(self.adapter)
            self.tools[publish_tool.name] = publish_tool
            
            # 注册评论工具
            get_comments_tool = GetCommentsTool(self.adapter)
            self.tools[get_comments_tool.name] = get_comments_tool
            
            reply_comments_tool = ReplyCommentsTool(self.adapter)
            self.tools[reply_comments_tool.name] = reply_comments_tool
            
            # 注册监控工具
            monitor_tool = MonitorTool(self.adapter)
            self.tools[monitor_tool.name] = monitor_tool
            
            # 注册超时诊断工具
            timeout_diagnostic_tool = TimeoutDiagnosticTool(self.adapter)
            self.tools[timeout_diagnostic_tool.name] = timeout_diagnostic_tool
            
            # 注册搜索工具
            search_tool = SearchNotesTool(self.adapter)
            self.tools[search_tool.name] = search_tool
            
            # 注册内容获取工具
            content_tool = GetNoteContentTool(self.adapter)
            self.tools[content_tool.name] = content_tool
            
            # 注册分析工具
            analyze_tool = AnalyzeNoteTool(self.adapter)
            self.tools[analyze_tool.name] = analyze_tool
            
            # 注册评论发布工具
            post_comment_tool = PostCommentTool(self.adapter)
            self.tools[post_comment_tool.name] = post_comment_tool
            
            # 注册账号管理工具
            account_management_tool = AccountManagementTool(self.adapter)
            self.tools[account_management_tool.name] = account_management_tool
            
            logger.info(f"成功注册 {len(self.tools)} 个工具: {list(self.tools.keys())}")
            
        except Exception as e:
            logger.error(f"工具注册失败: {str(e)}")
            raise
    
    def get_tool_list(self) -> List[types.Tool]:
        """
        获取所有工具的 MCP Tool 列表
        
        Returns:
            MCP Tool 列表
        """
        return [tool.to_mcp_tool() for tool in self.tools.values()]
    
    def get_tool(self, name: str) -> BaseTool:
        """
        根据名称获取工具
        
        Args:
            name: 工具名称
            
        Returns:
            工具实例
            
        Raises:
            ValueError: 工具不存在
        """
        if name not in self.tools:
            available_tools = list(self.tools.keys())
            raise ValueError(f"工具 '{name}' 不存在。可用工具: {available_tools}")
        
        return self.tools[name]
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """
        调用指定工具
        
        Args:
            name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        try:
            tool = self.get_tool(name)
            logger.info(f"调用工具: {name}")
            
            # 使用安全执行方法
            result = await tool.safe_execute(arguments)
            
            logger.info(f"工具 {name} 执行完成")
            return result
            
        except Exception as e:
            logger.error(f"工具调用失败 {name}: {str(e)}")
            error_content = f"❌ 工具调用失败\n\n🚨 错误: {str(e)}\n🔧 工具: {name}\n📝 请检查参数格式和网络连接"
            return [types.TextContent(type="text", text=error_content)]
    
    def get_tool_info(self) -> Dict[str, Any]:
        """
        获取所有工具的信息
        
        Returns:
            工具信息字典
        """
        tool_info = {}
        
        for name, tool in self.tools.items():
            tool_info[name] = {
                "name": tool.name,
                "description": tool.description,
                "schema": tool.get_schema(),
                "type": tool.__class__.__name__
            }
        
        return tool_info
    
    def validate_tool_arguments(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证工具参数
        
        Args:
            name: 工具名称
            arguments: 待验证的参数
            
        Returns:
            验证后的参数
            
        Raises:
            ValueError: 参数验证失败
        """
        tool = self.get_tool(name)
        return tool.validate_arguments(arguments)
    
    def get_tools_by_category(self) -> Dict[str, List[str]]:
        """
        按类别获取工具列表
        
        Returns:
            按类别分组的工具列表
        """
        categories = {
            "内容管理": [],
            "评论管理": [],
            "内容搜索": [],
            "内容获取": [],
            "内容分析": [],
            "账号管理": [],
            "系统监控": [],
            "诊断工具": [],
            "其他": []
        }
        
        for name, tool in self.tools.items():
            if "publish" in name:
                categories["内容管理"].append(name)
            elif "comment" in name:
                categories["评论管理"].append(name)
            elif "search" in name:
                categories["内容搜索"].append(name)
            elif "content" in name:
                categories["内容获取"].append(name)
            elif "analyze" in name:
                categories["内容分析"].append(name)
            elif "account" in name:
                categories["账号管理"].append(name)
            elif "monitor" in name:
                categories["系统监控"].append(name)
            elif "diagnostic" in name or "timeout" in name:
                categories["诊断工具"].append(name)
            else:
                categories["其他"].append(name)
        
        # 移除空类别
        return {k: v for k, v in categories.items() if v}
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        获取工具使用统计（简化版本）
        
        Returns:
            使用统计信息
        """
        return {
            "total_tools": len(self.tools),
            "tool_names": list(self.tools.keys()),
            "categories": self.get_tools_by_category(),
            "last_updated": "2024-01-01T00:00:00"  # 可以后续实现真实的统计
        } 