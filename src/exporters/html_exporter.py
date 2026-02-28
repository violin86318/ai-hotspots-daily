"""
HTML 导出器 - Phase 2 增强版
支持 Top 10 精选和 AI 创意展示
"""

from datetime import datetime
from typing import List, Dict
from pathlib import Path
from loguru import logger


class HTMLExporter:
    """HTML 报告导出器"""

    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export(self, items: List[Dict], top10: List[Dict] = None,
               ideas: Dict[str, List[Dict]] = None, date_str: str = None) -> str:
        """
        导出为 HTML 文件

        Args:
            items: 所有内容列表
            top10: Top 10 精选
            ideas: AI 生成的创意 {title: [ideas]}
            date_str: 日期字符串
        """
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')

        logger.info(f"生成 HTML 报告: {date_str}")

        # 按分类组织所有内容
        categorized = self._categorize_items(items)

        # 生成 HTML 内容
        html_content = self._generate_html(
            items, categorized, top10 or [], ideas or {}, date_str
        )

        # 写入文件
        output_file = self.output_dir / f"{date_str}.html"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML 报告已生成: {output_file}")
        return str(output_file)

    def _categorize_items(self, items: List[Dict]) -> Dict:
        """按分类组织内容"""
        categorized = {}
        for item in items:
            analysis = item.get("analysis", {})
            category = analysis.get("category", "AI 相关")
            if category not in categorized:
                categorized[category] = []
            categorized[category].append(item)
        return categorized

    def _get_top10(self, items: List[Dict]) -> List[Dict]:
        """获取 Top 10（按重要性排序）"""
        sorted_items = sorted(
            items,
            key=lambda x: x.get("analysis", {}).get("importance", 0),
            reverse=True
        )
        return sorted_items[:10]

    def _generate_html(self, items: List[Dict], categorized: Dict,
                       top10: List[Dict], ideas: Dict[str, List[Dict]],
                       date_str: str) -> str:
        """生成 HTML 内容"""
        total = len(items)
        reddit_count = sum(1 for item in items if item.get("source") == "reddit")

        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 热点日报 - {date_str}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 40px;
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            font-size: 32px;
            color: #667eea;
            margin-bottom: 16px;
        }}
        .header .meta {{
            color: #666;
            font-size: 14px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .stat-card .number {{
            font-size: 36px;
            font-weight: bold;
            color: #667eea;
        }}
        .stat-card .label {{
            color: #666;
            font-size: 14px;
            margin-top: 8px;
        }}
        .section {{
            background: white;
            padding: 24px;
            border-radius: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .section h2 {{
            color: #667eea;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 2px solid #f0f0f0;
        }}
        /* Top 10 Styles */
        .top10-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }}
        .hotspot-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            border-left: 4px solid #667eea;
            position: relative;
        }}
        .rank-badge {{
            position: absolute;
            top: 16px;
            right: 16px;
            width: 36px;
            height: 36px;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 16px;
        }}
        .card-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 8px;
            padding-right: 40px;
        }}
        .card-meta {{
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }}
        .card-summary {{
            font-size: 14px;
            color: #444;
            margin-bottom: 12px;
        }}
        /* Product Ideas */
        .product-ideas {{
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px dashed #ddd;
        }}
        .idea-card {{
            background: white;
            padding: 16px;
            border-radius: 8px;
            margin-bottom: 12px;
            border-left: 3px solid #764ba2;
        }}
        .idea-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}
        .idea-name {{
            font-weight: 600;
            color: #667eea;
            font-size: 15px;
        }}
        .idea-score {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
        }}
        .idea-body {{
            font-size: 13px;
            color: #555;
        }}
        .idea-body p {{
            margin-bottom: 8px;
        }}
        .idea-body ul {{
            margin-left: 20px;
            margin-bottom: 8px;
        }}
        .idea-body li {{
            margin-bottom: 4px;
        }}
        .idea-body strong {{
            color: #667eea;
        }}
        /* Regular Items */
        .item {{
            padding: 20px;
            border-left: 4px solid #667eea;
            margin-bottom: 16px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .item h3 {{
            font-size: 18px;
            margin-bottom: 12px;
            color: #333;
        }}
        .item .meta {{
            font-size: 13px;
            color: #666;
            margin-bottom: 12px;
        }}
        .item .summary {{
            color: #444;
            margin-bottom: 12px;
        }}
        .item .keypoints {{
            list-style: none;
            padding-left: 0;
        }}
        .item .keypoints li {{
            padding: 4px 0;
            padding-left: 16px;
            position: relative;
        }}
        .item .keypoints li::before {{
            content: "•";
            color: #667eea;
            position: absolute;
            left: 0;
        }}
        .item .link {{
            display: inline-block;
            margin-top: 12px;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-size: 13px;
        }}
        .item .link:hover {{
            background: #5568d3;
        }}
        .sentiment {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 12px;
            margin-left: 8px;
        }}
        .sentiment.positive {{ background: #d4edda; color: #155724; }}
        .sentiment.negative {{ background: #f8d7da; color: #721c24; }}
        .sentiment.neutral {{ background: #e2e3e5; color: #383d41; }}
        .footer {{
            text-align: center;
            padding: 40px;
            color: white;
            opacity: 0.8;
        }}
        @media (max-width: 768px) {{
            .header {{ padding: 24px; }}
            .header h1 {{ font-size: 24px; }}
            .top10-grid {{ grid-template-columns: 1fr; }}
            .item {{ padding: 16px; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 AI 热点日报</h1>
            <div class="meta">
                📅 {date_str} | 🤖 AI 分析 + 创意生成 | 📊 {total} 条热点
            </div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="number">{total}</div>
                <div class="label">总条目</div>
            </div>
            <div class="stat-card">
                <div class="number">{reddit_count}</div>
                <div class="label">Reddit 讨论</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(categorized)}</div>
                <div class="label">分类数</div>
            </div>
            <div class="stat-card">
                <div class="number">{len(top10)}</div>
                <div class="label">Top 10 精选</div>
            </div>
        </div>
"""

        # Top 10 精选区域
        if top10:
            html += """
        <div class="section">
            <h2>🏆 Top 10 精选热点 + AI 产品创意</h2>
            <div class="top10-grid">
"""
            for i, item in enumerate(top10, 1):
                html += self._render_top10_card(item, i, ideas.get(item.get('title', ''), []))
            html += """
            </div>
        </div>
"""

        # 按分类添加所有内容
        for category, cat_items in categorized.items():
            html += f"""
        <div class="section">
            <h2>{category}</h2>
"""
            for item in cat_items:
                html += self._render_regular_item(item)
            html += "        </div>\n"

        # 页脚
        html += f"""
        <div class="footer">
            <p>🤖 AI 热点收集系统 | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>数据来源: Reddit | AI 创意由 Gemini 生成 | Powered by GitHub Actions</p>
        </div>
    </div>
</body>
</html>
"""

        return html

    def _render_top10_card(self, item: Dict, rank: int, ideas: List[Dict]) -> str:
        """渲染 Top 10 卡片"""
        analysis = item.get("analysis", {})
        sentiment = analysis.get("sentiment", {})
        sentiment_class = sentiment.get("sentiment", "neutral")

        html = f"""
            <div class="hotspot-card">
                <div class="rank-badge">{rank}</div>
                <div class="card-title">{item.get('title', '无标题')}</div>
                <div class="card-meta">
                    📌 {item.get('source', 'unknown')} |
                    👍 {item.get('engagement', {}).get('score', 0)} |
                    💬 {item.get('engagement', {}).get('comments', 0)}
                    <span class="sentiment {sentiment_class}">{sentiment.get('emoji', '😐')}</span>
                </div>
                <div class="card-summary">{analysis.get('summary', '')}</div>
"""

        # 添加 AI 创意
        if ideas:
            html += '<div class="product-ideas">\n'
            for idea in ideas:
                html += f"""
                <div class="idea-card">
                    <div class="idea-header">
                        <span class="idea-name">{idea.get('name', '未命名')}</span>
                        <span class="idea-score">{idea.get('score', 80)}分</span>
                    </div>
                    <div class="idea-body">
                        <p><strong>💡 核心价值：</strong>{idea.get('description', '')}</p>
                        <p><strong>🎯 目标用户：</strong>{idea.get('target_users', '')}</p>
                        <p><strong>✨ 核心功能：</strong></p>
                        <ul>
"""
                for feature in idea.get('features', [])[:4]:
                    html += f"                            <li>{feature}</li>\n"
                html += """                        </ul>
                    </div>
                </div>
"""
            html += '                </div>\n'

        html += f"""
                <a href="{item.get('url', '#')}" class="link" target="_blank">查看原文 →</a>
            </div>
"""
        return html

    def _render_regular_item(self, item: Dict) -> str:
        """渲染普通条目"""
        analysis = item.get("analysis", {})
        sentiment = analysis.get("sentiment", {})
        sentiment_class = sentiment.get("sentiment", "neutral")

        html = f"""
            <div class="item">
                <h3>{item.get('title', '无标题')}</h3>
                <div class="meta">
                    📌 {item.get('source', 'unknown')} |
                    👍 {item.get('engagement', {}).get('score', 0)} |
                    💬 {item.get('engagement', {}).get('comments', 0)}
                    <span class="sentiment {sentiment_class}">{sentiment.get('emoji', '😐')} {sentiment_class}</span>
                </div>
                <div class="summary">{analysis.get('summary', '')}</div>
"""
        key_points = analysis.get('key_points', [])
        if key_points:
            html += '<ul class="keypoints">\n'
            for point in key_points:
                html += f'<li>{point}</li>\n'
            html += '</ul>\n'

        html += f"""
                <a href="{item.get('url', '#')}" class="link" target="_blank">查看原文 →</a>
            </div>
"""
        return html
