#!/bin/bash

# NewsTrader n8n 启动脚本

echo "🚀 启动 NewsTrader n8n 工作流系统..."

# 检查是否已有运行的n8n容器
if podman ps | grep -q "n8n-newstrader"; then
    echo "✅ n8n 已在运行"
else
    echo "📦 启动 n8n 容器..."
    
    # 启动n8n容器
    podman run -d --name n8n-newstrader \
        -p 5678:5678 \
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
        -e N8N_HOST=localhost \
        -e N8N_PORT=5678 \
        -e N8N_PROTOCOL=http \
        -e GENERIC_TIMEZONE=Asia/Shanghai \
        --network host \
        docker.io/n8nio/n8n
    
    echo "⏳ 等待 n8n 启动完成..."
    sleep 15
fi

echo ""
echo "🌐 n8n Web界面访问信息:"
echo "   URL: http://localhost:5678"
echo "   用户名: admin"
echo "   密码: newstrader123"
echo ""
echo "📋 基础工作流文件位置:"
echo "   /home/wyatt/dev-projects/NewsTrader/n8n-workflows/basic-news-scraper.json"
echo ""
echo "🔧 下一步操作:"
echo "   1. 打开浏览器访问 http://localhost:5678"
echo "   2. 使用上述用户名密码登录"
echo "   3. 导入基础工作流 JSON 文件"
echo "   4. 根据需要调整工作流配置"
echo ""
echo "✅ n8n 已准备就绪!"