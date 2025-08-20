"""
小红书适配器
连接 MCP 服务端和现有的 FastAPI 服务
支持多账号操作
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
import httpx
import json
from datetime import datetime
from config import MCPConfig

logger = logging.getLogger(__name__)

class XiaohongshuAdapter:
    """小红书功能适配器，负责与现有 FastAPI 服务通信，支持多账号操作"""
    
    def __init__(self, fastapi_base_url: str = "http://localhost:8000"):
        self.base_url = fastapi_base_url
        self.config = MCPConfig.get_adapter_config()
        
        # 使用配置的超时设置创建客户端
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=5.0,  # 连接超时
                read=self.config["timeout"],  # 读取超时
                write=10.0,   # 写入超时
                pool=5.0      # 连接池超时
            )
        )
        
        self._monitor_status = {
            "is_running": True,
            "last_check": datetime.now().isoformat(),
            "success_count": 0,
            "error_count": 0
        }
        self._publish_history = []
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request_with_retry(self, method: str, url: str, operation: str, **kwargs) -> httpx.Response:
        """
        带重试机制的HTTP请求
        
        Args:
            method: HTTP方法
            url: 请求URL
            operation: 操作类型，用于获取超时设置
            **kwargs: 其他请求参数
            
        Returns:
            HTTP响应
            
        Raises:
            Exception: 所有重试都失败后抛出异常
        """
        # 获取操作特定的超时设置
        timeout = MCPConfig.get_timeout_for_operation(operation)
        kwargs['timeout'] = timeout
        
        max_retries = self.config["max_retries"] if self.config["enable_auto_retry"] else 1
        retry_delay = self.config["retry_delay"]
        
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    logger.info(f"重试第 {attempt} 次请求: {method} {url}")
                    await asyncio.sleep(retry_delay)
                
                response = await self.client.request(method, url, **kwargs)
                
                # 检查状态码
                if response.status_code == 503:
                    raise httpx.HTTPStatusError(
                        "FastAPI 服务当前不可用 (503)。请确保后端服务正在运行：python main.py",
                        request=response.request,
                        response=response
                    )
                
                response.raise_for_status()
                return response
                
            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(f"请求超时 (尝试 {attempt + 1}/{max_retries}): {url} - 超时设置: {timeout}秒")
                if attempt == max_retries - 1:
                    raise Exception(f"请求超时：{timeout}秒内无响应。建议检查网络连接或增加超时设置。")
                    
            except httpx.ConnectError as e:
                last_exception = e
                logger.warning(f"连接失败 (尝试 {attempt + 1}/{max_retries}): {url}")
                if attempt == max_retries - 1:
                    raise Exception(f"无法连接到FastAPI服务({self.base_url})。请确保服务正在运行：python main.py")
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 503:
                    last_exception = e
                    logger.warning(f"服务不可用 (尝试 {attempt + 1}/{max_retries}): {url}")
                    if attempt == max_retries - 1:
                        raise Exception("FastAPI服务当前不可用。请启动后端服务：python main.py")
                else:
                    # 其他HTTP错误不重试
                    raise e
                    
            except Exception as e:
                last_exception = e
                logger.error(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    break
        
        # 所有重试都失败
        raise Exception(f"请求失败，已重试 {max_retries} 次。最后错误: {str(last_exception)}")
    
    async def publish_content(self, pic_urls: List[str], title: str, content: str, labels: Optional[List[str]] = None, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        发布内容到小红书
        
        Args:
            pic_urls: 图片URL列表
            title: 标题
            content: 内容
            labels: 自定义标签列表，可选
            phone_number: 指定账号手机号，可选
            
        Returns:
            发布结果
        """
        try:
            # 构建请求参数
            data = {
                "pic_urls": pic_urls,
                "title": title,
                "content": content
            }
            
            # 如果提供了labels参数，添加到请求数据中
            if labels is not None:
                data["labels"] = labels
                
            # 如果提供了phone_number参数，添加到请求数据中
            if phone_number is not None:
                data["phone_number"] = phone_number
            
            account_info = phone_number or "默认账号"
            logger.info(f"开始发布内容: {title} (账号: {account_info})")
            
            # 调用 FastAPI 服务 - 使用改进的重试机制
            response = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/publish",
                "publish",
                json=data
            )
            
            result = response.json()
            
            # 检查响应中的status字段，如果是error则抛出异常
            if result.get("status") == "error":
                error_message = result.get("message", "发布失败，未知错误")
                logger.error(f"FastAPI返回错误: {error_message}")
                # 添加明确的业务错误标识，让异常处理能正确识别
                raise Exception(f"发布失败: {error_message}")
            
            # 记录发布历史
            self._publish_history.append({
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "pic_count": len(pic_urls),
                "labels": labels or ["#小红书"],  # 记录使用的标签
                "phone_number": phone_number,  # 记录使用的账号
                "status": result.get("status", "unknown"),
                "urls": result.get("urls", [])
            })
            
            # 保持历史记录在合理范围内
            if len(self._publish_history) > 50:
                self._publish_history = self._publish_history[-50:]
            
            logger.info(f"内容发布成功: {title} (账号: {account_info})")
            return result
            
        except Exception as e:
            error_msg = str(e)
            account_info = phone_number or "默认账号"
            logger.error(f"发布内容失败 (账号: {account_info}): {error_msg}")
            
            # 记录失败的发布历史
            self._publish_history.append({
                "timestamp": datetime.now().isoformat(),
                "title": title,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "pic_count": len(pic_urls),
                "labels": labels or ["#小红书"],  # 记录使用的标签
                "phone_number": phone_number,  # 记录使用的账号
                "status": "failed",
                "error": error_msg
            })
            
            # 优先检查是否为业务逻辑错误（来自FastAPI响应的error状态）
            if "发布失败:" in error_msg:
                # 保持原有的业务错误信息
                raise Exception(error_msg)
            elif "timeout" in error_msg.lower() or "超时" in error_msg:
                raise Exception(f"发布超时: {error_msg}")
            elif "connect" in error_msg.lower() or "连接" in error_msg:
                raise Exception(f"连接失败: 无法连接到小红书服务。请检查网络连接和服务状态。详细错误: {error_msg}")
            else:
                raise Exception(f"发布失败: {error_msg}")
    
    async def get_comments(self, url: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        获取小红书笔记评论
        
        Args:
            url: 小红书笔记URL
            phone_number: 指定账号手机号，可选
            
        Returns:
            评论列表和分析结果
        """
        try:
            account_info = phone_number or "默认账号"
            logger.info(f"开始获取评论: {url} (账号: {account_info})")
            
            # 构建请求参数
            params = {"url": url}
            if phone_number is not None:
                params["phone_number"] = phone_number
            
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/get_comments",
                "comments",
                params=params
            )
            
            result = response.json()
            logger.info(f"评论获取完成: {url} (账号: {account_info})")
            return result
            
        except Exception as e:
            error_msg = str(e)
            account_info = phone_number or "默认账号"
            logger.error(f"获取评论失败 (账号: {account_info}): {error_msg}")
            
            if "timeout" in error_msg.lower() or "超时" in error_msg:
                raise Exception(f"获取评论超时: {error_msg}")
            elif "connect" in error_msg.lower() or "连接" in error_msg:
                raise Exception(f"连接失败: 无法连接到小红书服务。请检查网络连接。详细错误: {error_msg}")
            else:
                raise Exception(f"获取评论失败: {error_msg}")
    
    async def reply_comments(self, comments_response: Dict[str, List[str]], url: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        回复小红书笔记评论
        
        Args:
            comments_response: 评论回复映射
            url: 小红书笔记URL
            phone_number: 指定账号手机号，可选
            
        Returns:
            回复结果
        """
        try:
            account_info = phone_number or "默认账号"
            logger.info(f"开始回复评论: {url} (账号: {account_info})")
            
            # 构建请求参数
            params = {"url": url}
            if phone_number is not None:
                params["phone_number"] = phone_number
            
            response = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/post_comments",
                "comments",
                params=params,
                json=comments_response
            )
            
            result = response.json()
            logger.info(f"评论回复完成: {url} (账号: {account_info})")
            return result
            
        except Exception as e:
            error_msg = str(e)
            account_info = phone_number or "默认账号"
            logger.error(f"回复评论失败 (账号: {account_info}): {error_msg}")
            
            if "timeout" in error_msg.lower() or "超时" in error_msg:
                raise Exception(f"回复评论超时: {error_msg}")
            elif "connect" in error_msg.lower() or "连接" in error_msg:
                raise Exception(f"连接失败: 无法连接到小红书服务。请检查网络连接。详细错误: {error_msg}")
            else:
                raise Exception(f"回复评论失败: {error_msg}")
    
    async def search_notes(self, keywords: str, limit: int = 5, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        搜索小红书笔记
        
        Args:
            keywords: 搜索关键词
            limit: 返回结果数量限制，最多20条
            phone_number: 指定账号手机号，可选
            
        Returns:
            搜索结果列表
        """
        try:
            account_info = phone_number or "默认账号"
            logger.info(f"开始搜索笔记: {keywords} (账号: {account_info})")
            
            # 构建请求参数
            params = {
                "keywords": keywords,
                "limit": min(max(limit, 1), 20)  # 确保limit在1-20范围内
            }
            if phone_number is not None:
                params["phone_number"] = phone_number
            
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/search_notes",
                "content",
                params=params
            )
            
            result = response.json()
            logger.info(f"笔记搜索完成: {keywords} (账号: {account_info})")
            return result
            
        except Exception as e:
            error_msg = str(e)
            account_info = phone_number or "默认账号"
            logger.error(f"搜索笔记失败 (账号: {account_info}): {error_msg}")
            
            if "timeout" in error_msg.lower() or "超时" in error_msg:
                raise Exception(f"搜索超时: {error_msg}")
            elif "connect" in error_msg.lower() or "连接" in error_msg:
                raise Exception(f"连接失败: 无法连接到小红书服务。请检查网络连接。详细错误: {error_msg}")
            else:
                raise Exception(f"搜索失败: {error_msg}")
    
    async def get_note_content(self, url: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        获取小红书笔记的详细内容
        
        Args:
            url: 小红书笔记URL
            phone_number: 指定账号手机号，可选
            
        Returns:
            笔记详细内容
        """
        try:
            account_info = phone_number or "默认账号"
            logger.info(f"开始获取笔记内容: {url} (账号: {account_info})")
            
            # 构建请求参数
            params = {"url": url}
            if phone_number is not None:
                params["phone_number"] = phone_number
            
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/get_note_content",
                "content",
                params=params
            )
            
            result = response.json()
            logger.info(f"笔记内容获取完成: {url} (账号: {account_info})")
            return result
            
        except Exception as e:
            error_msg = str(e)
            account_info = phone_number or "默认账号"
            logger.error(f"获取笔记内容失败 (账号: {account_info}): {error_msg}")
            
            if "timeout" in error_msg.lower() or "超时" in error_msg:
                raise Exception(f"获取内容超时: {error_msg}")
            elif "connect" in error_msg.lower() or "连接" in error_msg:
                raise Exception(f"连接失败: 无法连接到小红书服务。请检查网络连接。详细错误: {error_msg}")
            else:
                raise Exception(f"获取内容失败: {error_msg}")
    
    async def analyze_note(self, url: str, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        分析小红书笔记内容，提取关键信息和领域标签
        
        Args:
            url: 小红书笔记URL
            phone_number: 指定账号手机号，可选
            
        Returns:
            笔记分析结果
        """
        try:
            account_info = phone_number or "默认账号"
            logger.info(f"开始分析笔记: {url} (账号: {account_info})")
            
            # 构建请求参数
            params = {"url": url}
            if phone_number is not None:
                params["phone_number"] = phone_number
            
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/analyze_note",
                "analysis",
                params=params
            )
            
            result = response.json()
            logger.info(f"笔记分析完成: {url} (账号: {account_info})")
            return result
            
        except Exception as e:
            error_msg = str(e)
            account_info = phone_number or "默认账号"
            logger.error(f"分析笔记失败 (账号: {account_info}): {error_msg}")
            
            if "timeout" in error_msg.lower() or "超时" in error_msg:
                raise Exception(f"分析超时: {error_msg}")
            elif "connect" in error_msg.lower() or "连接" in error_msg:
                raise Exception(f"连接失败: 无法连接到小红书服务。请检查网络连接。详细错误: {error_msg}")
            else:
                raise Exception(f"分析失败: {error_msg}")
    
    async def post_comment(self, url: str, comment: str, mentions: Optional[List[str]] = None, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        发布评论到指定小红书笔记
        
        Args:
            url: 小红书笔记URL
            comment: 要发布的评论内容
            mentions: 可选的@提及用户名列表
            phone_number: 指定账号手机号，可选
            
        Returns:
            评论发布结果
        """
        try:
            account_info = phone_number or "默认账号"
            logger.info(f"开始发布评论: {url} (账号: {account_info})")
            
            # 构建请求参数
            params = {"url": url}
            if phone_number is not None:
                params["phone_number"] = phone_number
                
            request_data = {
                "comment": comment
            }
            if mentions:
                request_data["metions_lists"] = mentions  # 注意：保持与API一致的字段名
            if phone_number:
                request_data["phone_number"] = phone_number
            
            response = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/post_comment",
                "comments",
                params=params,
                json=request_data
            )
            
            result = response.json()
            logger.info(f"评论发布完成: {url} (账号: {account_info})")
            return result
            
        except Exception as e:
            error_msg = str(e)
            account_info = phone_number or "默认账号"
            logger.error(f"发布评论失败 (账号: {account_info}): {error_msg}")
            
            if "timeout" in error_msg.lower() or "超时" in error_msg:
                raise Exception(f"发布评论超时: {error_msg}")
            elif "connect" in error_msg.lower() or "连接" in error_msg:
                raise Exception(f"连接失败: 无法连接到小红书服务。请检查网络连接。详细错误: {error_msg}")
            else:
                raise Exception(f"发布评论失败: {error_msg}")
    
    # ==================== 账号管理接口 ====================
    
    async def add_account(self, phone_number: str) -> Dict[str, Any]:
        """
        添加新账号
        
        Args:
            phone_number: 手机号
            
        Returns:
            添加结果
        """
        try:
            logger.info(f"开始添加账号: {phone_number}")
            
            response = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/account/add",
                "default",
                json={"phone_number": phone_number}
            )
            
            result = response.json()
            logger.info(f"账号添加完成: {phone_number}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"添加账号失败: {phone_number} - {error_msg}")
            raise Exception(f"添加账号失败: {error_msg}")
    
    async def list_accounts(self) -> Dict[str, Any]:
        """
        获取所有账号列表
        
        Returns:
            账号列表
        """
        try:
            logger.info("开始获取账号列表")
            
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/account/list",
                "default"
            )
            
            result = response.json()
            logger.info(f"账号列表获取完成，共 {result.get('total', 0)} 个账号")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取账号列表失败: {error_msg}")
            raise Exception(f"获取账号列表失败: {error_msg}")
    
    async def set_current_account(self, phone_number: str) -> Dict[str, Any]:
        """
        设置当前默认账号
        
        Args:
            phone_number: 手机号
            
        Returns:
            设置结果
        """
        try:
            logger.info(f"开始设置当前账号: {phone_number}")
            
            response = await self._make_request_with_retry(
                "POST",
                f"{self.base_url}/account/set_current",
                "default",
                json={"phone_number": phone_number}
            )
            
            result = response.json()
            logger.info(f"当前账号设置完成: {phone_number}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"设置当前账号失败: {phone_number} - {error_msg}")
            raise Exception(f"设置当前账号失败: {error_msg}")
    
    async def remove_account(self, phone_number: str) -> Dict[str, Any]:
        """
        移除账号
        
        Args:
            phone_number: 手机号
            
        Returns:
            移除结果
        """
        try:
            logger.info(f"开始移除账号: {phone_number}")
            
            response = await self._make_request_with_retry(
                "DELETE",
                f"{self.base_url}/account/remove",
                "default",
                params={"phone_number": phone_number}
            )
            
            result = response.json()
            logger.info(f"账号移除完成: {phone_number}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"移除账号失败: {phone_number} - {error_msg}")
            raise Exception(f"移除账号失败: {error_msg}")
    
    async def get_account_status(self, phone_number: Optional[str] = None) -> Dict[str, Any]:
        """
        获取账号状态
        
        Args:
            phone_number: 手机号，为None时获取所有账号状态
            
        Returns:
            账号状态
        """
        try:
            account_info = phone_number or "所有账号"
            logger.info(f"开始获取账号状态: {account_info}")
            
            params = {}
            if phone_number:
                params["phone_number"] = phone_number
            
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/account/status",
                "default",
                params=params
            )
            
            result = response.json()
            logger.info(f"账号状态获取完成: {account_info}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            account_info = phone_number or "所有账号"
            logger.error(f"获取账号状态失败: {account_info} - {error_msg}")
            raise Exception(f"获取账号状态失败: {error_msg}")
    
    # ==================== 原有方法保持不变 ====================
    
    async def get_monitor_status(self) -> Dict[str, Any]:
        """
        获取监控状态
        
        Returns:
            监控状态信息
        """
        try:
            logger.info("开始获取监控状态")
            
            # 更新监控状态
            self._monitor_status["last_check"] = datetime.now().isoformat()
            
            # 执行健康检查
            is_healthy = await self.health_check()
            
            status_info = {
                "service_status": "healthy" if is_healthy else "unhealthy",
                "last_check": self._monitor_status["last_check"],
                "success_count": self._monitor_status["success_count"],
                "error_count": self._monitor_status["error_count"],
                "publish_history_count": len(self._publish_history),
                "connection_status": "connected" if is_healthy else "disconnected"
            }
            
            logger.info("监控状态获取完成")
            return status_info
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"获取监控状态失败: {error_msg}")
            raise Exception(f"获取监控状态失败: {error_msg}")
    
    async def get_publish_history(self) -> List[Dict[str, Any]]:
        """
        获取发布历史记录
        
        Returns:
            发布历史列表
        """
        return self._publish_history.copy()
    
    async def health_check(self) -> bool:
        """
        执行健康检查
        
        Returns:
            健康状态布尔值
        """
        try:
            response = await self._make_request_with_retry(
                "GET",
                f"{self.base_url}/",
                "health_check"
            )
            
            # 如果能成功获取响应，认为服务健康
            return response.status_code == 200
            
        except Exception:
            return False
    
    def update_monitor_stats(self, success: bool):
        """
        更新监控统计
        
        Args:
            success: 操作是否成功
        """
        if success:
            self._monitor_status["success_count"] += 1
        else:
            self._monitor_status["error_count"] += 1 