# NewsTrader n8n 集成设置指南

## 🎯 概述

已成功将 n8n 工作流自动化平台集成到 NewsTrader 项目中，用于可视化管理新闻抓取和处理流程。

## 🚀 快速启动

### 1. 启动 n8n 服务
```bash
# 使用提供的启动脚本
./scripts/start-n8n.sh

# 或手动启动
podman run -d --name n8n-newstrader \
  -p 5678:5678 \
  --network host \
  -e DB_TYPE=postgresdb \
  -e DB_POSTGRESDB_HOST=localhost \
  -e DB_POSTGRESDB_PORT=5433 \
  -e DB_POSTGRESDB_DATABASE=newstrader \
  -e DB_POSTGRESDB_USER=postgres \
  -e DB_POSTGRESDB_PASSWORD=password \
  -e DB_POSTGRESDB_SCHEMA=n8n \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=newstrader123 \
  docker.io/n8nio/n8n
```

### 2. 访问 Web 界面
- **URL**: http://localhost:5678
- **用户名**: admin
- **密码**: newstrader123

### 3. 导入基础工作流
1. 点击右上角 "+" 按钮
2. 选择 "Import from file"
3. 上传文件: `n8n-workflows/basic-news-scraper.json`

## 📋 基础工作流说明

### 工作流结构
```
定时触发器 (每30分钟)
    ↓
并行抓取 RSS 源
├── Reuters 商业新闻
└── Bloomberg 市场新闻
    ↓
处理和过滤数据
├── 解析 RSS XML
├── 提取文章信息
├── 检查交易相关性
└── 去重处理
    ↓
影响力过滤 (评分 > 5)
    ↓
分发处理
├── 保存到 NewsTrader API
└── 触发深度分析
```

### 工作流节点详解

#### 1. Schedule Trigger (定时触发器)
- **频率**: 每30分钟执行一次
- **作用**: 自动触发新闻抓取流程
- **可调整**: 在节点设置中修改时间间隔

#### 2. RSS Request 节点 (Reuters & Bloomberg)
- **功能**: 获取RSS源的XML数据
- **Headers**: 设置了User-Agent避免被屏蔽
- **超时**: 30秒请求超时

#### 3. Process RSS Data (代码节点)
- **解析**: 从XML中提取标题、链接、描述、发布时间
- **过滤**: 只保留包含交易相关关键词的文章
- **去重**: 基于URL去除重复文章
- **评分**: 临时随机评分（待后续改进）

#### 4. Filter High Impact (条件判断)
- **条件**: relevance_score > 5
- **分支**: 高影响文章走不同处理路径

#### 5. API Integration 节点
- **Save to API**: 保存文章到NewsTrader数据库
- **Trigger Analysis**: 触发深度分析流程

## 🔧 配置和定制

### 修改抓取频率
1. 点击 "Schedule Trigger" 节点
2. 调整 "Interval" 设置
3. 保存工作流

### 添加新的RSS源
1. 复制现有的 HTTP Request 节点
2. 修改URL为新的RSS地址
3. 连接到 "Process RSS Data" 节点

### 调整过滤条件
1. 编辑 "Process RSS Data" 节点
2. 修改 `tradingKeywords` 数组
3. 调整 `relevance_score` 计算逻辑

### 自定义处理逻辑
1. 添加新的 Code 节点
2. 编写JavaScript处理逻辑
3. 连接到合适的位置

## 📊 监控和调试

### 查看执行历史
1. 点击工作流名称旁的 "Executions" 
2. 查看每次执行的详细日志
3. 检查节点输入输出数据

### 手动测试
1. 点击 "Execute Workflow" 按钮
2. 观察每个节点的执行结果
3. 调试问题节点

### 日志查看
```bash
# 查看n8n容器日志
podman logs n8n-newstrader

# 实时监控日志
podman logs -f n8n-newstrader
```

## 🔄 与现有系统集成

### API 端点配置
工作流中的API调用指向本地NewsTrader后端：
- `http://localhost:8000/api/v1/news/articles` - 保存文章
- `http://localhost:8000/api/v1/news/scrape` - 触发分析

### 数据库共享
n8n使用独立的schema (`n8n`) 存储工作流数据，与业务数据隔离但共享同一PostgreSQL实例。

### Celery 协同
- n8n负责工作流编排和触发
- Celery继续处理重计算任务
- 两者通过API接口协同工作

## 🛠️ 扩展建议

### 短期改进
1. **智能评分**: 集成更准确的影响力评分算法
2. **错误处理**: 添加重试和通知机制
3. **数据验证**: 增强文章数据的验证逻辑

### 长期规划
1. **多渠道集成**: 添加Twitter、Reddit等社交媒体源
2. **实时通知**: 高影响新闻的即时Slack/邮件通知
3. **机器学习**: 基于历史数据训练评分模型

## 🔒 安全注意事项

- Web界面已启用基础认证
- 数据库密码通过环境变量配置
- 建议生产环境使用更强的密码
- 考虑启用HTTPS访问

## 📞 故障排除

### 常见问题
1. **无法访问界面**: 检查端口5678是否被占用
2. **数据库连接失败**: 确认PostgreSQL服务正在运行
3. **RSS解析错误**: 检查RSS源是否可访问

### 重启服务
```bash
# 停止n8n容器
podman stop n8n-newstrader
podman rm n8n-newstrader

# 重新启动
./scripts/start-n8n.sh
```

---

**配置完成！** 现在可以通过可视化界面管理NewsTrader的自动化工作流了。