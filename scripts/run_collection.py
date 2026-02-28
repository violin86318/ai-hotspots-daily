#!/usr/bin/env python3
"""
GitHub Actions 数据收集入口 - Phase 2 增强版
支持 Top 10 精选和 AI 创意生成
"""
import sys
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import yaml
from loguru import logger
from datetime import datetime
from collectors.reddit_collector import RedditCollector
from processors.ai_analyzer import AIAnalyzer
from processors.ai_idea_generator import AIIdeaGenerator
from exporters.html_exporter import HTMLExporter


def get_top10(items):
    """获取 Top 10（按互动数据综合排序）"""
    def score(item):
        engagement = item.get("engagement", {})
        return (
            engagement.get("score", 0) +
            engagement.get("comments", 0) * 2
        )

    sorted_items = sorted(items, key=score, reverse=True)
    return sorted_items[:10]


def main():
    logger.info("=" * 60)
    logger.info("🔥 AI Hotspots Daily - Phase 2")
    logger.info("AI 分析 + Top 10 精选 + 产品创意生成")
    logger.info("=" * 60)

    # 加载配置
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 设置输出目录
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(exist_ok=True)

    # ========== 1. 数据收集 ==========
    logger.info("\n[1/4] 数据收集...")
    reddit_config = config.get("sources", {}).get("reddit", {})
    reddit_collector = RedditCollector(reddit_config)
    items = reddit_collector.collect(lookback_hours=24)

    if not items:
        logger.warning("⚠️ 未收集到任何数据")
        return

    logger.info(f"✅ 收集到 {len(items)} 条数据")

    # ========== 2. AI 分析 ==========
    logger.info("\n[2/4] AI 分析...")
    analyzer = AIAnalyzer(config)
    analyzed_items = analyzer.analyze_batch(items)
    logger.info(f"✅ 分析完成: {len(analyzed_items)} 条")

    # ========== 3. Top 10 精选 + 创意生成 ==========
    logger.info("\n[3/4] Top 10 精选 + AI 创意生成...")

    # 获取 Top 10
    top10 = get_top10(analyzed_items)
    logger.info(f"✅ Top 10 精选完成")

    # 生成创意
    idea_generator = AIIdeaGenerator(config)
    ideas = idea_generator.generate_for_top10(top10)
    logger.info(f"✅ 创意生成完成: {sum(len(v) for v in ideas.values())} 个创意")

    # ========== 4. 生成 HTML 报告 ==========
    logger.info("\n[4/4] 生成 HTML 报告...")
    exporter = HTMLExporter(output_dir=str(output_dir))
    date_str = datetime.now().strftime('%Y-%m-%d')
    html_path = exporter.export(
        items=analyzed_items,
        top10=top10,
        ideas=ideas,
        date_str=date_str
    )
    logger.info(f"✅ HTML 报告: {html_path}")

    logger.info("\n" + "=" * 60)
    logger.info("✅ Phase 2 任务完成!")
    logger.info(f"📊 数据: {len(analyzed_items)} 条")
    logger.info(f"🏆 Top 10: 精选完成")
    logger.info(f"🎨 创意: {sum(len(v) for v in ideas.values())} 个")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
