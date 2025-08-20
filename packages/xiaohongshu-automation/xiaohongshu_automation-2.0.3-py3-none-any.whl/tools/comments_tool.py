"""
小红书评论工具
实现评论获取和回复功能
"""

import re
from typing import Any, Dict, List
from urllib.parse import urlparse
from tools.base_tool import BaseTool, ToolResult

class GetCommentsTool(BaseTool):
    """获取小红书评论工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_get_comments",
            description="获取指定小红书帖子的评论信息，支持评论分析和统计"
        )
        self.adapter = adapter
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数 Schema"""
        return {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "小红书笔记URL，如：https://www.xiaohongshu.com/explore/...",
                    "pattern": r".*xiaohongshu\.com.*"
                },
                "phone_number": {
                    "type": "string",
                    "description": "指定获取评论账号的手机号（可选），如果不提供则使用当前默认账号",
                    "required": False
                },
                "analyze": {
                    "type": "boolean",
                    "description": "是否进行评论分析（默认true）",
                    "default": True
                }
            },
            "required": ["url"]
        }
    
    def _validate_xiaohongshu_url(self, url: str) -> str:
        """
        验证小红书URL格式
        
        Args:
            url: 待验证的URL
            
        Returns:
            验证后的URL
            
        Raises:
            ValueError: URL格式无效
        """
        try:
            parsed = urlparse(url)
            if not all([parsed.scheme, parsed.netloc]):
                raise ValueError("URL格式无效")
            
            if "xiaohongshu.com" not in parsed.netloc:
                raise ValueError("不是有效的小红书URL")
            
            return url
            
        except Exception as e:
            raise ValueError(f"URL验证失败: {str(e)}")
    
    def _analyze_comments(self, comments_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析评论数据
        
        Args:
            comments_data: 评论数据
            
        Returns:
            评论分析结果
        """
        analysis = {
            "total_comments": 0,
            "sentiment_distribution": {"positive": 0, "neutral": 0, "negative": 0},
            "keyword_frequency": {},
            "user_engagement": {"active_users": 0, "reply_rate": 0},
            "content_insights": {"avg_length": 0, "has_emojis": 0, "has_mentions": 0}
        }
        
        if comments_data.get("status") != "success":
            return analysis
        
        comments = comments_data.get("comments", [])
        if isinstance(comments, str):
            # 如果返回的是字符串（如"当前无评论"）
            return analysis
        
        if not isinstance(comments, list):
            return analysis
        
        analysis["total_comments"] = len(comments)
        
        if analysis["total_comments"] == 0:
            return analysis
        
        # 分析每条评论
        total_length = 0
        keywords = {}
        
        for comment in comments:
            if not isinstance(comment, dict):
                continue
                
            content = comment.get("content", "")
            if not content:
                continue
            
            # 长度统计
            total_length += len(content)
            
            # 表情符号检测
            if re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content):
                analysis["content_insights"]["has_emojis"] += 1
            
            # @用户检测
            if re.search(r'@[^\s@]+', content):
                analysis["content_insights"]["has_mentions"] += 1
            
            # 简单情感分析（基于关键词）
            positive_words = ["好", "棒", "赞", "喜欢", "爱", "美", "漂亮", "不错", "推荐", "👍", "❤️", "😍"]
            negative_words = ["差", "烂", "不好", "讨厌", "难看", "垃圾", "失望", "👎", "😞", "😡"]
            
            content_lower = content.lower()
            positive_count = sum(1 for word in positive_words if word in content_lower)
            negative_count = sum(1 for word in negative_words if word in content_lower)
            
            if positive_count > negative_count:
                analysis["sentiment_distribution"]["positive"] += 1
            elif negative_count > positive_count:
                analysis["sentiment_distribution"]["negative"] += 1
            else:
                analysis["sentiment_distribution"]["neutral"] += 1
            
            # 关键词提取（简单实现）
            words = re.findall(r'[\u4e00-\u9fff]+', content)  # 提取中文词汇
            for word in words:
                if len(word) >= 2:  # 只统计2字以上的词
                    keywords[word] = keywords.get(word, 0) + 1
        
        # 计算平均长度
        if analysis["total_comments"] > 0:
            analysis["content_insights"]["avg_length"] = total_length / analysis["total_comments"]
        
        # 提取热门关键词（前10个）
        sorted_keywords = sorted(keywords.items(), key=lambda x: x[1], reverse=True)
        analysis["keyword_frequency"] = dict(sorted_keywords[:10])
        
        # 用户参与度（简化计算）
        analysis["user_engagement"]["active_users"] = analysis["total_comments"]
        if analysis["total_comments"] > 0:
            analysis["user_engagement"]["reply_rate"] = (
                analysis["content_insights"]["has_mentions"] / analysis["total_comments"] * 100
            )
        
        return analysis
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行获取评论操作
        
        Args:
            arguments: 工具参数
            
        Returns:
            评论获取结果
        """
        try:
            # 提取参数
            url = arguments["url"]
            phone_number = arguments.get("phone_number")
            analyze = arguments.get("analyze", True)
            
            # 验证URL
            validated_url = self._validate_xiaohongshu_url(url)
            
            # 获取评论数据
            comments_data = await self.adapter.get_comments(validated_url, phone_number)
            
            # 构建结果
            result_data = {
                "comments_data": comments_data,
                "url": validated_url
            }
            
            # 如果需要分析
            if analyze:
                analysis = self._analyze_comments(comments_data)
                result_data["analysis"] = analysis
            
            # 判断获取状态
            if comments_data.get("status") == "success":
                if comments_data.get("message") == "当前无评论":
                    message = "帖子暂无评论"
                else:
                    comment_count = len(comments_data.get("comments", []))
                    message = f"成功获取 {comment_count} 条评论"
                    if analyze and result_data.get("analysis"):
                        sentiment = result_data["analysis"]["sentiment_distribution"]
                        message += f"（正面: {sentiment['positive']}, 中性: {sentiment['neutral']}, 负面: {sentiment['negative']}）"
            else:
                message = "获取评论失败"
            
            return ToolResult(
                success=True,
                data=result_data,
                message=message
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message="获取评论过程中发生错误，请检查URL格式和网络连接"
            )
    
    def _format_success_result(self, result: ToolResult) -> str:
        """自定义成功结果格式化"""
        output = f"✅ 评论获取完成！\n\n"
        
        if result.message:
            output += f"📝 {result.message}\n\n"
        
        if result.data:
            data = result.data
            comments_data = data.get("comments_data", {})
            analysis = data.get("analysis")
            
            # 基本信息
            output += f"🔗 帖子链接: {data.get('url', 'N/A')}\n"
            output += f"📊 获取状态: {comments_data.get('status', 'unknown')}\n"
            
            # 如果有分析数据
            if analysis:
                output += f"\n📈 评论分析:\n"
                output += f"   • 总评论数: {analysis['total_comments']}\n"
                
                if analysis['total_comments'] > 0:
                    sentiment = analysis['sentiment_distribution']
                    output += f"   • 情感分布: 正面 {sentiment['positive']} | 中性 {sentiment['neutral']} | 负面 {sentiment['negative']}\n"
                    
                    insights = analysis['content_insights']
                    output += f"   • 平均长度: {insights['avg_length']:.1f} 字\n"
                    output += f"   • 包含表情: {insights['has_emojis']} 条\n"
                    output += f"   • 包含@用户: {insights['has_mentions']} 条\n"
                    
                    # 热门关键词
                    if analysis['keyword_frequency']:
                        output += f"   • 热门关键词: {', '.join(list(analysis['keyword_frequency'].keys())[:5])}\n"
            
            # 评论内容预览（前3条）
            comments = comments_data.get("comments", [])
            if isinstance(comments, list) and len(comments) > 0:
                output += f"\n💬 评论预览（前3条）:\n"
                for i, comment in enumerate(comments[:3]):
                    if isinstance(comment, dict):
                        content = comment.get("content", "")[:50]
                        if len(comment.get("content", "")) > 50:
                            content += "..."
                        output += f"   {i+1}. {content}\n"
        
        if result.execution_time:
            output += f"\n⏱️ 获取耗时: {result.execution_time:.2f}秒"
        
        output += f"\n🕐 完成时间: {result.timestamp}"
        
        return output


class ReplyCommentsTool(BaseTool):
    """回复小红书评论工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_reply_comments",
            description="批量回复小红书帖子评论，支持智能回复建议"
        )
        self.adapter = adapter
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数 Schema"""
        return {
            "type": "object",
            "properties": {
                "comments_response": {
                    "type": "object",
                    "description": "评论回复数据，格式为 {comment_id: [reply1, reply2, ...]}",
                    "additionalProperties": {
                        "type": "array",
                        "items": {"type": "string"}
                    }
                },
                "url": {
                    "type": "string",
                    "description": "小红书笔记URL，如：https://www.xiaohongshu.com/explore/...",
                    "pattern": r".*xiaohongshu\.com.*"
                },
                "auto_optimize": {
                    "type": "boolean",
                    "description": "是否自动优化回复内容（默认true）",
                    "default": True
                },
                "phone_number": {
                    "type": "string",
                    "description": "指定回复评论账号的手机号（可选），如果不提供则使用当前默认账号",
                    "required": False
                }
            },
            "required": ["comments_response", "url"]
        }
    
    def _optimize_reply(self, reply: str) -> str:
        """
        优化回复内容
        
        Args:
            reply: 原始回复
            
        Returns:
            优化后的回复
        """
        # 基本清理
        optimized = reply.strip()
        
        # 确保友好语调
        if not any(word in optimized for word in ["谢谢", "感谢", "😊", "❤️", "👍"]):
            # 如果回复比较冷淡，添加友好元素
            if len(optimized) < 20 and not optimized.endswith(("！", "~", "😊")):
                optimized += " 😊"
        
        # 长度控制
        if len(optimized) > 200:
            optimized = optimized[:197] + "..."
        
        return optimized
    
    def _validate_replies(self, comments_response: Dict[str, List[str]], auto_optimize: bool = True) -> Dict[str, List[str]]:
        """
        验证和优化回复内容
        
        Args:
            comments_response: 评论回复数据
            auto_optimize: 是否自动优化
            
        Returns:
            验证后的回复数据
        """
        validated_responses = {}
        
        for comment_id, replies in comments_response.items():
            if not isinstance(replies, list):
                raise ValueError(f"评论 {comment_id} 的回复必须是数组格式")
            
            validated_replies = []
            for reply in replies:
                if not isinstance(reply, str):
                    raise ValueError(f"回复内容必须是字符串格式")
                
                if len(reply.strip()) == 0:
                    continue  # 跳过空回复
                
                if auto_optimize:
                    optimized_reply = self._optimize_reply(reply)
                    validated_replies.append(optimized_reply)
                else:
                    validated_replies.append(reply.strip())
            
            if validated_replies:  # 只保留有效回复
                validated_responses[comment_id] = validated_replies
        
        return validated_responses
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行回复评论操作
        
        Args:
            arguments: 工具参数
            
        Returns:
            回复结果
        """
        try:
            # 提取参数
            comments_response = arguments["comments_response"]
            url = arguments["url"]
            auto_optimize = arguments.get("auto_optimize", True)
            phone_number = arguments.get("phone_number", None)  # 获取可选的phone_number参数
            
            # 验证URL
            if "xiaohongshu.com" not in url:
                raise ValueError("不是有效的小红书URL")
            
            # 验证和优化回复内容
            validated_responses = self._validate_replies(comments_response, auto_optimize)
            
            if not validated_responses:
                raise ValueError("没有有效的回复内容")
            
            # 统计信息
            total_comments = len(validated_responses)
            total_replies = sum(len(replies) for replies in validated_responses.values())
            
            # 调用适配器回复评论
            account_info = phone_number or "默认账号"
            self.logger.info(f"使用账号 {account_info} 回复 {total_comments} 条评论")
            result = await self.adapter.reply_comments(validated_responses, url, phone_number)
            
            # 构建成功结果
            success_data = {
                "reply_result": result,
                "statistics": {
                    "total_comments": total_comments,
                    "total_replies": total_replies,
                    "auto_optimized": auto_optimize,
                    "account": account_info
                },
                "validated_responses": validated_responses
            }
            
            message = f"使用账号 {account_info} 成功回复 {total_comments} 条评论，共 {total_replies} 条回复"
            if auto_optimize:
                message += "（已自动优化）"
            
            return ToolResult(
                success=True,
                data=success_data,
                message=message
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message="回复评论过程中发生错误，请检查参数格式和网络连接"
            )
    
    def _format_success_result(self, result: ToolResult) -> str:
        """自定义成功结果格式化"""
        output = f"✅ 评论回复完成！\n\n"
        
        if result.message:
            output += f"📝 {result.message}\n\n"
        
        if result.data:
            data = result.data
            reply_result = data.get("reply_result", {})
            stats = data.get("statistics", {})
            responses = data.get("validated_responses", {})
            
            # 回复统计
            output += f"📊 回复统计:\n"
            output += f"   • 回复评论数: {stats.get('total_comments', 0)}\n"
            output += f"   • 总回复条数: {stats.get('total_replies', 0)}\n"
            output += f"   • 自动优化: {'✅' if stats.get('auto_optimized') else '❌'}\n"
            
            # 回复状态
            if reply_result.get("message") == "success":
                output += f"   • 回复状态: ✅ 成功\n"
            else:
                output += f"   • 回复状态: ❌ {reply_result.get('message', '未知')}\n"
            
            # 回复内容预览
            if responses:
                output += f"\n💬 回复内容预览:\n"
                count = 0
                for comment_id, replies in list(responses.items())[:3]:  # 只显示前3个
                    output += f"   评论 {comment_id}:\n"
                    for reply in replies[:2]:  # 每个评论最多显示2条回复
                        preview = reply[:30] + "..." if len(reply) > 30 else reply
                        output += f"     → {preview}\n"
                    count += 1
                
                if len(responses) > 3:
                    output += f"   ... 还有 {len(responses) - 3} 条评论的回复\n"
        
        if result.execution_time:
            output += f"\n⏱️ 回复耗时: {result.execution_time:.2f}秒"
        
        output += f"\n🕐 完成时间: {result.timestamp}"
        
        return output 