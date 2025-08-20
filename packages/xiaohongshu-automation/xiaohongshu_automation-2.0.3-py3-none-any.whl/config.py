"""
MCP 服务端配置文件
"""

import os
from typing import Dict, Any

class MCPConfig:
    """MCP 服务端配置类"""
    
    # FastAPI 服务配置
    FASTAPI_BASE_URL = os.getenv("FASTAPI_BASE_URL", "http://localhost:8000")
    FASTAPI_TIMEOUT = int(os.getenv("FASTAPI_TIMEOUT", "30"))  # 降低默认超时
    
    # 不同操作的超时设置
    PUBLISH_TIMEOUT = int(os.getenv("PUBLISH_TIMEOUT", "160"))  # 发布操作较长
    COMMENTS_TIMEOUT = int(os.getenv("COMMENTS_TIMEOUT", "130"))  # 评论操作中等
    MONITOR_TIMEOUT = int(os.getenv("MONITOR_TIMEOUT", "115"))   # 监控操作较快
    SEARCH_TIMEOUT = int(os.getenv("SEARCH_TIMEOUT", "45"))      # 搜索操作较快
    CONTENT_TIMEOUT = int(os.getenv("CONTENT_TIMEOUT", "60"))    # 内容获取操作
    ANALYSIS_TIMEOUT = int(os.getenv("ANALYSIS_TIMEOUT", "70"))  # 分析操作
    HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))  # 健康检查很快
    
    # MCP 服务端配置
    SERVER_NAME = "xiaohongshu-automation"
    SERVER_VERSION = "1.0.0"
    
    # 日志配置
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 功能开关
    ENABLE_TOOLS = True
    ENABLE_RESOURCES = True
    ENABLE_PROMPTS = True
    
    # 监控配置
    MONITOR_INTERVAL = int(os.getenv("MONITOR_INTERVAL", "180"))  # 3分钟
    MAX_HISTORY_RECORDS = int(os.getenv("MAX_HISTORY_RECORDS", "50"))
    
    # 重试配置
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "2"))
    
    # 错误处理配置
    ENABLE_AUTO_RETRY = os.getenv("ENABLE_AUTO_RETRY", "true").lower() == "true"
    DETAILED_ERROR_MSG = os.getenv("DETAILED_ERROR_MSG", "true").lower() == "true"
    
    @classmethod
    def get_server_capabilities(cls) -> Dict[str, Any]:
        """获取服务端能力配置"""
        return {
            "tools": cls.ENABLE_TOOLS,
            "resources": cls.ENABLE_RESOURCES,
            "prompts": cls.ENABLE_PROMPTS,
            "logging": {}
        }
    
    @classmethod
    def get_adapter_config(cls) -> Dict[str, Any]:
        """获取适配器配置"""
        return {
            "base_url": cls.FASTAPI_BASE_URL,
            "timeout": cls.FASTAPI_TIMEOUT,
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY,
            "publish_timeout": cls.PUBLISH_TIMEOUT,
            "comments_timeout": cls.COMMENTS_TIMEOUT,
            "monitor_timeout": cls.MONITOR_TIMEOUT,
            "search_timeout": cls.SEARCH_TIMEOUT,
            "content_timeout": cls.CONTENT_TIMEOUT,
            "analysis_timeout": cls.ANALYSIS_TIMEOUT,
            "health_check_timeout": cls.HEALTH_CHECK_TIMEOUT,
            "enable_auto_retry": cls.ENABLE_AUTO_RETRY,
            "detailed_error_msg": cls.DETAILED_ERROR_MSG
        }
    
    @classmethod
    def get_timeout_for_operation(cls, operation: str) -> int:
        """
        根据操作类型获取超时设置
        
        Args:
            operation: 操作类型 (publish, comments, monitor, search, content, analysis, health_check)
            
        Returns:
            超时秒数
        """
        timeouts = {
            "publish": cls.PUBLISH_TIMEOUT,
            "comments": cls.COMMENTS_TIMEOUT,
            "monitor": cls.MONITOR_TIMEOUT,
            "search": cls.SEARCH_TIMEOUT,
            "content": cls.CONTENT_TIMEOUT,
            "analysis": cls.ANALYSIS_TIMEOUT,
            "health_check": cls.HEALTH_CHECK_TIMEOUT
        }
        return timeouts.get(operation, cls.FASTAPI_TIMEOUT) 