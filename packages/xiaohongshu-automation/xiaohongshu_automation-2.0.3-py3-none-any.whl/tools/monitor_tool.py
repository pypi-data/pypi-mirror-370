"""
小红书监控工具
实现系统监控和状态管理功能
"""

from typing import Any, Dict, List
from datetime import datetime, timedelta
from tools.base_tool import BaseTool, ToolResult

class MonitorTool(BaseTool):
    """小红书监控状态工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_monitor",
            description="获取小红书自动化系统的监控状态和运行统计"
        )
        self.adapter = adapter
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数 Schema"""
        return {
            "type": "object",
            "properties": {
                "include_history": {
                    "type": "boolean",
                    "description": "是否包含发布历史（默认true）",
                    "default": True
                },
                "include_health": {
                    "type": "boolean",
                    "description": "是否包含健康检查（默认true）",
                    "default": True
                },
                "history_limit": {
                    "type": "integer",
                    "description": "历史记录限制数量（默认10）",
                    "default": 10,
                    "minimum": 1,
                    "maximum": 50
                }
            },
            "required": []
        }
    
    def _analyze_publish_history(self, history: List[Dict[str, Any]], limit: int = 10) -> Dict[str, Any]:
        """
        分析发布历史
        
        Args:
            history: 发布历史记录
            limit: 分析记录数量限制
            
        Returns:
            历史分析结果
        """
        if not history:
            return {
                "total_posts": 0,
                "success_rate": 0,
                "recent_activity": "无发布记录",
                "trends": {}
            }
        
        # 限制分析的记录数量
        recent_history = history[-limit:] if len(history) > limit else history
        
        # 基本统计
        total_posts = len(recent_history)
        successful_posts = sum(1 for post in recent_history if post.get("status") == "success")
        success_rate = (successful_posts / total_posts * 100) if total_posts > 0 else 0
        
        # 时间分析
        now = datetime.now()
        recent_posts = []
        
        for post in recent_history:
            try:
                post_time = datetime.fromisoformat(post.get("timestamp", ""))
                time_diff = now - post_time
                
                if time_diff.days == 0:
                    recent_posts.append("今天")
                elif time_diff.days == 1:
                    recent_posts.append("昨天")
                elif time_diff.days <= 7:
                    recent_posts.append("本周")
                else:
                    recent_posts.append("更早")
            except:
                continue
        
        # 活动趋势
        activity_counts = {}
        for period in recent_posts:
            activity_counts[period] = activity_counts.get(period, 0) + 1
        
        # 最近活动描述
        if activity_counts.get("今天", 0) > 0:
            recent_activity = f"今天发布了 {activity_counts['今天']} 条内容"
        elif activity_counts.get("昨天", 0) > 0:
            recent_activity = f"昨天发布了 {activity_counts['昨天']} 条内容"
        elif activity_counts.get("本周", 0) > 0:
            recent_activity = f"本周发布了 {activity_counts['本周']} 条内容"
        else:
            recent_activity = "最近无发布活动"
        
        return {
            "total_posts": total_posts,
            "successful_posts": successful_posts,
            "success_rate": round(success_rate, 1),
            "recent_activity": recent_activity,
            "trends": activity_counts,
            "latest_post": recent_history[-1] if recent_history else None
        }
    
    def _get_system_health_score(self, monitor_status: Dict[str, Any], history_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        计算系统健康评分
        
        Args:
            monitor_status: 监控状态
            history_analysis: 历史分析
            
        Returns:
            健康评分结果
        """
        score = 0
        max_score = 100
        issues = []
        
        # 服务运行状态 (30分)
        if monitor_status.get("is_running", False):
            score += 30
        else:
            issues.append("FastAPI 服务未运行")
        
        # 发布成功率 (25分)
        success_rate = history_analysis.get("success_rate", 0)
        if success_rate >= 90:
            score += 25
        elif success_rate >= 70:
            score += 20
        elif success_rate >= 50:
            score += 15
        else:
            if history_analysis.get("total_posts", 0) > 0:
                issues.append(f"发布成功率较低 ({success_rate}%)")
        
        # 错误率 (20分)
        error_count = monitor_status.get("error_count", 0)
        success_count = monitor_status.get("success_count", 0)
        total_operations = error_count + success_count
        
        if total_operations > 0:
            error_rate = error_count / total_operations * 100
            if error_rate <= 5:
                score += 20
            elif error_rate <= 15:
                score += 15
            elif error_rate <= 30:
                score += 10
            else:
                issues.append(f"错误率较高 ({error_rate:.1f}%)")
        else:
            score += 10  # 没有操作记录，给予部分分数
        
        # 最近活动 (15分)
        recent_activity = history_analysis.get("recent_activity", "")
        if "今天" in recent_activity:
            score += 15
        elif "昨天" in recent_activity or "本周" in recent_activity:
            score += 10
        else:
            issues.append("最近无发布活动")
        
        # 系统稳定性 (10分)
        try:
            last_check = monitor_status.get("last_check", "")
            if last_check:
                last_check_time = datetime.fromisoformat(last_check)
                time_since_check = datetime.now() - last_check_time
                
                if time_since_check.total_seconds() < 300:  # 5分钟内
                    score += 10
                elif time_since_check.total_seconds() < 1800:  # 30分钟内
                    score += 5
                else:
                    issues.append("系统检查时间过久")
        except:
            issues.append("无法获取系统检查时间")
        
        # 健康等级
        if score >= 90:
            health_level = "优秀"
            health_emoji = "🟢"
        elif score >= 70:
            health_level = "良好"
            health_emoji = "🟡"
        elif score >= 50:
            health_level = "一般"
            health_emoji = "🟠"
        else:
            health_level = "需要关注"
            health_emoji = "🔴"
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": round(score / max_score * 100, 1),
            "level": health_level,
            "emoji": health_emoji,
            "issues": issues
        }
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行监控状态检查
        
        Args:
            arguments: 工具参数
            
        Returns:
            监控结果
        """
        try:
            # 提取参数
            include_history = arguments.get("include_history", True)
            include_health = arguments.get("include_health", True)
            history_limit = arguments.get("history_limit", 10)
            
            # 获取监控状态
            monitor_status = await self.adapter.get_monitor_status()
            
            # 构建结果数据
            result_data = {
                "monitor_status": monitor_status,
                "check_time": datetime.now().isoformat()
            }
            
            # 获取发布历史
            history_analysis = {}
            if include_history:
                history = await self.adapter.get_publish_history()
                history_analysis = self._analyze_publish_history(history, history_limit)
                result_data["history_analysis"] = history_analysis
                result_data["publish_history"] = history[-history_limit:] if history else []
            
            # 健康检查
            health_score = {}
            if include_health:
                # 执行健康检查
                is_healthy = await self.adapter.health_check()
                result_data["health_check"] = {
                    "is_healthy": is_healthy,
                    "check_time": datetime.now().isoformat()
                }
                
                # 计算健康评分
                health_score = self._get_system_health_score(monitor_status, history_analysis)
                result_data["health_score"] = health_score
            
            # 构建消息
            if monitor_status.get("is_running", False):
                base_message = "系统运行正常"
            else:
                base_message = "系统状态异常"
            
            if health_score:
                message = f"{base_message} - 健康评分: {health_score['percentage']}% ({health_score['level']})"
            else:
                message = base_message
            
            return ToolResult(
                success=True,
                data=result_data,
                message=message
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message="获取监控状态时发生错误"
            )
    
    def _format_success_result(self, result: ToolResult) -> str:
        """自定义成功结果格式化"""
        output = f"✅ 系统监控报告\n\n"
        
        if result.message:
            output += f"📝 {result.message}\n\n"
        
        if result.data:
            data = result.data
            monitor_status = data.get("monitor_status", {})
            health_score = data.get("health_score", {})
            history_analysis = data.get("history_analysis", {})
            health_check = data.get("health_check", {})
            
            # 系统状态
            output += f"🖥️ 系统状态:\n"
            output += f"   • 服务运行: {'✅ 正常' if monitor_status.get('is_running') else '❌ 异常'}\n"
            output += f"   • 最后检查: {monitor_status.get('last_check', 'N/A')}\n"
            output += f"   • 成功次数: {monitor_status.get('success_count', 0)}\n"
            output += f"   • 错误次数: {monitor_status.get('error_count', 0)}\n"
            
            # 健康评分
            if health_score:
                output += f"\n{health_score.get('emoji', '📊')} 健康评分:\n"
                output += f"   • 总分: {health_score.get('score', 0)}/{health_score.get('max_score', 100)} ({health_score.get('percentage', 0)}%)\n"
                output += f"   • 等级: {health_score.get('level', 'N/A')}\n"
                
                issues = health_score.get('issues', [])
                if issues:
                    output += f"   • 问题: {', '.join(issues[:3])}\n"
                    if len(issues) > 3:
                        output += f"     ... 还有 {len(issues) - 3} 个问题\n"
            
            # 健康检查
            if health_check:
                output += f"\n🔍 连接检查:\n"
                output += f"   • FastAPI 连接: {'✅ 正常' if health_check.get('is_healthy') else '❌ 失败'}\n"
                output += f"   • 检查时间: {health_check.get('check_time', 'N/A')}\n"
            
            # 发布历史分析
            if history_analysis:
                output += f"\n📊 发布统计:\n"
                output += f"   • 总发布数: {history_analysis.get('total_posts', 0)}\n"
                output += f"   • 成功发布: {history_analysis.get('successful_posts', 0)}\n"
                output += f"   • 成功率: {history_analysis.get('success_rate', 0)}%\n"
                output += f"   • 最近活动: {history_analysis.get('recent_activity', 'N/A')}\n"
                
                # 活动趋势
                trends = history_analysis.get('trends', {})
                if trends:
                    trend_items = [f"{k}: {v}" for k, v in trends.items()]
                    output += f"   • 活动分布: {', '.join(trend_items)}\n"
            
            # 最新发布
            publish_history = data.get("publish_history", [])
            if publish_history:
                latest = publish_history[-1]
                output += f"\n📝 最新发布:\n"
                output += f"   • 标题: {latest.get('title', 'N/A')}\n"
                output += f"   • 状态: {latest.get('status', 'N/A')}\n"
                output += f"   • 时间: {latest.get('timestamp', 'N/A')}\n"
        
        if result.execution_time:
            output += f"\n⏱️ 检查耗时: {result.execution_time:.2f}秒"
        
        output += f"\n🕐 报告时间: {result.timestamp}"
        
        return output