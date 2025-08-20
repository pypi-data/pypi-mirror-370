#!/usr/bin/env python3
"""
小红书自动化工具 MCP 服务端
基于 Model Context Protocol 为 AI 助手提供小红书操作能力
支持多账号管理和操作
"""

import asyncio
import logging
from typing import Any, Sequence
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource, Tool, TextContent, ImageContent, EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl
import mcp.types as types

from adapters.xiaohongshu_adapter import XiaohongshuAdapter
from tools.tool_manager import ToolManager
from config import MCPConfig

# 配置日志
logging.basicConfig(
    level=getattr(logging, MCPConfig.LOG_LEVEL),
    format=MCPConfig.LOG_FORMAT
)
logger = logging.getLogger("xiaohongshu-mcp-server")

class XiaohongshuMCPServer:
    """小红书 MCP 服务端主类"""
    
    def __init__(self):
        self.server = Server("xiaohongshu-automation")
        self.adapter = XiaohongshuAdapter(MCPConfig.FASTAPI_BASE_URL)
        self.tool_manager = ToolManager(self.adapter)
        self._setup_handlers()
    
    def _setup_handlers(self):
        """设置 MCP 协议处理器"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            """返回可用工具列表"""
            try:
                tools = self.tool_manager.get_tool_list()
                logger.info(f"返回 {len(tools)} 个工具")
                return tools
            except Exception as e:
                logger.error(f"获取工具列表失败: {str(e)}")
                return []
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
            """处理工具调用"""
            try:
                logger.info(f"收到工具调用请求: {name}")
                result = await self.tool_manager.call_tool(name, arguments)
                return result
                
            except Exception as e:
                logger.error(f"工具调用处理失败 {name}: {str(e)}")
                error_content = f"❌ 工具调用处理失败\n\n🚨 错误: {str(e)}\n🔧 工具: {name}"
                return [TextContent(type="text", text=error_content)]
        
        @self.server.list_resources()
        async def handle_list_resources() -> list[Resource]:
            """返回可用资源列表"""
            return [
                Resource(
                    uri=AnyUrl("xiaohongshu://monitor/status"),
                    name="监控状态",
                    description="获取当前监控任务的状态信息和系统健康报告",
                    mimeType="application/json"
                ),
                Resource(
                    uri=AnyUrl("xiaohongshu://posts/history"),
                    name="发布历史",
                    description="获取历史发布记录和统计分析",
                    mimeType="application/json"
                ),
                Resource(
                    uri=AnyUrl("xiaohongshu://tools/info"),
                    name="工具信息",
                    description="获取所有可用工具的详细信息和使用说明，包括多账号功能",
                    mimeType="application/json"
                ),
                Resource(
                    uri=AnyUrl("xiaohongshu://accounts/status"),
                    name="账号状态",
                    description="获取所有账号的状态信息和管理概览",
                    mimeType="application/json"
                )
            ]
        
        @self.server.read_resource()
        async def handle_read_resource(uri: AnyUrl) -> str:
            """读取资源内容"""
            try:
                uri_str = str(uri)
                
                if uri_str == "xiaohongshu://monitor/status":
                    # 使用监控工具获取详细状态
                    monitor_tool = self.tool_manager.get_tool("xiaohongshu_monitor")
                    result = await monitor_tool.execute({
                        "include_history": True,
                        "include_health": True,
                        "history_limit": 20
                    })
                    
                    if result.success:
                        return f"📊 监控状态报告\n\n{monitor_tool._format_success_result(result)}"
                    else:
                        return f"❌ 获取监控状态失败: {result.error}"
                
                elif uri_str == "xiaohongshu://posts/history":
                    history = await self.adapter.get_publish_history()
                    if history:
                        output = "📝 发布历史记录\n\n"
                        for i, post in enumerate(history[-10:], 1):  # 最近10条
                            status_emoji = "✅" if post.get("status") == "success" else "❌"
                            output += f"{i}. {status_emoji} {post.get('title', 'N/A')}\n"
                            output += f"   时间: {post.get('timestamp', 'N/A')}\n"
                            output += f"   图片: {post.get('pic_count', 0)} 张\n\n"
                        return output
                    else:
                        return "📝 暂无发布历史记录"
                
                elif uri_str == "xiaohongshu://tools/info":
                    tool_info = self.tool_manager.get_tool_info()
                    categories = self.tool_manager.get_tools_by_category()
                    
                    output = "🔧 工具信息总览\n\n"
                    output += f"📊 总计: {len(tool_info)} 个工具\n\n"
                    output += "🎯 多账号支持: 所有业务工具都支持可选的 phone_number 参数\n\n"
                    
                    for category, tools in categories.items():
                        output += f"📁 {category}:\n"
                        for tool_name in tools:
                            info = tool_info[tool_name]
                            output += f"   • {tool_name}: {info['description']}\n"
                        output += "\n"
                    
                    output += "💡 使用说明:\n"
                    output += "   • 不指定 phone_number: 使用当前默认账号\n"
                    output += "   • 指定 phone_number: 使用指定账号进行操作\n"
                    output += "   • 账号管理: 使用 xiaohongshu_account_management 工具\n"
                    
                    return output
                
                elif uri_str == "xiaohongshu://accounts/status":
                    # 获取账号状态信息
                    try:
                        account_tool = self.tool_manager.get_tool("xiaohongshu_account_management")
                        
                        # 获取账号列表
                        list_result = await account_tool.execute({"action": "list"})
                        
                        # 获取所有账号状态
                        status_result = await account_tool.execute({"action": "status"})
                        
                        output = "👥 账号管理状态\n\n"
                        
                        if list_result.success and list_result.data:
                            list_data = list_result.data
                            output += f"📊 总账号数: {list_data.get('总账号数', 0)}\n"
                            output += f"🎯 当前默认账号: {list_data.get('当前默认账号', '未设置')}\n"
                            
                            accounts = list_data.get("账号列表", [])
                            if accounts:
                                output += f"📱 账号列表:\n"
                                for i, account in enumerate(accounts, 1):
                                    output += f"   {i}. {account}\n"
                            output += "\n"
                        
                        if status_result.success and status_result.data:
                            status_data = status_result.data
                            all_status = status_data.get("所有账号状态", {})
                            if all_status:
                                output += f"📈 账号状态详情:\n"
                                for phone, status in all_status.items():
                                    status_emoji = "✅" if status.get("status") == "healthy" else "⚠️"
                                    output += f"   {status_emoji} {phone}: {status.get('status', '未知')}\n"
                            output += "\n"
                        
                        output += "🔧 账号管理操作:\n"
                        output += "   • 添加账号: xiaohongshu_account_management(action='add', phone_number='手机号')\n"
                        output += "   • 切换账号: xiaohongshu_account_management(action='set_current', phone_number='手机号')\n"
                        output += "   • 移除账号: xiaohongshu_account_management(action='remove', phone_number='手机号')\n"
                        
                        return output
                        
                    except Exception as e:
                        return f"❌ 获取账号状态失败: {str(e)}"
                
                else:
                    raise ValueError(f"未知资源: {uri}")
                    
            except Exception as e:
                logger.error(f"资源读取错误 {uri}: {str(e)}")
                return f"❌ 读取资源失败: {str(e)}"
        
        @self.server.list_prompts()
        async def handle_list_prompts() -> list[types.Prompt]:
            """返回可用提示模板列表"""
            return [
                types.Prompt(
                    name="xiaohongshu_content_template",
                    description="生成小红书风格的内容模板，支持多种主题和风格",
                    arguments=[
                        types.PromptArgument(
                            name="topic",
                            description="内容主题（如：美食、旅行、科技、生活等）",
                            required=True
                        ),
                        types.PromptArgument(
                            name="style",
                            description="内容风格（生活、专业、幽默、文艺等）",
                            required=False
                        ),
                        types.PromptArgument(
                            name="length",
                            description="内容长度（短、中、长）",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="xiaohongshu_reply_template",
                    description="生成友好的评论回复模板，支持多种语调和场景",
                    arguments=[
                        types.PromptArgument(
                            name="comment",
                            description="原始评论内容",
                            required=True
                        ),
                        types.PromptArgument(
                            name="tone",
                            description="回复语调（友好、专业、幽默、感谢等）",
                            required=False
                        ),
                        types.PromptArgument(
                            name="context",
                            description="回复场景（咨询、赞美、建议、投诉等）",
                            required=False
                        )
                    ]
                ),
                types.Prompt(
                    name="xiaohongshu_optimization_tips",
                    description="提供小红书内容优化建议和最佳实践",
                    arguments=[
                        types.PromptArgument(
                            name="content_type",
                            description="内容类型（图文、视频、合集等）",
                            required=True
                        ),
                        types.PromptArgument(
                            name="target_audience",
                            description="目标受众（年轻女性、职场人士、学生等）",
                            required=False
                        )
                    ]
                )
            ]
        
        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict[str, str]) -> types.GetPromptResult:
            """获取提示模板内容"""
            try:
                if name == "xiaohongshu_content_template":
                    topic = arguments.get("topic", "")
                    style = arguments.get("style", "生活")
                    length = arguments.get("length", "中")
                    
                    length_guide = {
                        "短": "50-100字，简洁明了",
                        "中": "100-300字，详细描述",
                        "长": "300-500字，深入分析"
                    }
                    
                    template = f"""
