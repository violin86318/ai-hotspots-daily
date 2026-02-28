#!/bin/bash
# 设置定时任务 - 每天上午 9:00 同步

echo "🕘 设置定时任务..."
echo ""

# 创建 cron 任务 (每天 9:00)
CRON_JOB="0 9 * * * /Users/wanglingwei/Documents/github/ai-hotspots-daily/scripts/sync-local-html.sh >> /tmp/ai-hotspots-sync.log 2>&1"

# 检查是否已存在
if crontab -l 2>/dev/null | grep -q "sync-local-html.sh"; then
    echo "✅ 定时任务已存在"
else
    # 添加新任务
    (crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -
    echo "✅ 定时任务已添加: 每天 9:00"
fi

echo ""
echo "📋 当前定时任务:"
crontab -l | grep -A1 -B1 "ai-hotspots" || echo "   无"
echo ""
echo "📝 日志文件: /tmp/ai-hotspots-sync.log"
echo ""
echo "🔗 手动运行测试:"
echo "   /Users/wanglingwei/Documents/github/ai-hotspots-daily/scripts/sync-local-html.sh"
