#!/usr/bin/env python3
"""
Simple test API for troubleshooting
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

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'user': 'postgres',
    'password': 'password',
    'database': 'newstrader'
}

@app.get("/")
async def root():
    return {"message": "Test API Running", "status": "OK"}

@app.get("/api/v1/symbols/search")
async def search_symbols(q: str):
    """Search stock symbols"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = q.upper().strip()
        
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
        print(f"Search error: {e}")
        return {"results": [], "error": str(e)}

@app.post("/api/v1/watchlist/add")
async def add_watchlist(request: dict):
    """Add to watchlist"""
    try:
        symbol = request.get("symbol")
        if not symbol:
            return {"success": False, "error": "Symbol required"}
        
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Check if stock exists
        cursor.execute("""
            SELECT symbol, ts_code, name FROM a_stocks 
            WHERE symbol = %s AND list_status = 'L'
        """, (symbol,))
        
        stock = cursor.fetchone()
        if not stock:
            cursor.close()
            conn.close()
            return {"success": False, "error": f"Symbol {symbol} not found"}
        
        # Add to watchlist
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
            "watchlist": {"symbols": [symbol]}
        }
        
    except Exception as e:
        print(f"Add error: {e}")
        return {"success": False, "error": str(e)}

@app.get("/api/v1/watchlist")
async def get_watchlist():
    """Get watchlist"""
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
        print(f"Get watchlist error: {e}")
        return {"symbols": []}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Test API starting on port 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")