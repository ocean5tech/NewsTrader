#!/usr/bin/env python3
"""
直接测试股票搜索功能 - 验证数据库查询
"""

import psycopg2

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'user': 'postgres',
    'password': 'password',
    'database': 'newstrader'
}

def test_stock_search(query):
    """测试股票搜索"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        query = query.upper().strip()
        print(f"\n🔍 搜索查询: '{query}'")
        
        # 搜索SQL
        sql = """
        SELECT symbol, ts_code, name, exchange, name_pinyin_short, list_status
        FROM a_stocks 
        WHERE list_status = 'L' AND (
            symbol LIKE %s OR 
            name_pinyin_short LIKE %s OR 
            name LIKE %s
        )
        ORDER BY 
            CASE 
                WHEN symbol = %s THEN 1
                WHEN symbol LIKE %s THEN 2
                WHEN name_pinyin_short = %s THEN 3
                ELSE 4
            END
        LIMIT 10
        """
        
        params = [
            f"{query}%",      # symbol LIKE
            f"{query}%",      # pinyin_short LIKE  
            f"%{query}%",     # name LIKE
            query,            # exact symbol match
            f"{query}%",      # symbol prefix
            query             # exact pinyin match
        ]
        
        cursor.execute(sql, params)
        rows = cursor.fetchall()
        
        print(f"✅ 找到 {len(rows)} 个结果:")
        for i, row in enumerate(rows, 1):
            print(f"  {i}. {row[0]} - {row[2]} ({row[4]}) [{row[3]}]")
        
        cursor.close()
        conn.close()
        
        return len(rows) > 0
    
    except Exception as e:
        print(f"❌ 搜索错误: {e}")
        return False

def test_add_watchlist(symbol):
    """测试添加关注列表"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print(f"\n📝 测试添加关注: {symbol}")
        
        # 检查股票是否存在
        cursor.execute("""
            SELECT symbol, ts_code, name FROM a_stocks 
            WHERE symbol = %s AND list_status = 'L'
        """, (symbol,))
        
        stock = cursor.fetchone()
        if not stock:
            print(f"❌ 股票 {symbol} 不存在")
            cursor.close()
            conn.close()
            return False
        
        print(f"✅ 股票存在: {stock[0]} - {stock[2]}")
        
        # 添加到关注列表（如果表存在）
        try:
            cursor.execute("""
                INSERT INTO stock_watchlist (symbol, ts_code, name, notes)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (symbol) DO UPDATE SET 
                    is_active = true, 
                    notes = EXCLUDED.notes,
                    updated_at = CURRENT_TIMESTAMP
                RETURNING id, symbol, name
            """, (stock[0], stock[1], stock[2], "测试添加"))
            
            result = cursor.fetchone()
            conn.commit()
            print(f"✅ 成功添加到关注列表: ID={result[0]}, {result[1]} - {result[2]}")
            
        except Exception as e:
            print(f"⚠️  关注列表操作失败: {e}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 添加关注错误: {e}")
        return False

def main():
    print("🧪 NewsTrader 股票搜索功能测试")
    print("=" * 50)
    
    # 测试用例
    test_cases = [
        "PAYH",      # 拼音首字母搜索
        "000001",    # 股票代码搜索
        "平安",       # 中文名称搜索
        "WKA",       # 万科A拼音
        "茅台",       # 贵州茅台名称
        "不存在"      # 不存在的查询
    ]
    
    successful_searches = 0
    
    for query in test_cases:
        if test_stock_search(query):
            successful_searches += 1
    
    print(f"\n📊 搜索测试结果: {successful_searches}/{len(test_cases)} 成功")
    
    # 测试添加关注功能
    if successful_searches > 0:
        test_add_watchlist("000001")  # 测试添加平安银行
    
    print("\n🎯 问题诊断:")
    if successful_searches == 0:
        print("❌ 所有搜索都失败 - 可能是数据库连接问题")
    elif successful_searches < len(test_cases) - 1:  # 排除"不存在"这个预期失败的测试
        print("⚠️  部分搜索失败 - 可能是查询逻辑问题")
    else:
        print("✅ 搜索功能正常 - 数据库连接和查询都工作正常")
        print("💡 如果前端添加按钮仍然灰化，可能是前端API调用问题")

if __name__ == "__main__":
    main()