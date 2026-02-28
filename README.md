# AI Hotspots Daily 🤖

每日自动收集 Reddit AI 热点，生成可视化报告，并部署到 GitHub Pages。

## 功能特点

- 🔥 **自动收集**：每天自动从 Reddit AI 相关社区收集热门帖子
- 🤖 **AI 分析**：使用 Gemini 模型自动生成中文摘要和关键点
- 📊 **可视化报告**：生成精美的 HTML 报告
- 🌐 **GitHub Pages**：自动部署到 GitHub Pages，可在线访问
- ⏰ **定时运行**：每天 UTC 07:00（北京时间 15:00）自动运行

## 数据来源

- Reddit: r/MachineLearning, r/LocalLLaMA, r/OpenAI, r/ClaudeAI 等

## 技术栈

- Python 3.11
- GitHub Actions
- GitHub Pages
- OpenAI / SiliconFlow API

## 部署指南

### 1. Fork / 创建仓库

将此代码推送到你的 GitHub 仓库。

### 2. 配置 Secrets

在 GitHub 仓库设置中添加以下 Secrets：

| Secret | 说明 | 必需 |
|--------|------|------|
| `OPENAI_PROXY_API_KEY` | API 密钥 | ✅ |
| `OPENAI_PROXY_BASE` | API Base URL | ✅ |
| `OPENAI_PROXY_MODEL` | 模型名称 (如 gemini-3-flash-preview) | ✅ |
| `SILICONFLOW_API_KEY` | 备用 API 密钥 | ❌ |

### 3. 启用 GitHub Pages

1. 进入仓库 Settings → Pages
2. Source: GitHub Actions
3. 保存

### 4. 手动测试

进入 Actions → AI Hotspots Daily Report → Run workflow

### 5. 访问报告

- 最新报告: `https://<username>.github.io/ai-hotspots-daily/`
- 历史报告: `https://<username>.github.io/ai-hotspots-daily/reports.html`

## 本地测试

```bash
# 克隆仓库
git clone https://github.com/<username>/ai-hotspots-daily.git
cd ai-hotspots-daily

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 设置环境变量
export OPENAI_PROXY_API_KEY="your-key"
export OPENAI_PROXY_BASE="https://your-proxy.com/v1"
export OPENAI_PROXY_MODEL="gemini-3-flash-preview"

# 运行收集
python scripts/run_collection.py
```

## 项目结构

```
ai-hotspots-daily/
├── .github/workflows/       # GitHub Actions 配置
├── config/                  # 配置文件
├── src/                     # 源代码
│   ├── collectors/          # 数据收集器
│   ├── processors/          # AI 分析器
│   └── exporters/           # 导出器
├── scripts/                 # 入口脚本
└── requirements.txt         # 依赖

```

## License

MIT
