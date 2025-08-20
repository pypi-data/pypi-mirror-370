"""
超时诊断工具
帮助诊断和解决MCP服务的超时问题
"""

import asyncio
import time
import logging
from typing import Dict, Any, List
import httpx
from datetime import datetime

from tools.base_tool import BaseTool, ToolResult
from config import MCPConfig

logger = logging.getLogger(__name__)

class TimeoutDiagnosticTool(BaseTool):
    """超时诊断工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_timeout_diagnostic",
            description="诊断MCP服务和FastAPI后端的连接和超时问题，提供解决建议"
        )
        self.adapter = adapter
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行超时诊断
        
        Args:
            arguments: 诊断参数
            
        Returns:
            诊断结果
        """
        try:
            include_network_test = arguments.get("include_network_test", True)
            include_performance_test = arguments.get("include_performance_test", True)
            test_endpoints = arguments.get("test_endpoints", ["health", "publish", "comments"])
            
            diagnostic_results = {
                "timestamp": datetime.now().isoformat(),
                "config_check": await self._check_timeout_config(),
                "service_status": await self._check_service_status(),
                "network_tests": [],
                "performance_tests": [],
                "recommendations": []
            }
            
            # 网络连接测试
            if include_network_test:
                diagnostic_results["network_tests"] = await self._run_network_tests(test_endpoints)
            
            # 性能测试
            if include_performance_test:
                diagnostic_results["performance_tests"] = await self._run_performance_tests(test_endpoints)
            
            # 生成建议
            diagnostic_results["recommendations"] = self._generate_recommendations(diagnostic_results)
            
            return ToolResult(
                success=True,
                data=diagnostic_results,
                message=f"超时诊断完成，检查了 {len(test_endpoints)} 个端点"
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message="超时诊断执行失败"
            )
    
    async def _check_timeout_config(self) -> Dict[str, Any]:
        """检查超时配置"""
        config = MCPConfig.get_adapter_config()
        
        return {
            "default_timeout": config["timeout"],
            "publish_timeout": config["publish_timeout"],
            "comments_timeout": config["comments_timeout"],
            "monitor_timeout": config["monitor_timeout"],
            "health_check_timeout": config["health_check_timeout"],
            "auto_retry_enabled": config["enable_auto_retry"],
            "max_retries": config["max_retries"],
            "retry_delay": config["retry_delay"],
            "fastapi_url": config["base_url"]
        }
    
    async def _check_service_status(self) -> Dict[str, Any]:
        """检查服务状态"""
        start_time = time.time()
        
        try:
            # 简单连接测试
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.adapter.base_url}/docs")
                
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "is_running": response.status_code == 200,
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "url": f"{self.adapter.base_url}/docs",
                "error": None
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "is_running": False,
                "status_code": None,
                "response_time": round(response_time, 3),
                "url": f"{self.adapter.base_url}/docs",
                "error": str(e)
            }
    
    async def _run_network_tests(self, endpoints: List[str]) -> List[Dict[str, Any]]:
        """运行网络连接测试"""
        tests = []
        
        for endpoint in endpoints:
            if endpoint == "health":
                test_result = await self._test_endpoint("GET", "/docs", "health_check")
            elif endpoint == "publish":
                test_result = await self._test_endpoint("POST", "/publish", "publish", test_data=True)
            elif endpoint == "comments":
                test_result = await self._test_endpoint("GET", "/get_comments", "comments", test_params=True)
            else:
                continue
                
            tests.append({
                "endpoint": endpoint,
                **test_result
            })
        
        return tests
    
    async def _test_endpoint(self, method: str, path: str, operation: str, test_data: bool = False, test_params: bool = False) -> Dict[str, Any]:
        """测试单个端点"""
        url = f"{self.adapter.base_url}{path}"
        timeout = MCPConfig.get_timeout_for_operation(operation)
        
        kwargs = {"timeout": timeout}
        
        if test_data and method == "POST":
            kwargs["json"] = {
                "pic_urls": ["https://example.com/test.jpg"],
                "title": "超时测试",
                "content": "这是一个超时诊断测试"
            }
        
        if test_params and method == "GET":
            kwargs["params"] = {"url": "https://www.xiaohongshu.com/explore/test"}
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(method, url, **kwargs)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": True,
                "status_code": response.status_code,
                "response_time": round(response_time, 3),
                "timeout_setting": timeout,
                "method": method,
                "url": url,
                "error": None
            }
            
        except httpx.TimeoutException as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": False,
                "status_code": None,
                "response_time": round(response_time, 3),
                "timeout_setting": timeout,
                "method": method,
                "url": url,
                "error": f"超时错误: {str(e)}"
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": False,
                "status_code": None,
                "response_time": round(response_time, 3),
                "timeout_setting": timeout,
                "method": method,
                "url": url,
                "error": str(e)
            }
    
    async def _run_performance_tests(self, endpoints: List[str]) -> List[Dict[str, Any]]:
        """运行性能测试"""
        tests = []
        
        for endpoint in endpoints:
            if endpoint == "health":
                # 连续测试健康检查端点
                times = []
                for i in range(5):
                    start_time = time.time()
                    try:
                        async with httpx.AsyncClient(timeout=5.0) as client:
                            response = await client.get(f"{self.adapter.base_url}/docs")
                        end_time = time.time()
                        times.append(end_time - start_time)
                    except:
                        times.append(None)
                    
                    if i < 4:  # 最后一次不等待
                        await asyncio.sleep(0.5)
                
                valid_times = [t for t in times if t is not None]
                if valid_times:
                    tests.append({
                        "endpoint": endpoint,
                        "test_type": "performance",
                        "sample_count": len(valid_times),
                        "avg_response_time": round(sum(valid_times) / len(valid_times), 3),
                        "min_response_time": round(min(valid_times), 3),
                        "max_response_time": round(max(valid_times), 3),
                        "success_rate": len(valid_times) / len(times) * 100
                    })
        
        return tests
    
    def _generate_recommendations(self, diagnostic_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成改进建议"""
        recommendations = []
        
        # 检查服务状态
        if not diagnostic_results["service_status"]["is_running"]:
            recommendations.append({
                "priority": "高",
                "category": "服务状态",
                "issue": "FastAPI服务未运行",
                "solution": "运行命令：python main.py 启动后端服务",
                "details": f"无法连接到 {diagnostic_results['config_check']['fastapi_url']}"
            })
        
        # 检查响应时间
        service_response_time = diagnostic_results["service_status"]["response_time"]
        if service_response_time > 3.0:
            recommendations.append({
                "priority": "中",
                "category": "性能",
                "issue": f"服务响应时间较慢（{service_response_time}秒）",
                "solution": "检查服务器负载，考虑增加超时设置",
                "details": "建议将超时设置增加到60秒以上"
            })
        
        # 检查网络测试结果
        for test in diagnostic_results.get("network_tests", []):
            if not test["success"]:
                if "503" in str(test.get("error", "")):
                    recommendations.append({
                        "priority": "高",
                        "category": "服务可用性",
                        "issue": f"{test['endpoint']} 端点返回503错误",
                        "solution": "确保FastAPI服务完全启动并且所有依赖正常",
                        "details": "503错误表示服务暂时不可用"
                    })
                elif "超时" in str(test.get("error", "")):
                    recommendations.append({
                        "priority": "中",
                        "category": "超时配置",
                        "issue": f"{test['endpoint']} 端点超时",
                        "solution": f"考虑将{test['endpoint']}操作的超时设置从{test['timeout_setting']}秒增加到更大值",
                        "details": "可以通过环境变量调整超时设置"
                    })
        
        # 检查超时配置
        config = diagnostic_results["config_check"]
        if config["default_timeout"] < 30:
            recommendations.append({
                "priority": "低",
                "category": "配置优化",
                "issue": "默认超时设置较低",
                "solution": f"考虑将默认超时从{config['default_timeout']}秒增加到30-60秒",
                "details": "可以通过设置 FASTAPI_TIMEOUT 环境变量调整"
            })
        
        if not config["auto_retry_enabled"]:
            recommendations.append({
                "priority": "低",
                "category": "可靠性",
                "issue": "自动重试功能未启用",
                "solution": "启用自动重试以提高系统稳定性",
                "details": "可以通过设置 ENABLE_AUTO_RETRY=true 环境变量启用"
            })
        
        # 如果没有发现问题，给出积极的反馈
        if not recommendations:
            recommendations.append({
                "priority": "信息",
                "category": "系统状态",
                "issue": "未发现明显问题",
                "solution": "系统配置良好，继续监控",
                "details": "所有检查均通过，系统运行正常"
            })
        
        return recommendations
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数架构"""
        return {
            "type": "object",
            "properties": {
                "include_network_test": {
                    "type": "boolean",
                    "description": "是否包含网络连接测试",
                    "default": True
                },
                "include_performance_test": {
                    "type": "boolean", 
                    "description": "是否包含性能测试",
                    "default": True
                },
                "test_endpoints": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["health", "publish", "comments"]
                    },
                    "description": "要测试的端点列表",
                    "default": ["health", "publish", "comments"]
                }
            }
        } 