# 小红书内容创作模板

## 📝 创作参数
- **主题**: {topic}
- **风格**: {style}
- **长度**: {length}（{length_guide.get(length, '适中')}）

## 🎯 标题创作指南
### 标题公式
1. **数字型**: "5个{topic}小技巧，让你..."
2. **疑问型**: "为什么{topic}这么受欢迎？"
3. **对比型**: "{topic} VS 传统方式，差别太大了！"
4. **情感型**: "爱上{topic}的第N天，我..."

### 标题要素
- ✅ 控制在15-20字
- ✅ 包含关键词"{topic}"
- ✅ 使用适当表情符号
- ✅ 制造悬念或好奇心

## 📖 内容结构模板

### 开头（吸引注意）
- 🔥 热点话题引入
- 💡 个人经历分享
- ❓ 提出引人思考的问题
- 📊 有趣的数据或事实

### 主体（价值输出）
1. **{style}风格特点**:
   - 生活风格: 真实、温暖、贴近日常
   - 专业风格: 权威、详细、有数据支撑
   - 幽默风格: 轻松、有趣、善用梗图
   - 文艺风格: 优美、感性、富有诗意

2. **内容要点**:
   - 🎯 核心观点清晰
   - 📷 配图与文字呼应
   - 💎 提供实用价值
   - 🔗 适当互动引导

