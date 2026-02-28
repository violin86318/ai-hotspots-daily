#!/bin/bash
# 本地 HTML 文件同步到 GitHub
# 保持原有目录结构：reports/ 和 reports/YYYY/MM/

# 配置
SOURCE_DIR="/Users/wanglingwei/Movies/violinvault/SynologyDrive/Clipping/19-ClaudeCode/AI-Hotspots/HTML"
REPO_DIR="/Users/wanglingwei/Documents/github/ai-hotspots-daily"
REPORTS_DIR="$REPO_DIR/reports"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "🔄 同步本地 HTML 到 GitHub"
echo "========================================"
echo ""

# 检查目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ 错误: 源目录不存在${NC}"
    exit 1
fi

# 切换到仓库目录
cd "$REPO_DIR" || exit 1

# 创建 reports 目录
mkdir -p "$REPORTS_DIR"

echo "📂 源目录: $SOURCE_DIR"
echo "📂 目标目录: $REPORTS_DIR"
echo ""

# 使用 rsync 保持目录结构同步
echo "📋 同步文件..."

# 先清空旧的 reports 目录（保留 .git 等）
find "$REPORTS_DIR" -name "*.html" -delete 2>/dev/null || true

# 使用 rsync 或 cp -R 保持目录结构
if command -v rsync &> /dev/null; then
    rsync -av --delete "$SOURCE_DIR/" "$REPORTS_DIR/" --include="*.html" --include="*/" --exclude="*"
else
    # 如果没有 rsync，使用 cp -R
    cp -R "$SOURCE_DIR/"* "$REPORTS_DIR/" 2>/dev/null || true
fi

# 统计文件数量
FILE_COUNT=$(find "$REPORTS_DIR" -name "*.html" | wc -l)
echo "✅ 同步完成: $FILE_COUNT 个 HTML 文件"
echo ""

# 检查是否有变化
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✅ 没有新文件需要推送${NC}"
    exit 0
fi

# 提交并推送
echo "🚀 推送到 GitHub..."
git add reports/
git commit -m "📊 同步报告: $(date '+%Y-%m-%d %H:%M:%S')"

if git push origin main; then
    echo ""
    echo -e "${GREEN}✅ 推送成功!${NC}"
    echo ""
    echo "🌐 网站地址:"
    echo "   https://violin86318.github.io/ai-hotspots-daily/"
else
    echo ""
    echo -e "${RED}❌ 推送失败${NC}"
    exit 1
fi

echo ""
echo "========================================"
