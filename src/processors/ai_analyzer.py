"""
AI 分析器 - 简化版 (GitHub Actions 版本)
支持 OpenAI 兼容格式
"""

from typing import List, Dict
from loguru import logger
import os

class AIAnalyzer:
    """AI 内容分析器"""

    def __init__(self, config: dict):
        self.config = config
        self.client = None
        self.provider = None
        self.categories = config.get("categories", [])
        self.model_config = config.get("ai_summary", {})
        self._init_client()

    def _init_client(self):
        """初始化 AI 客户端"""
        # 优先使用 OpenAI 格式代理
        openai_proxy_key = os.getenv("OPENAI_PROXY_API_KEY")
        openai_proxy_base = os.getenv("OPENAI_PROXY_BASE")

        if openai_proxy_key and openai_proxy_base:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=openai_proxy_key,
                    base_url=openai_proxy_base.rstrip('/')
                )
                self.provider = "openai_proxy"
                self.model = os.getenv("OPENAI_PROXY_MODEL", "gemini-3-flash-preview")
                logger.info(f"✅ OpenAI 代理初始化成功 ({self.model})")
                return
            except Exception as e:
                logger.warning(f"OpenAI 代理初始化失败: {e}")

        # 备用：SiliconFlow
        siliconflow_key = os.getenv("SILICONFLOW_API_KEY")
        if siliconflow_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=siliconflow_key,
                    base_url="https://api.siliconflow.cn/v1"
                )
                self.provider = "siliconflow"
                self.model = os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-72B-Instruct")
                logger.info(f"✅ SiliconFlow 初始化成功 ({self.model})")
                return
            except Exception as e:
                logger.warning(f"SiliconFlow 初始化失败: {e}")

        logger.warning("⚠️ 未找到可用的 AI API")
        self.client = None

    def analyze_batch(self, items: List[Dict]) -> List[Dict]:
        """批量分析内容"""
        if not self.client:
            logger.info("AI 分析未启用，使用简化分析")
            return self._simple_analyze(items)

        logger.info(f"使用 {self.provider} 分析 {len(items)} 条内容...")

        analyzed_items = []
        for i, item in enumerate(items):
            try:
                analyzed_item = self._analyze_single(item)
                analyzed_items.append(analyzed_item)
                if (i + 1) % 10 == 0:
                    logger.info(f"分析进度: {i+1}/{len(items)}")
            except Exception as e:
                logger.error(f"分析失败: {e}")
                # 降级处理
                analyzed_items.append(self._simple_analyze_single(item))

        return analyzed_items

    def _analyze_single(self, item: Dict) -> Dict:
        """分析单条内容"""
        title = item.get('title', '')
        raw_text = item.get('raw_text', title)

        # 分类
        category = self._classify(raw_text)

        # AI 生成摘要
        summary = self._generate_summary(title, raw_text)

        # 提取关键点
        key_points = self._extract_key_points(title, raw_text)

        # 情感分析
        sentiment = self._analyze_sentiment(raw_text)

        # 重要性评分
        importance = self._calculate_importance(item, sentiment)

        item["analysis"] = {
            "category": category,
            "summary": summary,
            "key_points": key_points,
            "sentiment": sentiment,
            "importance": importance,
        }

        return item

    def _generate_summary(self, title: str, content: str) -> str:
        """使用 AI 生成摘要"""
        if not self.client:
            return title[:50] + "..." if len(title) > 50 else title

        try:
            prompt = f"""请用中文总结以下内容，一句话概括（20字以内）：

标题: {title}
内容: {content[:500]}

只返回摘要，不要其他内容。"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )

            summary = response.choices[0].message.content.strip()
            # 清理结果
            summary = summary.replace("摘要:", "").replace("总结:", "").strip()
            if len(summary) > 50:
                summary = summary[:50] + "..."
            return summary

        except Exception as e:
            logger.error(f"摘要生成失败: {e}")
            return title[:50] + "..." if len(title) > 50 else title

    def _extract_key_points(self, title: str, content: str) -> List[str]:
        """提取关键点"""
        if not self.client:
            return []

        try:
            prompt = f"""请从以下内容中提取3个关键要点：

标题: {title}
内容: {content[:800]}

请以列表形式返回，每行一个要点，格式如下：
- 要点1
- 要点2
- 要点3

每个要点不超过15个字。"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )

            result = response.choices[0].message.content.strip()
            key_points = []
            for line in result.split('\n'):
                line = line.strip()
                if line.startswith('- ') or line.startswith('• '):
                    point = line[2:].strip()
                    if point:
                        key_points.append(point)

            return key_points[:3]

        except Exception as e:
            logger.error(f"关键点提取失败: {e}")
            return []

    def _analyze_sentiment(self, text: str) -> Dict:
        """情感分析"""
        text_lower = text.lower()

        # 简单的关键词匹配
        positive_words = ['good', 'great', 'amazing', 'awesome', 'excellent', '好消息', '突破', '成功']
        negative_words = ['bad', 'terrible', 'awful', 'problem', 'issue', 'bug', '坏消息', '失败', '问题']

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return {"sentiment": "positive", "emoji": "😊"}
        elif negative_count > positive_count:
            return {"sentiment": "negative", "emoji": "😟"}
        else:
            return {"sentiment": "neutral", "emoji": "😐"}

    def _classify(self, text: str) -> str:
        """内容分类"""
        text_lower = text.lower()

        for category in self.categories:
            keywords = category.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    return category["name"]

        return self.categories[0]["name"] if self.categories else "AI 相关"

    def _calculate_importance(self, item: Dict, sentiment: Dict) -> int:
        """计算重要性评分"""
        score = 0

        # 基于互动数据
        engagement = item.get("engagement", {})
        reddit_score = engagement.get("score", 0)
        comments = engagement.get("comments", 0)

        if reddit_score > 1000 or comments > 500:
            score += 3
        elif reddit_score > 500 or comments > 200:
            score += 2
        elif reddit_score > 100 or comments > 50:
            score += 1

        # 基于情感
        if sentiment.get("sentiment") == "positive":
            score += 1

        return min(score, 5) or 1

    def _simple_analyze(self, items: List[Dict]) -> List[Dict]:
        """简化分析（无 AI）"""
        for item in items:
            self._simple_analyze_single(item)
        return items

    def _simple_analyze_single(self, item: Dict) -> Dict:
        """单条简化分析"""
        item["analysis"] = {
            "category": self._classify(item.get("raw_text", "")),
            "summary": item.get("title", "")[:50] + "...",
            "key_points": [],
            "sentiment": {"sentiment": "neutral", "emoji": "😐"},
            "importance": 1,
        }
        return item
