#!/usr/bin/env python3
"""
简化的股票API服务 - 用于测试股票搜索和关注功能
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from typing import List, Dict, Any, Optional
import json
from pydantic import BaseModel

app = FastAPI(
    title="Stock Search API",
    description="A股股票搜索和关注API",
    version="1.0.0"
)

# CORS设置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'user': 'postgres',
    'password': 'password',
    'database': 'newstrader'
}

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"数据库连接失败: {str(e)}")

# Pydantic模型
class StockInfo(BaseModel):
    symbol: str
    ts_code: str
    name: str
    exchange: str
    market: Optional[str] = None
    name_pinyin: Optional[str] = None
    name_pinyin_short: Optional[str] = None
    list_status: str = "L"

class StockSearchResponse(BaseModel):
    total: int
    results: List[StockInfo]

class WatchlistRequest(BaseModel):
    symbol: str
    notes: Optional[str] = ""

class WatchlistItem(BaseModel):
    id: int
    symbol: str
    ts_code: str
    name: str
    is_active: bool
    alert_enabled: bool
    notes: Optional[str] = None
    added_at: str

@app.get("/")
async def root():
    return {"message": "Stock Search API is running", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "stock-api"}

@app.get("/api/v1/stocks/search", response_model=StockSearchResponse)
async def search_stocks(
    q: str = Query(..., description="搜索关键词，支持股票代码、拼音首字母或股票名称"),
    limit: int = Query(default=20, le=100, description="返回结果数量限制")
):
    """
    搜索股票
    支持的搜索方式：
    - 股票代码: 000001, 600000
    - 拼音首字母: PAYH (平安银行), GZMT (贵州茅台)
    - 股票名称: 平安, 茅台
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = q.upper().strip()
        
        # 构建SQL查询条件
        conditions = []
        params = []
        
        # 1. 股票代码搜索
        if query.isdigit():
            conditions.append("symbol LIKE %s")
            params.append(f"{query}%")
        
        # 2. 拼音首字母搜索
        if query.isalpha():
            conditions.append("name_pinyin_short LIKE %s")
            params.append(f"{query}%")
            conditions.append("name_pinyin LIKE %s")
            params.append(f"{query}%")
        
        # 3. 股票名称搜索
        conditions.append("name LIKE %s")
        params.append(f"%{query}%")
        
        # 构建完整的SQL查询
        sql = f"""
        SELECT symbol, ts_code, name, exchange, market, name_pinyin, name_pinyin_short, list_status
        FROM a_stocks 
        WHERE list_status = 'L' AND ({' OR '.join(conditions)})
        ORDER BY 
            CASE 
                WHEN symbol = %s THEN 1
                WHEN symbol LIKE %s THEN 2
                WHEN name_pinyin_short = %s THEN 3
                WHEN name_pinyin_short LIKE %s THEN 4
                ELSE 5
            END,
            symbol
        LIMIT %s
        """
        
        # 添加排序参数
        params.extend([query, f"{query}%", query, f"{query}%", limit])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            results.append(StockInfo(
                symbol=row[0],
                ts_code=row[1],
                name=row[2],
                exchange=row[3],
                market=row[4],
                name_pinyin=row[5],
                name_pinyin_short=row[6],
                list_status=row[7]
            ))
        
        cursor.close()
        conn.close()
        
        return StockSearchResponse(total=len(results), results=results)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")

