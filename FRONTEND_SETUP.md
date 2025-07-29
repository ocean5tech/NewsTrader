# NewsTrader 前端开发环境设置

## 🎯 概述

React + TypeScript + Ant Design 前端已成功编译和部署，支持新闻展示、分析可视化、回测等功能。

## 🚀 快速启动

### 方式1: 使用启动脚本（推荐）
```bash
# 一键启动所有服务
./scripts/start-dev.sh
```

### 方式2: 手动启动
```bash
# 1. 设置环境变量（解决代理问题）
export NO_PROXY="localhost,127.0.0.1,0.0.0.0"
unset http_proxy https_proxy

# 2. 启动后端
backend/venv/bin/python simple_backend.py &

# 3. 启动前端
cd frontend && npm start
```

## 🌐 访问地址

- **前端界面**: http://localhost:3000
- **后端API**: http://localhost:8000  
- **API文档**: http://localhost:8000/docs
- **n8n工作流**: http://localhost:5678

## 📱 前端功能

### 主要页面

#### 1. Dashboard (仪表板)
- **路径**: `/dashboard`
- **功能**: 
  - 市场概览统计
  - 最新高影响力新闻
  - 实时市场情感指标
  - 关键数据卡片展示

#### 2. News (新闻页面)  
- **路径**: `/news`
- **功能**:
  - 新闻列表展示
  - 影响评分颜色标签
  - 情感分析显示
  - 受影响股票标签
  - 文章详情模态框
  - 实时数据刷新

#### 3. Analysis (分析页面)
- **路径**: `/analysis` 
- **功能**:
  - 市场情感监控面板
  - 股票影响对比图表
  - 影响汇总表格
  - 关键词趋势分析
  - 数据可视化图表

#### 4. Backtest (回测页面)
- **路径**: `/backtest`
- **功能**:
  - 历史预测准确性分析
  - 回测结果图表
  - 性能指标展示
  - 策略评估工具

### UI组件特色

#### 数据可视化
- **Recharts图表**: 条形图、饼图、线图
- **颜色编码**: 
  - 红色: 高影响(>7分)
  - 橙色: 中影响(4-7分) 
  - 绿色: 低影响(<4分)
  - 绿色: 正面情感(>0.1)
  - 红色: 负面情感(<-0.1)
  - 蓝色: 中性情感

#### 交互功能
- **实时刷新**: 定时拖取最新数据
- **智能过滤**: 按股票、影响评分过滤
- **详情查看**: 点击查看完整文章内容
- **响应式设计**: 适配不同屏幕尺寸

## 🔧 技术栈详情

### 前端依赖
```json
{
  "react": "^18.2.0",           // 核心框架
  "typescript": "^4.9.5",       // 类型安全
  "antd": "^5.12.8",           // UI组件库
  "react-router-dom": "^6.20.1", // 路由管理
  "react-query": "^3.39.3",    // 数据状态管理
  "recharts": "^2.8.0",        // 数据可视化
  "axios": "^1.6.2",           // HTTP客户端
  "dayjs": "^1.11.10"          // 日期处理
}
```

### 项目结构
```
frontend/
├── src/
│   ├── components/          # 公共组件
│   │   └── Navigation.tsx   # 导航栏
│   ├── pages/              # 页面组件
│   │   ├── Dashboard.tsx    # 仪表板
│   │   ├── NewsPage.tsx     # 新闻页面
│   │   ├── AnalysisPage.tsx # 分析页面
│   │   └── BacktestPage.tsx # 回测页面
│   ├── services/           # API服务
│   │   └── api.ts          # API封装
│   ├── types/              # TypeScript类型
│   │   └── index.ts        # 数据类型定义
│   ├── hooks/              # 自定义Hook
│   └── utils/              # 工具函数
├── public/                 # 静态资源
└── build/                  # 构建输出
```

## 📊 API集成

### 数据流架构
```
前端组件 → API服务层 → 后端FastAPI → 数据处理 → PostgreSQL
     ↑                                                  ↓
   状态管理 ← React Query ← HTTP响应 ← JSON数据 ← 数据库查询
```

### 主要API端点
```typescript
// 新闻相关
GET /api/v1/news/articles        // 获取新闻列表
GET /api/v1/news/articles/{id}   // 获取单篇新闻
GET /api/v1/news/trending        // 获取热门新闻

// 分析相关  
GET /api/v1/analysis/impact-summary    // 影响汇总
GET /api/v1/analysis/keyword-trends    // 关键词趋势

// 回测相关
POST /api/v1/backtest/run/{symbol}     // 运行回测
```

### 数据类型
```typescript
interface NewsArticle {
  id: string;
  title: string;
  summary: string;
  url: string;
  source: string;
  published_at: string;
  impact_score: number;      // 0-10
  sentiment_score: number;   // -1 to 1
  affected_symbols: string[];
  confidence_score: number;  // 0-1
}

interface ImpactSummary {
  symbol: string;
  article_count: number;
  avg_impact: number;
  avg_sentiment: number;
  avg_confidence: number;
}
```

## 🛠️ 开发工作流

### 热重载开发
- **前端**: 代码变更自动刷新浏览器
- **后端**: 支持FastAPI热重载
- **类型检查**: TypeScript实时错误提示

### 调试技巧
```bash
# 查看前端日志
cd frontend && npm start

# 查看后端日志  
tail -f /var/log/newstrader-backend.log

# API测试
NO_PROXY=localhost curl http://localhost:8000/api/v1/news/articles
```

### 常见问题解决

#### 1. 代理连接问题
```bash
# 设置环境变量
export NO_PROXY="localhost,127.0.0.1"
unset http_proxy https_proxy
```

#### 2. 端口冲突
```bash
# 检查端口占用
ss -tlnp | grep :3000
ss -tlnp | grep :8000

# 杀死占用进程
pkill -f "react-scripts"
pkill -f "simple_backend"
```

#### 3. 依赖问题
```bash
# 重新安装依赖
cd frontend && rm -rf node_modules package-lock.json
npm install
```

## 🎨 UI定制

### 主题配置
Ant Design主题可在`src/App.tsx`中定制：
```typescript
import { ConfigProvider, theme } from 'antd';

const customTheme = {
  token: {
    colorPrimary: '#1890ff',    // 主色调
    colorSuccess: '#52c41a',    // 成功色
    colorWarning: '#faad14',    // 警告色
    colorError: '#ff4d4f',      // 错误色
  },
};
```

### 响应式断点
```css
/* 移动端 */
@media (max-width: 768px) { }

/* 平板 */  
@media (max-width: 1024px) { }

/* 桌面端 */
@media (min-width: 1200px) { }
```

## 📈 性能优化

### 实现的优化
- **代码分割**: React.lazy动态导入
- **数据缓存**: React Query缓存管理
- **虚拟滚动**: 大数据列表优化
- **图片懒加载**: 新闻图片按需加载

### 待优化项
- **Service Worker**: 离线支持
- **Bundle分析**: webpack-bundle-analyzer
- **CDN加速**: 静态资源优化

## 🔄 未来扩展

### 计划功能
1. **实时通知**: WebSocket推送
2. **移动端适配**: 响应式优化
3. **主题切换**: 暗色模式支持
4. **多语言**: i18n国际化
5. **PWA支持**: 渐进式Web应用

### 集成计划
- **WebSocket**: 实时数据推送
- **Redis**: 前端状态缓存
- **Elasticsearch**: 全文搜索
- **Docker**: 容器化部署

---

**前端开发环境已就绪！** 现在可以进行全功能开发了。