# NewsTrader A股股票系统使用指南

## 🎯 系统概述

A股股票信息管理系统，支持股票代码、名称和拼音首字母搜索，提供完整的股票关注列表功能和自动数据更新。

## 🚀 快速开始

### 1. 系统初始化
```bash
# 运行自动设置脚本
./scripts/setup-stock-system.sh
```

### 2. 手动设置（如果自动脚本失败）
```bash
# 1. 创建数据库表
psql -h localhost -p 5433 -U postgres -d newstrader -f backend/migrations/create_stock_tables.sql

# 2. 安装依赖
pip install pypinyin==0.49.0 tushare==1.2.89 akshare==1.12.81

# 3. 初始化股票数据
curl -X POST http://localhost:8000/api/v1/stocks/update
```

## 📊 数据库结构

### A股股票表 (a_stocks)
- `symbol`: 股票代码 (000001)
- `ts_code`: TS代码 (000001.SZ)
- `name`: 股票名称
- `name_pinyin`: 全拼音 (PINGANYHANG)
- `name_pinyin_short`: 拼音首字母 (PAYH)
- `exchange`: 交易所 (SH/SZ)
- `market`: 市场类型 (主板/创业板/科创板)
- `list_status`: 上市状态 (L上市/D退市/P暂停)

### 关注列表表 (stock_watchlist)
- `symbol`: 股票代码
- `name`: 股票名称
- `is_active`: 是否激活监控
- `alert_enabled`: 是否启用提醒
- `notes`: 备注信息

## 🔍 API 接口详解

### 1. 股票搜索
```bash
# 按股票代码搜索
curl "http://localhost:8000/api/v1/stocks/search?q=000001&limit=10"

# 按拼音首字母搜索
curl "http://localhost:8000/api/v1/stocks/search?q=PAYH&limit=10"

# 按股票名称搜索
curl "http://localhost:8000/api/v1/stocks/search?q=平安&limit=10"
```

**响应示例:**
```json
{
  "total": 1,
  "results": [
    {
      "symbol": "000001",
      "ts_code": "000001.SZ",
      "name": "平安银行",
      "exchange": "SZ",
      "market": "主板",
      "name_pinyin": "PINGANYHANG",
      "name_pinyin_short": "PAYH",
      "list_status": "L"
    }
  ]
}
```

### 2. 获取股票信息
```bash
curl "http://localhost:8000/api/v1/stocks/000001"
```

### 3. 获取股票列表
```bash
# 获取所有股票
curl "http://localhost:8000/api/v1/stocks/list?limit=100"

# 按交易所筛选
curl "http://localhost:8000/api/v1/stocks/list?exchange=SZ&limit=50"

# 按市场类型筛选
curl "http://localhost:8000/api/v1/stocks/list?market=创业板&limit=50"
```

### 4. 更新股票数据
```bash
curl -X POST "http://localhost:8000/api/v1/stocks/update"
```

### 5. 关注列表管理

#### 获取关注列表
```bash
curl "http://localhost:8000/api/v1/stocks/watchlist/"
```

#### 添加股票到关注列表
```bash
curl -X POST "http://localhost:8000/api/v1/stocks/watchlist/" \
  -H "Content-Type: application/json" \
  -d '{"symbol":"000001","notes":"关注平安银行走势"}'
```

#### 更新关注项
```bash
curl -X PUT "http://localhost:8000/api/v1/stocks/watchlist/1" \
  -H "Content-Type: application/json" \
  -d '{"notes":"更新备注","alert_enabled":true}'
```

#### 删除关注项
```bash
curl -X DELETE "http://localhost:8000/api/v1/stocks/watchlist/1"
```

## 🔤 拼音搜索功能

### 支持的搜索方式

1. **股票代码**: `000001`, `600000`, `300001`
2. **拼音首字母**: `PAYH`, `GZMZ`, `ZGSY`
3. **股票名称**: `平安`, `茅台`, `石油`

### 常用股票拼音首字母
- 平安银行 (000001): `PAYH`
- 万科A (000002): `WKA`
- 贵州茅台 (600519): `GZMZ`
- 中国石油 (601857): `ZGSY`
- 招商银行 (600036): `ZSYH`
- 中国平安 (601318): `ZGPA`

## 🤖 n8n 自动化工作流

### 1. 定时更新工作流 (stock-data-updater.json)
- **执行频率**: 每周日凌晨2:00
- **功能**: 自动获取最新股票数据并更新数据库
- **包含**: 错误处理、重试机制、数据验证

### 2. 手动更新工作流 (manual-stock-update.json)
- **触发方式**: 手动执行
- **功能**: 完整的数据更新流程和质量验证
- **包含**: API健康检查、数据验证、详细报告

### 导入工作流步骤
1. 访问 n8n 界面: http://localhost:5678
2. 登录 (admin/newstrader123)
3. 点击 "Import from file"
4. 选择工作流 JSON 文件
5. 激活工作流

## 📈 数据源说明

### 主要数据源
1. **东方财富API**: 获取实时股票列表
2. **备用数据源**: 腾讯财经API (当主源不可用时)

### 数据更新策略
- **自动更新**: 每周日凌晨自动执行
- **手动更新**: 通过API接口或n8n工作流
- **增量更新**: 只更新变化的数据，提高效率

## 🔧 故障排除

### 常见问题

#### 1. 搜索无结果
**原因**: 数据库中无股票数据
**解决**: 执行数据初始化
```bash
curl -X POST "http://localhost:8000/api/v1/stocks/update"
```

#### 2. 拼音搜索不准确
**原因**: pypinyin依赖未安装
**解决**: 安装依赖
```bash
pip install pypinyin==0.49.0
```

#### 3. 数据更新失败
**原因**: 数据源连接问题
**解决**: 检查网络连接，或使用备用数据源

#### 4. API返回500错误
**原因**: 数据库表不存在
**解决**: 创建数据库表
```bash
psql -h localhost -p 5433 -U postgres -d newstrader -f backend/migrations/create_stock_tables.sql
```

### 调试方法

#### 1. 检查后端日志
```bash
# 查看后端服务日志
tail -f backend/logs/app.log
```

#### 2. 验证数据库连接
```bash
# 连接数据库检查表结构
psql -h localhost -p 5433 -U postgres -d newstrader -c "\\dt"
```

#### 3. 测试API接口
```bash
# 测试健康检查
curl http://localhost:8000/health

# 测试股票搜索
curl "http://localhost:8000/api/v1/stocks/search?q=000001"
```

## 📊 性能优化

### 数据库索引
已创建的索引：
- 股票代码索引 (symbol)
- TS代码索引 (ts_code)  
- 拼音首字母索引 (name_pinyin_short)
- 复合索引 (symbol + exchange)

### 搜索优化
- 使用 LIKE 查询支持前缀匹配
- 限制返回结果数量 (默认20，最大100)
- 只搜索上市状态股票 (list_status='L')

### 内存优化
- 批量处理股票数据更新
- 使用异步HTTP请求
- 合理的请求间隔避免被限流

## 📚 扩展功能

### 未来计划
1. **实时股价**: 集成实时股价API
2. **技术指标**: 添加技术分析指标
3. **价格提醒**: 基于关注列表的价格提醒
4. **数据导出**: 支持CSV/Excel导出
5. **移动端支持**: 提供移动端API

### 自定义开发
- 添加新的数据源
- 扩展搜索算法
- 集成其他金融数据
- 自定义关注规则

---

**系统版本**: v1.0  
**更新时间**: 2025-08-01  
**技术支持**: NewsTrader开发团队