@app.get("/api/v1/stocks/{symbol}", response_model=StockInfo)
async def get_stock_info(symbol: str):
    """获取单个股票信息"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT symbol, ts_code, name, exchange, market, name_pinyin, name_pinyin_short, list_status
            FROM a_stocks 
            WHERE symbol = %s AND list_status = 'L'
        """, (symbol,))
        
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail=f"股票 {symbol} 不存在")
        
        return StockInfo(
            symbol=row[0],
            ts_code=row[1],
            name=row[2],
            exchange=row[3],
            market=row[4],
            name_pinyin=row[5],
            name_pinyin_short=row[6],
            list_status=row[7]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票信息失败: {str(e)}")

@app.get("/api/v1/stocks/watchlist/", response_model=List[WatchlistItem])
async def get_watchlist(active_only: bool = Query(default=True, description="仅返回激活的关注项")):
    """获取股票关注列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT id, symbol, ts_code, name, is_active, alert_enabled, notes, added_at
                FROM stock_watchlist 
                WHERE is_active = true
                ORDER BY added_at DESC
            """)
        else:
            cursor.execute("""
                SELECT id, symbol, ts_code, name, is_active, alert_enabled, notes, added_at
                FROM stock_watchlist 
                ORDER BY added_at DESC
            """)
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        results = []
        for row in rows:
            results.append(WatchlistItem(
                id=row[0],
                symbol=row[1],
                ts_code=row[2],
                name=row[3],
                is_active=row[4],
                alert_enabled=row[5],
                notes=row[6],
                added_at=row[7].isoformat() if row[7] else ""
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关注列表失败: {str(e)}")

@app.post("/api/v1/stocks/watchlist/", response_model=WatchlistItem)
async def add_to_watchlist(request: WatchlistRequest):
    """添加股票到关注列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先检查股票是否存在
        cursor.execute("""
            SELECT symbol, ts_code, name FROM a_stocks 
            WHERE symbol = %s AND list_status = 'L'
        """, (request.symbol,))
        
        stock_row = cursor.fetchone()
        if not stock_row:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail=f"股票 {request.symbol} 不存在")
        
        symbol, ts_code, name = stock_row
        
        # 检查是否已在关注列表中
        cursor.execute("""
            SELECT id, symbol, ts_code, name, is_active, alert_enabled, notes, added_at
            FROM stock_watchlist 
            WHERE symbol = %s
        """, (request.symbol,))
        
        existing = cursor.fetchone()
        
        if existing:
            # 更新现有记录为激活状态
            cursor.execute("""
                UPDATE stock_watchlist 
                SET is_active = true, notes = %s, updated_at = CURRENT_TIMESTAMP
                WHERE symbol = %s
                RETURNING id, symbol, ts_code, name, is_active, alert_enabled, notes, added_at
            """, (request.notes, request.symbol))
            
            updated_row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return WatchlistItem(
                id=updated_row[0],
                symbol=updated_row[1],
                ts_code=updated_row[2],
                name=updated_row[3],
                is_active=updated_row[4],
                alert_enabled=updated_row[5],
                notes=updated_row[6],
                added_at=updated_row[7].isoformat()
            )
        else:
            # 添加新的关注项
            cursor.execute("""
                INSERT INTO stock_watchlist (symbol, ts_code, name, notes)
                VALUES (%s, %s, %s, %s)
                RETURNING id, symbol, ts_code, name, is_active, alert_enabled, notes, added_at
            """, (symbol, ts_code, name, request.notes))
            
            new_row = cursor.fetchone()
            conn.commit()
            cursor.close()
            conn.close()
            
            return WatchlistItem(
                id=new_row[0],
                symbol=new_row[1],
                ts_code=new_row[2],
                name=new_row[3],
                is_active=new_row[4],
                alert_enabled=new_row[5],
                notes=new_row[6],
                added_at=new_row[7].isoformat()
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加到关注列表失败: {str(e)}")

@app.delete("/api/v1/stocks/watchlist/{item_id}")
async def remove_from_watchlist(item_id: int):
    """从关注列表移除股票"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT name, symbol FROM stock_watchlist WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        
        if not item:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=404, detail="关注项不存在")
        
        name, symbol = item
        cursor.execute("DELETE FROM stock_watchlist WHERE id = %s", (item_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"message": f"已从关注列表移除 {name} ({symbol})"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"移除失败: {str(e)}")

@app.get("/api/v1/stocks/list", response_model=List[StockInfo])
async def get_stock_list(
    exchange: Optional[str] = Query(None, description="交易所代码 (SH/SZ)"),
    market: Optional[str] = Query(None, description="市场类型 (主板/创业板/科创板)"),
    limit: int = Query(default=100, le=1000, description="返回结果数量"),
    offset: int = Query(default=0, description="偏移量")
):
    """获取股票列表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = "SELECT symbol, ts_code, name, exchange, market, name_pinyin, name_pinyin_short, list_status FROM a_stocks WHERE list_status = 'L'"
        params = []
        
        if exchange:
            sql += " AND exchange = %s"
            params.append(exchange.upper())
        
        if market:
            sql += " AND market = %s"
            params.append(market)
        
        sql += " ORDER BY symbol LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        results = []
        for row in rows:
            results.append(StockInfo(
                symbol=row[0],
                ts_code=row[1],
                name=row[2],
                exchange=row[3],
                market=row[4],
                name_pinyin=row[5],
                name_pinyin_short=row[6],
                list_status=row[7]
            ))
        
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动简化股票API服务...")
    print("📊 支持的API接口:")
    print("   - GET  /api/v1/stocks/search?q=000001")
    print("   - GET  /api/v1/stocks/000001") 
    print("   - GET  /api/v1/stocks/list")
    print("   - GET  /api/v1/stocks/watchlist/")
    print("   - POST /api/v1/stocks/watchlist/")
    print("   - DELETE /api/v1/stocks/watchlist/{id}")
    print("")
    print("🔍 搜索示例:")
    print('   curl "http://localhost:8000/api/v1/stocks/search?q=PAYH"')
    print('   curl "http://localhost:8000/api/v1/stocks/search?q=000001"')
    print('   curl "http://localhost:8000/api/v1/stocks/search?q=平安"')
    print("")
    print("🎯 服务运行在: http://localhost:8000")
    
    uvicorn.run(app, host="0.0.0.0", port=8001)