#!/bin/bash

# NewsTrader 开发环境启动脚本

echo "🚀 启动 NewsTrader 开发环境..."

# 设置无代理环境变量（解决IBM代理问题）
export NO_PROXY="localhost,127.0.0.1,0.0.0.0"
unset http_proxy
unset https_proxy
unset HTTP_PROXY
unset HTTPS_PROXY

# 检查必要的服务
echo "📊 检查数据库服务..."
if ! podman ps | grep -q "newsdb"; then
    echo "❌ PostgreSQL 未运行，请先启动数据库"
    echo "运行: podman start newsdb"
    exit 1
fi

if ! podman ps | grep -q "newsredis"; then
    echo "❌ Redis 未运行，请先启动Redis"
    echo "运行: podman start newsredis" 
    exit 1
fi

echo "✅ 数据库服务正常"

# 启动后端
echo "🔧 启动后端服务..."
if pgrep -f "simple_backend.py" > /dev/null; then
    echo "✅ 后端已在运行"
else
    echo "📦 启动后端..."
    cd /home/wyatt/dev-projects/NewsTrader
    backend/venv/bin/python simple_backend.py &
    BACKEND_PID=$!
    echo "⏳ 等待后端启动..."
    sleep 5
    
    # 测试后端连接
    if curl -s --connect-timeout 5 http://localhost:8000/health > /dev/null; then
        echo "✅ 后端启动成功 (PID: $BACKEND_PID)"
    else
        echo "❌ 后端启动失败"
        exit 1
    fi
fi

# 启动前端  
echo "🎨 启动前端服务..."
if pgrep -f "react-scripts.*NewsTrader" > /dev/null; then
    echo "✅ 前端已在运行"
else
    echo "📦 启动前端..."
    cd /home/wyatt/dev-projects/NewsTrader/frontend
    NO_PROXY="localhost,127.0.0.1" npm start &
    FRONTEND_PID=$!
    echo "⏳ 等待前端启动..."
    sleep 10
    
    # 测试前端连接
    if curl -s --connect-timeout 5 http://localhost:3000 > /dev/null; then
        echo "✅ 前端启动成功 (PID: $FRONTEND_PID)"
    else
        echo "❌ 前端启动失败"
        exit 1
    fi
fi

# 启动n8n（如果需要）
echo "🔄 检查n8n服务..."
if podman ps | grep -q "n8n-newstrader"; then
    echo "✅ n8n 已在运行"
else
    echo "📦 启动n8n..."
    ./scripts/start-n8n.sh > /dev/null 2>&1 &
    sleep 5
    if podman ps | grep -q "n8n-newstrader"; then
        echo "✅ n8n 启动成功"
    else
        echo "⚠️  n8n 启动失败，但不影响主要功能"
    fi
fi

echo ""
echo "🎉 NewsTrader 开发环境启动完成!"
echo ""
echo "📱 服务访问地址:"
echo "   前端界面: http://localhost:3000"
echo "   后端API:  http://localhost:8000"
echo "   API文档:  http://localhost:8000/docs"
echo "   n8n工作流: http://localhost:5678"
echo ""
echo "🔧 API测试命令:"
echo "   健康检查: curl http://localhost:8000/health"
echo "   获取新闻: curl http://localhost:8000/api/v1/news/articles"
echo "   影响分析: curl http://localhost:8000/api/v1/analysis/impact-summary"
echo ""
echo "📝 开发注意事项:"
echo "   - 已设置NO_PROXY绕过IBM代理"
echo "   - 前端会自动刷新代码变更"
echo "   - 后端支持热重载"
echo "   - 数据存储在PostgreSQL中"
echo ""
echo "✅ 准备就绪，开始开发吧！"