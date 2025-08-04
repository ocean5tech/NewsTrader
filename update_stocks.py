#!/usr/bin/env python3
"""
股票数据更新脚本 - 从东方财富API获取完整A股数据
"""

import requests
import psycopg2
import json
import time
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

def fetch_stock_data():
    """从东方财富API获取A股数据 - 分页获取所有数据"""
    print("🔍 正在从东方财富API获取A股数据...")
    
    all_stocks = []
    page = 1
    page_size = 2000  # 每页2000只股票
    
    while True:
        print(f"📄 正在获取第 {page} 页数据...")
        
        # 东方财富A股列表API
        url = "http://80.push2.eastmoney.com/api/qt/clist/get"
        params = {
            'pn': page,  # 页数
            'pz': page_size,  # 每页数量
            'po': 1,  # 排序
            'np': 1,  # 下拉刷新
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': 2,
            'invt': 2,
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # A股主板、中小板、创业板、科创板
            'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            if 'data' not in data or 'diff' not in data['data']:
                print(f"❌ 第 {page} 页API响应格式错误")
                break
            
            diff_data = data['data']['diff']
            
            if not diff_data or len(diff_data) == 0:
                print(f"✅ 第 {page} 页没有更多数据，停止获取")
                break
            
            print(f"📊 第 {page} 页获取到 {len(diff_data)} 只股票数据")
            
            page_stocks = []
            for item in diff_data:
                try:
                    # f12: 股票代码, f14: 股票名称, f13: 市场标识
                    symbol = item.get('f12', '')
                    name = item.get('f14', '')
                    market_code = item.get('f13', 0)
                    
                    if not symbol or not name:
                        continue
                    
                    # 确定交易所
                    if market_code == 0:  # 深交所
                        exchange = 'SZ'
                        ts_code = f"{symbol}.SZ"
                    elif market_code == 1:  # 上交所
                        exchange = 'SH' 
                        ts_code = f"{symbol}.SH"
                    else:
                        continue  # 跳过其他市场
                    
                    # 生成拼音简写
                    name_pinyin_short = get_pinyin_short(name)
                    
                    # 确定市场类别
                    if symbol.startswith('000') or symbol.startswith('001') or symbol.startswith('002'):
                        market = '主板'
                    elif symbol.startswith('300'):
                        market = '创业板'
                    elif symbol.startswith('688'):
                        market = '科创板'
                    elif symbol.startswith('600') or symbol.startswith('601') or symbol.startswith('603'):
                        market = '主板'
                    else:
                        market = '其他'
                    
                    stock_data = {
                        'symbol': symbol,
                        'ts_code': ts_code,
                        'name': name,
                        'name_pinyin_short': name_pinyin_short,
                        'exchange': exchange,
                        'market': market,
                        'list_status': 'L'  # 上市状态
                    }
                    
                    page_stocks.append(stock_data)
                    
                except Exception as e:
                    print(f"⚠️  处理股票数据时出错: {e}")
                    continue
            
            all_stocks.extend(page_stocks)
            print(f"✅ 第 {page} 页成功处理 {len(page_stocks)} 只股票，累计 {len(all_stocks)} 只")
            
            # 如果这一页的数据少于页面大小，说明是最后一页
            if len(diff_data) < page_size:
                print(f"🏁 已获取所有数据，总计 {len(all_stocks)} 只股票")
                break
            
            page += 1
            time.sleep(1)  # 避免请求过快
            
        except requests.RequestException as e:
            print(f"❌ 第 {page} 页网络请求失败: {e}")
            if page == 1:  # 如果第一页就失败，直接返回
                return []
            else:  # 否则返回已获取的数据
                break
        except Exception as e:
            print(f"❌ 第 {page} 页处理失败: {e}")
            break
    
    print(f"✅ 总共成功处理 {len(all_stocks)} 只股票数据")
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
    print("🚀 开始更新A股数据...")
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 获取股票数据
    stocks = fetch_stock_data()
    
    if not stocks:
        print("❌ 未获取到股票数据，退出程序")
        return
    
    # 更新数据库
    result = update_database(stocks)
    
    print(f"⏰ 完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 A股数据更新完成!")
    
    return result

if __name__ == "__main__":
    main()