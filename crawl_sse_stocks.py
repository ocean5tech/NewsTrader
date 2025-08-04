#!/usr/bin/env python3
"""
爬取上海证券交易所股票列表
https://www.sse.com.cn/assortment/stock/list/share/
"""

import requests
import json
import time
import psycopg2
from pypinyin import lazy_pinyin

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'user': 'postgres',
    'password': 'password',
    'database': 'newstrader'
}

def get_pinyin_short(chinese_text):
    """生成拼音简写"""
    if not chinese_text:
        return ""
    
    # 获取拼音首字母
    pinyin_list = lazy_pinyin(chinese_text, strict=False)
    short = ''.join([py[0].upper() for py in pinyin_list if py])
    return short[:20]  # 限制长度

def crawl_sse_stocks():
    """爬取上交所股票数据"""
    print("🕷️  开始爬取上海证券交易所股票数据...")
    
    # 上交所股票列表API
    base_url = "http://query.sse.com.cn/security/stock/getStockListData2.do"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'http://www.sse.com.cn/',
        'Host': 'query.sse.com.cn'
    }
    
    all_stocks = []
    
    # 获取主板股票 (股票类型1)
    try:
        print("📊 获取主板股票...")
        params = {
            'jsonCallBack': 'jsonpCallback123456',
            'isPagination': 'true',
            'stockCode': '',
            'csrcCode': '',
            'areaName': '',
            'stockType': '1',  # 主板
            'pageHelp.cacheSize': '1',
            'pageHelp.beginPage': '1',
            'pageHelp.pageSize': '5000',  # 大页面大小
            'pageHelp.pageNo': '1',
            'pageHelp.endPage': '1'
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        content = response.text
        print(f"   📄 响应内容前100字符: {content[:100]}")
        
        # 尝试不同的解析方式
        data = None
        try:
            if content.startswith('jsonpCallback123456(') and content.endswith(')'):
                # JSONP格式
                json_str = content[20:-1]  # 修正长度
                data = json.loads(json_str)
            elif content.startswith('{'):
                # 直接JSON格式
                data = json.loads(content)
            else:
                # 可能是其他格式，尝试找到JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析失败: {e}")
            print(f"   📄 尝试解析的内容: {content[:200]}...")
            data = None
            
            if 'result' in data and data['result']:
                stocks_data = data['result']
                print(f"   📈 获取到 {len(stocks_data)} 只主板股票")
                
                for stock in stocks_data:
                    try:
                        symbol = stock.get('SECURITY_CODE_A', '').strip()
                        name = stock.get('SECURITY_ABBR_A', '').strip()
                        
                        if not symbol or not name:
                            continue
                        
                        # 生成拼音简写
                        name_pinyin_short = get_pinyin_short(name)
                        
                        # 确定市场类别
                        if symbol.startswith('688'):
                            market = '科创板'
                        else:
                            market = '主板'
                        
                        stock_data = {
                            'symbol': symbol,
                            'ts_code': f"{symbol}.SH",
                            'name': name,
                            'name_pinyin_short': name_pinyin_short,
                            'exchange': 'SH',
                            'market': market,
                            'list_status': 'L'
                        }
                        
                        all_stocks.append(stock_data)
                        
                    except Exception as e:
                        print(f"⚠️  处理股票数据时出错: {e}")
                        continue
        
        time.sleep(1)  # 避免请求过快
        
    except Exception as e:
        print(f"❌ 获取主板股票失败: {e}")
    
    # 获取科创板股票 (股票类型8)
    try:
        print("📊 获取科创板股票...")
        params = {
            'jsonCallBack': 'jsonpCallback123456',
            'isPagination': 'true',
            'stockCode': '',
            'csrcCode': '',
            'areaName': '',
            'stockType': '8',  # 科创板
            'pageHelp.cacheSize': '1',
            'pageHelp.beginPage': '1',
            'pageHelp.pageSize': '5000',
            'pageHelp.pageNo': '1',
            'pageHelp.endPage': '1'
        }
        
        response = requests.get(base_url, params=params, headers=headers, timeout=30)
        response.raise_for_status()
        
        # 解析响应
        content = response.text
        print(f"   📄 科创板响应内容前100字符: {content[:100]}")
        
        # 尝试不同的解析方式
        data = None
        try:
            if content.startswith('jsonpCallback123456(') and content.endswith(')'):
                # JSONP格式
                json_str = content[20:-1]  # 修正长度
                data = json.loads(json_str)
            elif content.startswith('{'):
                # 直接JSON格式
                data = json.loads(content)
            else:
                # 可能是其他格式，尝试找到JSON部分
                import re
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON解析失败: {e}")
            print(f"   📄 尝试解析的内容: {content[:200]}...")
            data = None
            
            if 'result' in data and data['result']:
                stocks_data = data['result']
                print(f"   🚀 获取到 {len(stocks_data)} 只科创板股票")
                
                for stock in stocks_data:
                    try:
                        symbol = stock.get('SECURITY_CODE_A', '').strip()
                        name = stock.get('SECURITY_ABBR_A', '').strip()
                        
                        if not symbol or not name:
                            continue
                        
                        # 生成拼音简写
                        name_pinyin_short = get_pinyin_short(name)
                        
                        stock_data = {
                            'symbol': symbol,
                            'ts_code': f"{symbol}.SH",
                            'name': name,
                            'name_pinyin_short': name_pinyin_short,
                            'exchange': 'SH',
                            'market': '科创板',
                            'list_status': 'L'
                        }
                        
                        all_stocks.append(stock_data)
                        
                    except Exception as e:
                        print(f"⚠️  处理股票数据时出错: {e}")
                        continue
        
    except Exception as e:
        print(f"❌ 获取科创板股票失败: {e}")
    
    print(f"✅ 上交所总共爬取到 {len(all_stocks)} 只股票")
    return all_stocks

def update_database(stocks):
    """更新数据库中的股票数据"""
    if not stocks:
        print("❌ 没有股票数据需要更新")
        return {'added': 0, 'updated': 0, 'total': 0}
    
    print(f"💾 正在更新数据库，共 {len(stocks)} 只股票...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        added_count = 0
        updated_count = 0
        
        for stock in stocks:
            try:
                # 检查股票是否已存在
                cursor.execute("SELECT id FROM a_stocks WHERE symbol = %s", (stock['symbol'],))
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有记录
                    cursor.execute("""
                        UPDATE a_stocks SET 
                            name = %s,
                            name_pinyin_short = %s,
                            ts_code = %s,
                            exchange = %s,
                            market = %s,
                            list_status = %s
                        WHERE symbol = %s
                    """, (
                        stock['name'],
                        stock['name_pinyin_short'],
                        stock['ts_code'],
                        stock['exchange'],
                        stock['market'],
                        stock['list_status'],
                        stock['symbol']
                    ))
                    updated_count += 1
                else:
                    # 插入新记录
                    cursor.execute("""
                        INSERT INTO a_stocks (symbol, ts_code, name, name_pinyin_short, exchange, market, list_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        stock['symbol'],
                        stock['ts_code'],
                        stock['name'],
                        stock['name_pinyin_short'],
                        stock['exchange'],
                        stock['market'],
                        stock['list_status']
                    ))
                    added_count += 1
                
                # 批量提交，每100条提交一次
                if (added_count + updated_count) % 100 == 0:
                    conn.commit()
                    print(f"📝 已处理 {added_count + updated_count} 只股票...")
                    
            except Exception as e:
                print(f"⚠️  处理股票 {stock['symbol']} 时出错: {e}")
                continue
        
        # 最终提交
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 数据库更新完成!")
        print(f"   - 新增股票: {added_count} 只")
        print(f"   - 更新股票: {updated_count} 只")
        print(f"   - 处理总数: {added_count + updated_count} 只")
        
        return {
            'added': added_count,
            'updated': updated_count,
            'total': added_count + updated_count
        }
        
    except Exception as e:
        print(f"❌ 数据库更新失败: {e}")
        return {'added': 0, 'updated': 0, 'total': 0, 'error': str(e)}

def main():
    """主函数"""
    print("🚀 开始爬取上海证券交易所完整股票数据...")
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 爬取上交所数据
    stocks = crawl_sse_stocks()
    
    if not stocks:
        print("❌ 未获取到股票数据，退出程序")
        return
    
    # 更新数据库
    result = update_database(stocks)
    
    print(f"⏰ 完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 上交所股票数据爬取完成!")
    
    return result

if __name__ == "__main__":
    main()