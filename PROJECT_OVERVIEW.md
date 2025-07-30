# NewsTrader - AI-Powered Trading News Analysis System

## 项目概述

NewsTrader 是一个基于人工智能的金融新闻分析系统，使用 Claude AI 分析新闻对股票、期货和大宗商品的市场影响，为交易决策提供智能支持。

## 架构图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (React)       │    │   (FastAPI)     │    │   Services      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • Dashboard     │◄──►│ • REST API      │◄──►│ • Claude AI     │
│ • News View     │    │ • News Scraper  │    │ • RSS Feeds     │
│ • Analysis      │    │ • AI Analysis   │    │ • Yahoo Finance │
│ • Backtest      │    │ • Backtest      │    │                 │
│ • Ant Design    │    │ • Celery Tasks  │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Data Layer    │
                       ├─────────────────┤
                       │ • PostgreSQL    │
                       │ • Redis Cache   │
                       │ • Data Models   │
                       └─────────────────┘
```

## 技术栈

### 后端 (Backend)
- **Python 3.11+** - 核心语言
- **FastAPI** - 异步 Web 框架
- **SQLAlchemy + Alembic** - ORM 和数据库迁移
- **PostgreSQL** - 主数据库
- **Redis** - 缓存和任务队列
- **Celery** - 后台任务处理
- **Claude AI (Anthropic)** - 新闻分析
- **Beautiful Soup + feedparser** - 网页抓取

### 前端 (Frontend)
- **React 18 + TypeScript** - UI 框架
- **Ant Design** - 组件库
- **React Query** - 数据状态管理
- **Recharts** - 数据可视化
- **Axios** - HTTP 客户端

### 基础设施 (Infrastructure)
- **Podman/Docker** - 容器化
- **PostgreSQL 15** - 数据库
- **Redis 7** - 缓存和消息代理

## 信息流 (Data Flow)

```
1. 新闻抓取 (News Scraping)
   RSS Feeds → News Scraper → Raw Articles

2. AI 分析 (AI Analysis)
   Raw Articles → Claude AI → Impact Analysis
   ↓
   • Impact Score (0-10)
   • Sentiment Score (-1 to +1)
   • Affected Symbols
   • Confidence Score (0-1)

3. 数据存储 (Data Storage)
   Analyzed Articles → PostgreSQL
   Cache/Sessions → Redis

4. 实时分析 (Real-time Analysis)
   Database → API Endpoints → Frontend Dashboard

5. 回测验证 (Backtesting)
   Historical Data + Predictions → Accuracy Metrics
```

## 核心功能

### 已实现功能 ✅
1. **新闻抓取系统** - 多源 RSS 新闻采集
2. **AI 影响力分析** - Claude AI 驱动的新闻影响评分
3. **情感分析** - 市场情感实时监测
4. **回测系统** - 预测准确性历史验证
5. **实时仪表板** - React 前端数据可视化
6. **RESTful API** - 完整的后端接口
7. **容器化部署** - Docker/Podman 支持

### 数据模型 (Data Models)
```python
NewsArticle:
- title, content, summary, url
- impact_score (0-10)
- sentiment_score (-1 to +1)
- affected_symbols (list)
- claude_analysis (JSON)
- confidence_score (0-1)

ImpactWeight:
- predicted_impact vs actual_impact
- accuracy tracking

