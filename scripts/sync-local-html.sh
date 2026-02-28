#!/bin/bash
# 本地 HTML 文件同步到 GitHub
# 用法: ./scripts/sync-local-html.sh

# 配置
SOURCE_DIR="/Users/wanglingwei/Movies/violinvault/SynologyDrive/Clipping/19-ClaudeCode/AI-Hotspots/HTML"
REPO_DIR="/Users/wanglingwei/Documents/github/ai-hotspots-daily"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "========================================"
echo "🔄 同步本地 HTML 到 GitHub"
echo "========================================"
echo ""

# 检查目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}❌ 错误: 源目录不存在${NC}"
    echo "   $SOURCE_DIR"
    exit 1
fi

# 切换到仓库目录
cd "$REPO_DIR" || exit 1

echo "📂 源目录: $SOURCE_DIR"
echo "📂 仓库目录: $REPO_DIR"
echo ""

# 查找 HTML 文件
echo "🔍 查找 HTML 文件..."
HTML_FILES=$(find "$SOURCE_DIR" -name "*.html" -type f)

if [ -z "$HTML_FILES" ]; then
    echo -e "${YELLOW}⚠️  未找到 HTML 文件${NC}"
    exit 0
fi

# 统计文件数量
FILE_COUNT=$(echo "$HTML_FILES" | wc -l | tr -d ' ')
echo "✅ 找到 $FILE_COUNT 个 HTML 文件"
echo ""

# 复制文件
echo "📋 复制文件..."
COPIED=0
while IFS= read -r file; do
    filename=$(basename "$file")

    # 复制到仓库根目录
    cp "$file" "$REPO_DIR/$filename"

    if [ $? -eq 0 ]; then
        echo "   ✅ $filename"
        ((COPIED++))
    else
        echo "   ❌ $filename (复制失败)"
    fi
done <<< "$HTML_FILES"

# 复制子目录（如果有年份文件夹）
if [ -d "$SOURCE_DIR/2026" ]; then
    echo ""
    echo "📂 复制年份文件夹..."
    cp -r "$SOURCE_DIR/"2* "$REPO_DIR/" 2>/dev/null || true
fi

echo ""
echo "📊 复制完成: $COPIED 个文件"
echo ""

# 检查是否有变化
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${GREEN}✅ 没有新文件需要推送${NC}"
    exit 0
fi

# 提交并推送
echo "🚀 推送到 GitHub..."
git add .
git commit -m "📊 同步报告: $(date '+%Y-%m-%d %H:%M:%S')"

if git push origin main; then
    echo ""
    echo -e "${GREEN}✅ 推送成功!${NC}"
    echo ""
    echo "🌐 网站地址:"
    echo "   最新报告: https://violin86318.github.io/ai-hotspots-daily/"
    echo "   历史报告: https://violin86318.github.io/ai-hotspots-daily/reports.html"
else
    echo ""
    echo -e "${RED}❌ 推送失败${NC}"
    exit 1
fi

echo ""
echo "========================================"
