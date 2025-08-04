#!/bin/bash

# NewsTrader A股股票系统设置脚本

echo "🚀 设置 NewsTrader A股股票系统..."

# 检查数据库连接
echo "📊 检查数据库连接..."
if ! podman ps | grep -q "newsdb"; then
    echo "❌ PostgreSQL 数据库未运行，请先启动数据库服务"
    echo "运行: podman run -d --name newsdb -e POSTGRES_DB=newstrader -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=password -p 5433:5432 postgres:15"
    exit 1
fi

# 创建数据库表
echo "🗄️  创建股票数据表..."
export PGPASSWORD=password
psql -h localhost -p 5433 -U postgres -d newstrader -f /home/wyatt/dev-projects/NewsTrader/backend/migrations/create_stock_tables.sql

if [ $? -eq 0 ]; then
    echo "✅ 数据库表创建成功"
else
    echo "❌ 数据库表创建失败"
    exit 1
fi

# 安装Python依赖
echo "📦 安装Python依赖..."
cd /home/wyatt/dev-projects/NewsTrader/backend
if [ -d "venv" ]; then
    source venv/bin/activate
    pip install pypinyin==0.49.0 tushare==1.2.89 akshare==1.12.81
    echo "✅ Python依赖安装完成"
else
    echo "⚠️  虚拟环境不存在，请手动安装依赖: pip install pypinyin tushare akshare"
fi

# 检查后端服务
echo "🔍 检查后端服务状态..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ 后端服务运行正常"
    
    # 初始化股票数据
    echo "📈 初始化股票数据..."
    response=$(curl -s -X POST http://localhost:8000/api/v1/stocks/update \
        -H "Content-Type: application/json" \
        -H "Accept: application/json")
    
    if [ $? -eq 0 ]; then
        echo "✅ 股票数据初始化成功"
        echo "📊 响应: $response"
    else
        echo "⚠️  股票数据初始化失败，可稍后手动执行"
    fi
else
    echo "⚠️  后端服务未运行，请先启动: python simple_backend.py"
fi

echo ""
echo "🎯 A股股票系统设置完成！"
echo ""
echo "📋 可用的API接口:"
echo "   - 搜索股票: GET /api/v1/stocks/search?q=000001"
echo "   - 获取股票信息: GET /api/v1/stocks/000001"
echo "   - 获取股票列表: GET /api/v1/stocks/list"
echo "   - 更新股票数据: POST /api/v1/stocks/update"
echo "   - 关注列表: GET /api/v1/stocks/watchlist/"
echo "   - 添加关注: POST /api/v1/stocks/watchlist/"
echo ""
echo "🔍 搜索功能支持:"
echo "   - 股票代码: 000001, 600000"
echo "   - 拼音首字母: PAYH (平安银行), GZMZ (贵州茅台)"
echo "   - 股票名称: 平安, 茅台"
echo ""
echo "🤖 n8n 工作流:"
echo "   - 自动更新: stock-data-updater.json (每周日凌晨2点)"
echo "   - 手动更新: manual-stock-update.json (可随时执行)"
echo ""
echo "📖 使用示例:"
echo '   curl "http://localhost:8000/api/v1/stocks/search?q=PAYH&limit=5"'
echo '   curl "http://localhost:8000/api/v1/stocks/000001"'
echo '   curl -X POST "http://localhost:8000/api/v1/stocks/watchlist/" -H "Content-Type: application/json" -d '"'"'{"symbol":"000001","notes":"关注平安银行"}'"'"
echo ""
echo "✅ 系统已准备就绪！"