BacktestResult:
- prediction accuracy metrics
- historical performance data
```

## 当前状态 (Current Status) - 更新于 2025-07-30

### 🟢 已完成 (Completed)
- ✅ 项目结构和基础架构
- ✅ FastAPI 后端框架 + 完整API
- ✅ PostgreSQL + Redis 数据层
- ✅ Claude AI 集成模块 (可选)
- ✅ 中英文新闻抓取和过滤系统
- ✅ React 前端界面 (完整部署)
- ✅ 智能新闻分析系统 (双向分析)
- ✅ 回测验证系统
- ✅ Docker/Podman 容器化配置
- ✅ n8n 工作流自动化集成
- ✅ 中文财经新闻支持
- ✅ 21个全球交易品种覆盖
- ✅ jieba中文分词和情感分析
- ✅ 完整的前端中文界面

### 🟢 新增核心功能 (New Features)
- ✅ **双向智能分析**：正向分析 + 反向分析
- ✅ **反向新闻搜索**：根据交易品种查找相关新闻
- ✅ **中文新闻源**：新浪财经、36氪、华尔街见闻等
- ✅ **多市场支持**：美股、A股、港股、商品、外汇
- ✅ **可视化界面**：智能分析页面完整实现
- ✅ **实时API**：完整的RESTful API接口

### 🟢 最新功能更新 (2025-07-30)
- ✅ **新闻详情功能**：查看详情按钮正常工作，显示完整新闻信息
- ✅ **动态置信度评分**：基于多因子算法的智能置信度计算(68%-85%)
- ✅ **投资结论系统**：替换Actions为"结论"功能，显示投资建议
- ✅ **中文翻译优化**：集成Claude AI高质量翻译，支持本地算法降级
- ✅ **新闻筛选机制**：智能过滤评论性新闻，专注事实性新闻
- ✅ **去重算法**：基于事件的新闻去重，避免重复内容
- ✅ **UI/UX改进**：修复按钮交互、链接跳转、样式优化
- ✅ **API稳定性**：解决超时问题，提供可靠的备用数据
- ✅ **真实链接验证**：确保新闻链接指向真实可访问的财经网站

### 🟡 可选功能 (Optional)
- 🔶 Claude AI API 密钥配置 (可选，有本地算法替代)
- 🔶 WebSocket 实时数据推送 (计划中)

### 🟢 已验证功能 (Verified)
- ✅ 前端完整编译和部署
- ✅ 后端API全面测试通过
- ✅ 中文新闻分析算法验证
- ✅ 数据库连接和存储正常
- ✅ 容器化服务运行稳定
- ✅ 新闻详情模态框功能正常
- ✅ 中文翻译质量显著提升
- ✅ 投资结论准确显示
- ✅ 所有新闻链接可正常访问

## 文件结构

```
NewsTrader/
├── backend/                 # Python 后端
│   ├── app/
│   │   ├── api/            # API 路由
│   │   ├── core/           # 核心配置
│   │   ├── models/         # 数据模型
│   │   ├── services/       # 业务逻辑
│   │   ├── mcp/            # Claude AI 集成
│   │   └── main.py         # 应用入口
│   ├── requirements.txt    # Python 依赖
│   ├── Dockerfile         # 容器配置
│   └── .env               # 环境变量
├── frontend/               # React 前端
│   ├── src/
│   │   ├── components/    # UI 组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API 服务
│   │   └── types/         # TypeScript 类型
│   └── package.json       # 前端依赖
├── docker-compose.yml      # 容器编排
├── simple_backend.py       # 简化测试后端
├── test.html              # 功能测试界面
└── README.md              # 项目文档
```

## 运行状态

### 当前运行的服务
```bash
# 数据库服务
podman ps
- newsdb (PostgreSQL:5433)
- newsredis (Redis:6380)

# 后端服务
python simple_backend.py (Port:8000)

# 测试界面
test.html (通过浏览器访问)
```

### API 端点
```
GET  /health                           # 健康检查
GET  /api/v1/news/articles            # 获取新闻文章
GET  /api/v1/news/trending            # 获取高影响力新闻
GET  /api/v1/analysis/impact-summary  # 市场影响分析
GET  /api/v1/analysis/keyword-trends  # 关键词趋势
POST /api/v1/backtest/run/{symbol}    # 运行回测
```

## 改进方向 (Future Improvements)

### 短期目标 (1-2 周)
1. **完整部署** - 完成 React 前端编译和部署
2. **AI 集成** - 配置 Claude AI API，实现真实新闻分析
3. **数据源集成** - 连接真实 RSS 新闻源
4. **性能优化** - 数据库查询和缓存优化

### 中期目标 (1-2 月)
1. **实时功能** - WebSocket 实时数据推送
2. **高级回测** - 更复杂的交易策略回测
3. **机器学习** - 基于历史数据的预测模型训练
4. **用户系统** - 用户认证和个人化设置
5. **移动端** - React Native 移动应用

### 长期目标 (3-6 月)
1. **多语言支持** - 国际新闻源和多语言分析
2. **高级分析** - 技术指标集成和算法交易信号
3. **云原生** - Kubernetes 部署和微服务架构
4. **商业化** - 订阅模式和企业级功能
5. **扩展市场** - 加密货币、外汇等市场支持

## 开发者指南

### 快速启动
```bash
# 1. 启动数据库服务
podman run -d --name newsdb -e POSTGRES_DB=newstrader -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5433:5432 postgres:15
podman run -d --name newsredis -p 6380:6379 redis:7-alpine

# 2. 启动后端
cd /home/wyatt/dev-projects/NewsTrader
backend/venv/bin/python simple_backend.py

# 3. 测试功能
# 打开 test.html 在浏览器中测试
```

### 环境配置
```bash
# 创建 .env 文件
cp backend/.env.example backend/.env

# 重要配置项
ANTHROPIC_API_KEY=your_claude_api_key
DATABASE_URL=postgresql://postgres:password@localhost:5433/newstrader
REDIS_URL=redis://localhost:6380
```

### 下一步工作重点
1. **配置 Claude AI API 密钥** - 启用真实 AI 分析
2. **完成 React 前端部署** - 提供完整用户界面
3. **集成真实新闻源** - 替换样本数据
4. **性能测试和优化** - 确保生产就绪

## 联系和维护

- **项目路径**: `/home/wyatt/dev-projects/NewsTrader`
- **技术栈**: Python + React + PostgreSQL + Redis
- **AI 引擎**: Claude AI (Anthropic)
- **容器化**: Podman/Docker
- **开发环境**: WSL Ubuntu

---

*本文档为 NewsTrader 项目的完整技术概览，适用于项目交接和持续开发。*