#!/usr/bin/env python3
"""
快速修复API - 解决前端添加按钮问题
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'user': 'postgres',
    'password': 'password',
    'database': 'newstrader'
}

@app.get("/")
async def root():
    return {"message": "Quick Fix API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/api/v1/symbols/search")
async def search_symbols(q: str):
    """搜索股票品种"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = q.upper().strip()
        
        # 搜索数据库中的股票
        sql = """
        SELECT symbol, name, exchange, name_pinyin_short
        FROM a_stocks 
        WHERE list_status = 'L' AND (
            symbol LIKE %s OR 
            name_pinyin_short LIKE %s OR 
            name LIKE %s
        )
        ORDER BY symbol
        LIMIT 10
        """
        
        cursor.execute(sql, [f"{query}%", f"{query}%", f"%{query}%"])
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            symbol, name, exchange, pinyin_short = row
            category = "A股银行" if "银行" in name else "A股个股"
            results.append({
                "symbol": symbol,
                "name": name,
                "category": category,
                "match_type": "symbol" if symbol.startswith(query) else "name"
            })
        
        cursor.close()
        conn.close()
        
        return {"results": results}
        
    except Exception as e:
        print(f"搜索错误: {e}")
        return {"results": []}

@app.post("/api/v1/watchlist/add")
async def add_watchlist(request: dict):
    """添加到关注列表"""
    try:
        symbol = request.get("symbol")
        if not symbol:
            return {"success": False, "error": "Symbol required"}
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 检查股票是否存在
        cursor.execute("""
            SELECT symbol, ts_code, name FROM a_stocks 
            WHERE symbol = %s AND list_status = 'L'
        """, (symbol,))
        
        stock = cursor.fetchone()
        if not stock:
            cursor.close()
            conn.close()
            return {"success": False, "error": f"Symbol {symbol} not found"}
        
        # 添加到关注列表
        cursor.execute("""
            INSERT INTO stock_watchlist (symbol, ts_code, name, notes)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (symbol) DO UPDATE SET 
                is_active = true,
                updated_at = CURRENT_TIMESTAMP
        """, (stock[0], stock[1], stock[2], f"Added {stock[0]}"))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return {
            "success": True,
            "message": f"Successfully added {stock[2]} ({stock[0]})",
            "watchlist": {"symbols": [symbol]}  # 简化响应
        }
        
    except Exception as e:
        print(f"添加错误: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/v1/watchlist")
async def get_watchlist():
    """获取关注列表"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol FROM stock_watchlist 
            WHERE is_active = true
            ORDER BY added_at DESC
        """)
        
        symbols = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        
        return {
            "symbols": symbols,
            "created_at": "2025-08-01T00:00:00Z",
            "updated_at": "2025-08-01T00:00:00Z"
        }
        
    except Exception as e:
        print(f"获取关注列表错误: {e}")
        return {"symbols": []}

@app.post("/api/v1/watchlist/remove")
async def remove_watchlist(request: dict):
    """从关注列表移除"""
    try:
        symbol = request.get("symbol")
        if not symbol:
            return {"success": False, "error": "Symbol required"}
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM stock_watchlist WHERE symbol = %s", (symbol,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": f"Removed {symbol}"}
        
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/v1/watchlist/news")
async def get_watchlist_news():
    """获取关注新闻（模拟数据）"""
    return {"news": []}  # 返回空数组，避免错误

if __name__ == "__main__":
    import uvicorn
    print("🚀 Quick Fix API 启动中...")
    print("📊 提供以下API:")
    print("   - GET  /api/v1/symbols/search?q=000001")
    print("   - POST /api/v1/watchlist/add")
    print("   - GET  /api/v1/watchlist")
    print("   - POST /api/v1/watchlist/remove")
    print("")
    uvicorn.run(app, host="0.0.0.0", port=8000)