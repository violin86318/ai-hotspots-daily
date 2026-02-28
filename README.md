# AI Hotspots Daily 🤖

本地生成 HTML 报告，自动同步到 GitHub Pages。

## 工作原理

1. **本地生成**：在 `/Clipping/19-ClaudeCode/AI-Hotspots/` 运行数据收集和报告生成
2. **自动同步**：定时任务检测新 HTML 文件，推送到 GitHub
3. **Pages 部署**：GitHub 自动部署到 Pages

## 本地设置

### 1. 配置定时任务 (cron)

```bash
# 编辑 crontab
crontab -e

# 添加以下内容（每天 9:00 运行）
0 9 * * * /Users/wanglingwei/Documents/github/ai-hotspots-daily/scripts/sync-local-html.sh >> /tmp/ai-hotspots-sync.log 2>&1
```

### 2. 手动同步

```bash
cd /Users/wanglingwei/Documents/github/ai-hotspots-daily
./scripts/sync-local-html.sh
```

## GitHub 配置

### 启用 GitHub Pages

1. 访问: https://github.com/violin86318/ai-hotspots-daily/settings/pages
2. **Source**: GitHub Actions
3. 保存

### 访问地址

- **最新报告**: https://violin86318.github.io/ai-hotspots-daily/
- **历史报告**: https://violin86318.github.io/ai-hotspots-daily/reports.html

## 同步逻辑

- 监控本地 HTML 文件夹: `/Clipping/19-ClaudeCode/AI-Hotspots/HTML/`
- 复制所有 `.html` 文件到 GitHub 仓库
- 推送后自动触发 Pages 部署
- 最新报告自动设为首页

## 项目结构

```
ai-hotspots-daily/
├── .github/workflows/
│   └── deploy-pages.yml      # Pages 自动部署
├── scripts/
│   └── sync-local-html.sh    # 本地同步脚本
├── *.html                     # 同步的 HTML 报告
└── README.md
```

## License

MIT
