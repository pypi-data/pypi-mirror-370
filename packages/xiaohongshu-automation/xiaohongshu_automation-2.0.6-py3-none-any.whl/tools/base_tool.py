"""
基础工具类
为所有 MCP 工具提供通用功能
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
from pydantic import BaseModel, ValidationError
import mcp.types as types

logger = logging.getLogger(__name__)

class ToolResult(BaseModel):
    """工具执行结果"""
    success: bool
    data: Optional[Any] = None
    message: str = ""
    error: Optional[str] = None
    timestamp: str = ""
    execution_time: Optional[float] = None
    
    def __init__(self, **data):
        if "timestamp" not in data:
            data["timestamp"] = datetime.now().isoformat()
        super().__init__(**data)

class BaseTool(ABC):
    """MCP 工具基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = logging.getLogger(f"tool.{name}")
    
    @abstractmethod
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行工具逻辑
        
        Args:
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        pass
    
    @abstractmethod
    def get_schema(self) -> Dict[str, Any]:
        """
        获取工具的 JSON Schema
        
        Returns:
            工具参数的 JSON Schema
        """
        pass
    
    def validate_arguments(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证工具参数
        
        Args:
            arguments: 待验证的参数
            
        Returns:
            验证后的参数
            
        Raises:
            ValueError: 参数验证失败
        """
        schema = self.get_schema()
        required_fields = schema.get("required", [])
        properties = schema.get("properties", {})
        
        # 检查必需字段
        for field in required_fields:
            if field not in arguments:
                raise ValueError(f"缺少必需参数: {field}")
        
        # 类型验证和转换
        validated_args = {}
        for key, value in arguments.items():
            if key in properties:
                prop_schema = properties[key]
                validated_args[key] = self._validate_field(key, value, prop_schema)
            else:
                self.logger.warning(f"未知参数: {key}")
                validated_args[key] = value
        
        return validated_args
    
    def _validate_field(self, field_name: str, value: Any, schema: Dict[str, Any]) -> Any:
        """
        验证单个字段
        
        Args:
            field_name: 字段名
            value: 字段值
            schema: 字段的 JSON Schema
            
        Returns:
            验证后的值
        """
        field_type = schema.get("type")
        
        if field_type == "string":
            if not isinstance(value, str):
                raise ValueError(f"参数 {field_name} 必须是字符串类型")
            
            # 检查最小/最大长度
            min_length = schema.get("minLength")
            max_length = schema.get("maxLength")
            if min_length and len(value) < min_length:
                raise ValueError(f"参数 {field_name} 长度不能少于 {min_length} 个字符")
            if max_length and len(value) > max_length:
                raise ValueError(f"参数 {field_name} 长度不能超过 {max_length} 个字符")
                
        elif field_type == "array":
            if not isinstance(value, list):
                raise ValueError(f"参数 {field_name} 必须是数组类型")
            
            # 检查数组长度
            min_items = schema.get("minItems")
            max_items = schema.get("maxItems")
            if min_items and len(value) < min_items:
                raise ValueError(f"参数 {field_name} 至少需要 {min_items} 个元素")
            if max_items and len(value) > max_items:
                raise ValueError(f"参数 {field_name} 最多只能有 {max_items} 个元素")
                
        elif field_type == "object":
            if not isinstance(value, dict):
                raise ValueError(f"参数 {field_name} 必须是对象类型")
        
        return value
    
    def format_result(self, result: ToolResult) -> List[types.TextContent]:
        """
        格式化工具执行结果为 MCP 响应
        
        Args:
            result: 工具执行结果
            
        Returns:
            MCP 文本内容列表
        """
        if result.success:
            # 成功结果
            content = self._format_success_result(result)
        else:
            # 错误结果
            content = self._format_error_result(result)
        
        return [types.TextContent(type="text", text=content)]
    
    def _format_success_result(self, result: ToolResult) -> str:
        """格式化成功结果"""
        output = f"✅ {self.name} 执行成功\n\n"
        
        if result.message:
            output += f"📝 消息: {result.message}\n\n"
        
        if result.data:
            if isinstance(result.data, dict):
                output += "📊 结果数据:\n"
                output += json.dumps(result.data, indent=2, ensure_ascii=False)
            else:
                output += f"📊 结果: {result.data}"
        
        if result.execution_time:
            output += f"\n\n⏱️ 执行时间: {result.execution_time:.2f}秒"
        
        output += f"\n🕐 完成时间: {result.timestamp}"
        
        return output
    
    def _format_error_result(self, result: ToolResult) -> str:
        """格式化错误结果"""
        output = f"❌ {self.name} 执行失败\n\n"
        
        if result.error:
            output += f"🚨 错误信息: {result.error}\n\n"
        
        if result.message:
            output += f"📝 详细说明: {result.message}\n\n"
        
        output += f"🕐 失败时间: {result.timestamp}"
        
        return output
    
    async def safe_execute(self, arguments: Dict[str, Any]) -> List[types.TextContent]:
        """
        安全执行工具，包含完整的错误处理
        
        Args:
            arguments: 工具参数
            
        Returns:
            MCP 响应内容
        """
        start_time = datetime.now()
        
        try:
            # 参数验证
            validated_args = self.validate_arguments(arguments)
            self.logger.info(f"开始执行工具 {self.name}")
            
            # 执行工具
            result = await self.execute(validated_args)
            
            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            result.execution_time = execution_time
            
            self.logger.info(f"工具 {self.name} 执行完成，耗时 {execution_time:.2f}秒")
            
            return self.format_result(result)
            
        except ValueError as e:
            # 参数验证错误
            self.logger.error(f"工具 {self.name} 参数验证失败: {str(e)}")
            error_result = ToolResult(
                success=False,
                error=f"参数验证失败: {str(e)}",
                message="请检查输入参数是否正确"
            )
            return self.format_result(error_result)
            
        except Exception as e:
            # 其他执行错误
            self.logger.error(f"工具 {self.name} 执行异常: {str(e)}")
            error_result = ToolResult(
                success=False,
                error=str(e),
                message="工具执行过程中发生未预期的错误"
            )
            return self.format_result(error_result)
    
    def to_mcp_tool(self) -> types.Tool:
        """
        转换为 MCP Tool 对象
        
        Returns:
            MCP Tool 对象
        """
        return types.Tool(
            name=self.name,
            description=self.description,
            inputSchema=self.get_schema()
        ) 