### 结尾（行动召唤）
- 💬 提出互动问题
- 👍 引导点赞收藏
- 🔄 鼓励转发分享
- 📝 邀请评论交流

## 🏷️ 话题标签建议
- 主话题: #{topic}
- 相关话题: #日常分享 #生活记录 #实用技巧
- 热门话题: #今日穿搭 #美食探店 #好物推荐

## 📱 小红书特色元素
- 🌟 适量使用表情符号
- 📍 地理位置标记（如适用）
- 🏷️ 相关品牌标记
- 💫 分段排版，提高可读性

## ✨ 优化建议
1. **视觉优化**: 图片清晰、构图美观、色调统一
2. **文字优化**: 语言生动、逻辑清晰、易于理解
3. **互动优化**: 主动回复评论、建立社区感
4. **时机优化**: 选择用户活跃时间发布

请根据以上模板，创作一篇关于"{topic}"的{style}风格小红书内容。
"""
                    
                    return types.GetPromptResult(
                        description=f"小红书{style}风格内容创作模板 - {topic}主题",
                        messages=[
                            types.PromptMessage(
                                role="user",
                                content=types.TextContent(type="text", text=template)
                            )
                        ]
                    )
                
                elif name == "xiaohongshu_reply_template":
                    comment = arguments.get("comment", "")
                    tone = arguments.get("tone", "友好")
                    context = arguments.get("context", "一般互动")
                    
                    template = f"""
# 小红书评论回复模板

## 📝 回复参数
- **原评论**: {comment}
- **回复语调**: {tone}
- **回复场景**: {context}

## 🎯 回复策略

### {tone}语调特点
- **友好**: 温暖亲切，使用"亲"、"宝贝"等称呼
- **专业**: 准确详细，提供专业建议和解答
- **幽默**: 轻松有趣，适当使用网络用语和表情
- **感谢**: 真诚感激，表达对支持的感谢

### {context}场景应对
- **咨询类**: 详细解答，提供实用建议
- **赞美类**: 谦虚感谢，分享更多内容
- **建议类**: 虚心接受，表示会考虑改进
- **投诉类**: 诚恳道歉，积极解决问题

## 💬 回复模板

### 开头语
- 友好型: "谢谢亲的关注！😊"
- 专业型: "感谢您的提问，"
- 幽默型: "哈哈哈，被你发现了！"
- 感谢型: "太感动了，谢谢支持！❤️"

### 主体内容
1. **直接回应**: 针对评论内容给出具体回复
2. **补充信息**: 提供额外的有用信息
3. **个人观点**: 分享自己的看法和经验
4. **互动引导**: 鼓励进一步交流

### 结尾语
- "有什么问题随时问我哦！"
- "希望对你有帮助～"
- "期待你的更多分享！"
- "一起加油！💪"

## 🌟 回复技巧

### 情感表达
- ✅ 使用适当的表情符号
- ✅ 保持真诚和热情
- ✅ 体现个人特色
- ✅ 营造亲近感

### 内容价值
- 💡 提供实用信息
- 🎯 解答具体问题
- 📚 分享相关经验
- 🔗 引导深入交流

