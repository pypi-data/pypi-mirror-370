"""
小红书发布工具
实现内容发布功能，包含图片和文字
"""

import re
from typing import Any, Dict, List
from urllib.parse import urlparse
from tools.base_tool import BaseTool, ToolResult

class PublishTool(BaseTool):
    """小红书内容发布工具"""
    
    def __init__(self, adapter):
        super().__init__(
            name="xiaohongshu_publish",
            description="发布内容到小红书，支持多张图片和富文本内容"
        )
        self.adapter = adapter
    
    def get_schema(self) -> Dict[str, Any]:
        """获取工具参数 Schema"""
        return {
            "type": "object",
            "properties": {
                "pic_urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "图片URL列表，支持1-9张图片",
                    "minItems": 1,
                    "maxItems": 9
                },
                "title": {
                    "type": "string",
                    "description": "发布标题，建议20字以内",
                    "minLength": 1,
                    "maxLength": 50
                },
                "content": {
                    "type": "string",
                    "description": "发布内容，支持话题标签和表情符号",
                    "minLength": 1,
                    "maxLength": 1000
                },
                "labels": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "自定义标签列表，如果不提供则使用默认标签 ['#小红书']",
                    "required": False
                },
                "phone_number": {
                    "type": "string",
                    "description": "指定发布账号的手机号（可选），如果不提供则使用当前默认账号",
                    "required": False
                }
            },
            "required": ["pic_urls", "title", "content"]
        }
    
    def _validate_urls(self, urls: List[str]) -> List[str]:
        """
        验证图片URL格式
        
        Args:
            urls: URL列表
            
        Returns:
            验证后的URL列表
            
        Raises:
            ValueError: URL格式无效或其他验证错误
        """
        validated_urls = []
        
        for i, url in enumerate(urls):
            # 检查URL是否为字符串
            if not isinstance(url, str):
                raise ValueError(f"第{i+1}个图片URL不是字符串类型: {type(url).__name__}")
            
            # 检查URL是否为空
            if not url.strip():
                raise ValueError(f"第{i+1}个图片URL为空")
            
            url = url.strip()
            
            # 基本URL格式验证
            try:
                parsed = urlparse(url)
                if not all([parsed.scheme, parsed.netloc]):
                    raise ValueError(f"第{i+1}个图片URL格式无效: {url}")
                    
                # 检查协议是否为http或https
                if parsed.scheme not in ['http', 'https']:
                    raise ValueError(f"第{i+1}个图片URL必须使用http或https协议: {url}")
                    
            except Exception as e:
                if isinstance(e, ValueError):
                    raise e
                else:
                    raise ValueError(f"第{i+1}个图片URL解析失败: {url} - {str(e)}")
            
            # 检查是否为图片URL（简单检查）
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
            url_lower = url.lower()
            
            # 如果URL包含图片扩展名或者是常见图片服务域名
            is_image = (
                any(ext in url_lower for ext in image_extensions) or
                any(domain in url_lower for domain in ['imgur.com', 'cloudinary.com', 'unsplash.com', 'pixabay.com', 'pexels.com', 'images.unsplash.com'])
            )
            
            if not is_image:
                self.logger.warning(f"第{i+1}个URL可能不是图片: {url}")
                # 注意：这里只是警告，不抛出错误，因为有些图片URL可能没有明显的扩展名
            
            validated_urls.append(url)
            self.logger.info(f"第{i+1}个图片URL验证通过: {url}")
        
        self.logger.info(f"所有{len(validated_urls)}个图片URL验证完成")
        return validated_urls
    
    def _validate_content(self, title: str, content: str) -> tuple[str, str]:
        """
        验证和优化内容
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            优化后的标题和内容
        """
        # 标题优化
        title = title.strip()
        if len(title) > 20:
            self.logger.warning("标题超过20字，可能影响展示效果")
        
        # 内容优化
        content = content.strip()
        
        # 检查话题标签格式
        hashtag_pattern = r'#[^#\s]+#?'
        hashtags = re.findall(hashtag_pattern, content)
        if hashtags:
            self.logger.info(f"检测到话题标签: {hashtags}")
        
        # 检查@用户格式
        mention_pattern = r'@[^\s@]+'
        mentions = re.findall(mention_pattern, content)
        if mentions:
            self.logger.info(f"检测到@用户: {mentions}")
        
        return title, content
    
    def _analyze_content_quality(self, title: str, content: str) -> Dict[str, Any]:
        """
        分析内容质量
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            内容质量分析结果
        """
        analysis = {
            "title_length": len(title),
            "content_length": len(content),
            "has_hashtags": bool(re.search(r'#[^#\s]+#?', content)),
            "has_mentions": bool(re.search(r'@[^\s@]+', content)),
            "has_emojis": bool(re.search(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', content)),
            "paragraph_count": len([p for p in content.split('\n') if p.strip()]),
            "quality_score": 0
        }
        
        # 计算质量分数
        score = 0
        
        # 标题长度适中 (5-20字)
        if 5 <= analysis["title_length"] <= 20:
            score += 20
        elif analysis["title_length"] > 0:
            score += 10
        
        # 内容长度适中 (50-500字)
        if 50 <= analysis["content_length"] <= 500:
            score += 30
        elif analysis["content_length"] >= 20:
            score += 15
        
        # 包含话题标签
        if analysis["has_hashtags"]:
            score += 20
        
        # 包含表情符号
        if analysis["has_emojis"]:
            score += 15
        
        # 内容分段
        if analysis["paragraph_count"] > 1:
            score += 15
        
        analysis["quality_score"] = score
        
        return analysis
    
    async def execute(self, arguments: Dict[str, Any]) -> ToolResult:
        """
        执行发布操作
        
        Args:
            arguments: 工具参数
            
        Returns:
            发布结果
        """
        try:
            # 提取参数
            pic_urls = arguments["pic_urls"]
            title = arguments["title"]
            content = arguments["content"]
            labels = arguments.get("labels", None)  # 获取可选的labels参数
            phone_number = arguments.get("phone_number", None)  # 获取可选的phone_number参数

            # 验证 pic_urls 必须是数组
            if not isinstance(pic_urls, list):
                raise ValueError("图片URL 'pic_urls' 必须是一个数组。")
            
            if len(pic_urls) == 0:
                raise ValueError("图片URL数组 'pic_urls' 不能为空，至少需要提供一张图片。")

            # 验证 content 不得包含 # 符号
            if "#" in content:
                raise ValueError("发布内容 'content' 中不得包含 '#' 符号，请将标签内容移至 'labels' 参数中。")

            # 验证 labels 参数
            if labels is not None:
                if not isinstance(labels, list):
                    raise ValueError("自定义标签 'labels' 必须是一个列表。")
                for i, label in enumerate(labels):
                    if not isinstance(label, str):
                        raise ValueError(f"自定义标签列表中的第 {i+1} 个元素 '{label}' 不是一个字符串。")
                    if not label.startswith("#"):
                        raise ValueError(f"自定义标签 '{label}' 必须以 '#' 开头。")
            
            # 验证图片URL
            try:
                validated_urls = self._validate_urls(pic_urls)
            except Exception as e:
                raise ValueError(f"图片URL验证失败: {str(e)}")
            
            # 验证和优化内容
            optimized_title, optimized_content = self._validate_content(title, content)
            
            # 分析内容质量
            quality_analysis = self._analyze_content_quality(optimized_title, optimized_content)
            
            # 调用适配器发布内容
            result = await self.adapter.publish_content(
                pic_urls=validated_urls,
                title=optimized_title,
                content=optimized_content,
                labels=labels,
                phone_number=phone_number
            )
            
            # 构建成功结果
            success_data = {
                "publish_result": result,
                "content_analysis": quality_analysis,
                "optimizations": {
                    "title_optimized": title != optimized_title,
                    "content_optimized": content != optimized_content,
                    "url_count": len(validated_urls),
                    "labels_used": labels or ["#小红书"]  # 显示使用的标签
                }
            }
            
            message = f"成功发布内容到小红书！"
            if quality_analysis["quality_score"] >= 80:
                message += " 内容质量优秀 ⭐⭐⭐"
            elif quality_analysis["quality_score"] >= 60:
                message += " 内容质量良好 ⭐⭐"
            else:
                message += " 建议优化内容质量 ⭐"
            
            return ToolResult(
                success=True,
                data=success_data,
                message=message
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e),
                message="发布过程中发生错误，请检查网络连接和参数设置"
            )
    
    def _format_success_result(self, result: ToolResult) -> str:
        """自定义成功结果格式化"""
        output = f"✅ 小红书内容发布成功！\n\n"
        
        if result.message:
            output += f"📝 {result.message}\n\n"
        
        if result.data:
            data = result.data
            publish_result = data.get("publish_result", {})
            analysis = data.get("content_analysis", {})
            optimizations = data.get("optimizations", {})
            
            # 发布结果
            if publish_result.get("status") == "success":
                output += "🎉 发布状态: 成功\n"
                if publish_result.get("urls"):
                    output += f"🔗 发布链接: {', '.join(publish_result['urls'])}\n"
            
            output += "\n📊 内容分析:\n"
            output += f"   • 标题长度: {analysis.get('title_length', 0)} 字\n"
            output += f"   • 内容长度: {analysis.get('content_length', 0)} 字\n"
            output += f"   • 质量评分: {analysis.get('quality_score', 0)}/100\n"
            output += f"   • 话题标签: {'✅' if analysis.get('has_hashtags') else '❌'}\n"
            output += f"   • 表情符号: {'✅' if analysis.get('has_emojis') else '❌'}\n"
            output += f"   • 内容分段: {'✅' if analysis.get('paragraph_count', 0) > 1 else '❌'}\n"
            
            if optimizations.get("url_count"):
                output += f"\n🖼️ 图片数量: {optimizations['url_count']} 张\n"
            
            if optimizations.get("labels_used"):
                output += f"🏷️ 使用标签: {', '.join(optimizations['labels_used'])}\n"
        
        if result.execution_time:
            output += f"\n⏱️ 发布耗时: {result.execution_time:.2f}秒"
        
        output += f"\n🕐 完成时间: {result.timestamp}"
        
        return output 