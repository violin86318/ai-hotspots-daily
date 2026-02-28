"""
AI 产品创意生成器
为热门 AI 话题生成产品创意
"""

import json
import os
from typing import List, Dict
from loguru import logger


class AIIdeaGenerator:
    """AI 创意生成器"""

    def __init__(self, config: dict = None):
        self.config = config or {}
        self.model = os.getenv("OPENAI_PROXY_MODEL", "gemini-3-flash-preview")
        self.max_ideas = 1  # 每个热点生成 1 个高质量创意
        self.client = None
        self.provider = None
        self._init_client()

    def _init_client(self):
        """初始化 AI 客户端"""
        # 优先 OpenAI 代理
        openai_key = os.getenv("OPENAI_PROXY_API_KEY")
        openai_base = os.getenv("OPENAI_PROXY_BASE")

        if openai_key and openai_base:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=openai_key,
                    base_url=openai_base.rstrip('/')
                )
                self.provider = "openai_proxy"
                logger.info(f"✅ 创意生成器初始化成功 ({self.model})")
                return
            except Exception as e:
                logger.warning(f"OpenAI 代理失败: {e}")

        # 备用 SiliconFlow
        sf_key = os.getenv("SILICONFLOW_API_KEY")
        if sf_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(
                    api_key=sf_key,
                    base_url="https://api.siliconflow.cn/v1"
                )
                self.provider = "siliconflow"
                self.model = os.getenv("SILICONFLOW_MODEL", "Qwen/Qwen2.5-72B-Instruct")
                logger.info(f"✅ 创意生成器初始化成功 (SiliconFlow)")
                return
            except Exception as e:
                logger.warning(f"SiliconFlow 失败: {e}")

        logger.warning("⚠️ 创意生成器未找到可用 API")

    def generate_for_hotspot(self, hotspot: Dict) -> List[Dict]:
        """为单个热点生成创意"""
        if not self.client:
            return self._fallback_ideas(hotspot)

        try:
            title = hotspot.get('title', '')
            summary = hotspot.get('analysis', {}).get('summary', '')
            category = hotspot.get('analysis', {}).get('category', 'AI 相关')

            prompt = f"""基于以下 AI 热点，生成 {self.max_ideas} 个创新的产品创意：

热点标题: {title}
热点分类: {category}
热点摘要: {summary}

要求：
1. 每个创意独特且有差异化
2. 包含具体的产品名称（中英文结合，有创意）
3. 明确目标用户群体
4. 列出3-4个核心功能特性
5. 用一句话描述核心价值

输出 JSON 格式：
{{
  "ideas": [
    {{
      "name": "产品名称（中英文）",
      "description": "一句话核心价值",
      "features": ["功能1", "功能2", "功能3"],
      "target_users": "目标用户描述",
      "score": 85
    }}
  ]
}}

只返回 JSON，不要有其他内容。"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=800,
                temperature=0.8
            )

            content = response.choices[0].message.content.strip()

            # 清理可能的 markdown 标记
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            content = content.strip()

            data = json.loads(content)
            ideas = data.get('ideas', [])

            # 格式化
            formatted = []
            for idea in ideas[:self.max_ideas]:
                formatted.append({
                    'name': idea.get('name', '未命名'),
                    'description': idea.get('description', ''),
                    'features': idea.get('features', [])[:4],
                    'target_users': idea.get('target_users', ''),
                    'score': idea.get('score', 80)
                })

            logger.info(f"✅ 生成 {len(formatted)} 个创意: {title[:40]}...")
            return formatted

        except Exception as e:
            logger.error(f"创意生成失败: {e}")
            return self._fallback_ideas(hotspot)

    def generate_for_top10(self, hotspots: List[Dict]) -> Dict[str, List[Dict]]:
        """为 Top 10 热点批量生成创意"""
        logger.info(f"\n🎨 为 Top {len(hotspots)} 热点生成创意...")

        results = {}
        for i, hotspot in enumerate(hotspots, 1):
            logger.info(f"[{i}/{len(hotspots)}] {hotspot.get('title', '')[:50]}...")
            ideas = self.generate_for_hotspot(hotspot)
            results[hotspot.get('title', '')] = ideas

        return results

    def _fallback_ideas(self, hotspot: Dict) -> List[Dict]:
        """备用创意（无 AI 时）"""
        title = hotspot.get('title', '')
        category = hotspot.get('analysis', {}).get('category', 'AI 相关')

        return [
            {
                'name': f'{category}分析工具',
                'description': f'基于该热点的数据分析平台',
                'features': ['数据监控', '趋势分析', '报告生成', 'API 接口'],
                'target_users': 'AI 研究人员、产品经理',
                'score': 75
            },
            {
                'name': f'{category}通知服务',
                'description': f'实时推送相关动态',
                'features': ['实时推送', '个性化订阅', '多平台支持', '智能过滤'],
                'target_users': '关注该领域的专业人士',
                'score': 70
            }
        ]