### 互动引导
- 💬 提出后续问题
- 👍 鼓励点赞关注
- 🔄 邀请分享经验
- 📝 征求意见建议

## ⚠️ 注意事项
- 避免过于商业化的语言
- 不要忽视负面评论
- 保持回复的及时性
- 注意语言的得体性

请根据以上模板，以{tone}的语调回复评论: "{comment}"
"""
                    
                    return types.GetPromptResult(
                        description=f"{tone}语调的评论回复模板 - {context}场景",
                        messages=[
                            types.PromptMessage(
                                role="user",
                                content=types.TextContent(type="text", text=template)
                            )
                        ]
                    )
                
                elif name == "xiaohongshu_optimization_tips":
                    content_type = arguments.get("content_type", "图文")
                    target_audience = arguments.get("target_audience", "通用")
                    
                    template = f"""
# 小红书内容优化指南

## 🎯 优化目标
- **内容类型**: {content_type}
- **目标受众**: {target_audience}

## 📊 {content_type}内容优化策略

### 视觉优化
1. **图片质量**
   - 分辨率: 建议1080x1080或更高
   - 构图: 遵循三分法则，突出主体
   - 色调: 保持统一的滤镜风格
   - 清晰度: 避免模糊和过度压缩

2. **封面设计**
   - 吸引眼球的视觉元素
   - 清晰的文字标题
   - 与内容高度相关
   - 符合平台审美趋势

### 文案优化
1. **标题策略**
   - 长度控制在15-20字
   - 包含核心关键词
   - 制造悬念或好奇心
   - 使用数字和符号

2. **正文结构**
   - 开头: 快速抓住注意力
   - 主体: 提供有价值的内容
   - 结尾: 引导互动和行动

### 话题标签
1. **主要标签**
   - 与内容高度相关
   - 选择热门但不过度竞争的标签
   - 结合时事热点

2. **辅助标签**
   - 地理位置标签
   - 品牌相关标签
   - 生活方式标签

## 👥 {target_audience}受众特点

### 内容偏好
- 年轻女性: 美妆、穿搭、生活方式
- 职场人士: 效率工具、职业发展
- 学生群体: 学习方法、校园生活
- 宝妈群体: 育儿经验、家庭生活

### 互动习惯
- 活跃时间: 晚上7-10点，周末全天
- 互动方式: 点赞、收藏、评论、分享
- 关注点: 实用性、美观性、趣味性

## 📈 数据优化

### 发布时机
- **最佳时间**: 19:00-22:00
- **最佳日期**: 周三到周日
- **避免时间**: 工作日早晨

### 互动策略
1. **发布后1小时**: 积极回复评论
2. **发布后24小时**: 分析数据表现
3. **发布后一周**: 总结经验教训

### 关键指标
- 点赞率: 目标>5%
- 收藏率: 目标>2%
- 评论率: 目标>1%
- 分享率: 目标>0.5%

## 🚀 增长技巧

### 内容规划
1. **内容日历**: 提前规划一周内容
2. **系列内容**: 建立内容IP和记忆点
3. **热点追踪**: 及时跟进平台热点

### 社区建设
1. **粉丝互动**: 主动回复和互动
2. **合作联动**: 与其他博主互动
3. **用户生成**: 鼓励粉丝创作相关内容

## ⚠️ 避免误区

### 内容误区
- 过度营销和广告
- 内容质量不稳定
- 缺乏个人特色
- 忽视用户反馈

### 运营误区
- 发布频率不规律
- 互动回复不及时
- 数据分析不深入
- 缺乏长期规划

请根据以上指南，优化你的{content_type}内容，以更好地服务{target_audience}受众。
"""
                    
                    return types.GetPromptResult(
                        description=f"{content_type}内容优化指南 - 面向{target_audience}",
                        messages=[
                            types.PromptMessage(
                                role="user",
                                content=types.TextContent(type="text", text=template)
                            )
                        ]
                    )
                
                else:
                    raise ValueError(f"未知提示模板: {name}")
                    
            except Exception as e:
                logger.error(f"提示模板获取错误 {name}: {str(e)}")
                raise
    
    async def run(self):
        """运行 MCP 服务端"""
        # 使用 stdio 传输
        from mcp.server.stdio import stdio_server
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("小红书 MCP 服务端启动成功")
            logger.info(f"已注册 {len(self.tool_manager.tools)} 个工具")
            
            await self.server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=MCPConfig.SERVER_NAME,
                    server_version=MCPConfig.SERVER_VERSION,
                    capabilities=self.server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )

def main():
    """主入口函数"""
    try:
        server = XiaohongshuMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在关闭服务...")
    except Exception as e:
        logger.error(f"服务启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    main() 