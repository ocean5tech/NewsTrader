#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
东方财富完整股票数据爬虫
"""

import requests
import json
import time

def get_all_stocks_from_eastmoney():
    """从东方财富分页获取所有股票数据"""
    print("开始从东方财富分页获取所有股票数据...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Referer': 'http://quote.eastmoney.com/',
    })
    
    all_stocks = []
    page = 1
    page_size = 100
    
    while True:
        print(f"正在获取第{page}页 (每页{page_size}条)...")
        
        url = 'http://push2.eastmoney.com/api/qt/clist/get'
        params = {
            'pn': str(page),
            'pz': str(page_size),
            'po': '1',
            'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2',
            'invt': '2',
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
            'fields': 'f12,f14,f2,f3,f20,f21'  # 代码,名称,最新价,涨跌幅,总市值,流通市值
        }
        
        try:
            response = session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('rc') == 0 and 'data' in data and 'diff' in data['data']:
                    page_stocks = data['data']['diff']
                    
                    if not page_stocks:  # 没有更多数据
                        print(f"第{page}页无数据，停止获取")
                        break
                    
                    # 处理当前页数据
                    valid_stocks = []
                    for stock in page_stocks:
                        code = stock.get('f12', '')
                        name = stock.get('f14', '')
                        
                        if code and name and len(code) == 6 and code.isdigit():
                            # 判断市场
                            if code.startswith('6'):
                                market = 'SH'
                                exchange = '上海证券交易所'
                            elif code.startswith(('0', '2', '3')):
                                market = 'SZ'
                                exchange = '深圳证券交易所'
                            else:
                                continue
                            
                            stock_info = {
                                'code': code,
                                'name': name,
                                'full_name': name,
                                'list_date': '',
                                'industry': '',
                                'area': '',
                                'market': market,
                                'exchange': exchange,
                                'price': stock.get('f2', 0),
                                'change_pct': stock.get('f3', 0),
                                'market_cap': stock.get('f20', 0),
                                'circulation_cap': stock.get('f21', 0)
                            }
                            valid_stocks.append(stock_info)
                    
                    all_stocks.extend(valid_stocks)
                    print(f"第{page}页获取成功: {len(valid_stocks)} 条有效数据")
                    
                    if len(page_stocks) < page_size:
                        print(f"第{page}页数据不足{page_size}条，可能已获取完所有数据")
                        break
                    
                    page += 1
                    time.sleep(1)  # 避免请求过快
                    
                    # 安全检查，避免无限循环
                    if page > 100 or len(all_stocks) > 10000:
                        print("已达到最大页数或数据量限制")
                        break
                        
                else:
                    print(f"第{page}页API返回错误: rc={data.get('rc')}")
                    break
                    
            else:
                print(f"第{page}页HTTP请求失败: {response.status_code}")
                break
                
        except Exception as e:
            print(f"第{page}页请求异常: {e}")
            break
    
    print(f"\n获取完成！总共获得 {len(all_stocks)} 条股票数据")
    
    # 统计分析
    sh_count = len([s for s in all_stocks if s['market'] == 'SH'])
    sz_count = len([s for s in all_stocks if s['market'] == 'SZ'])
    
    print(f"上海证券交易所: {sh_count} 只")
    print(f"深圳证券交易所: {sz_count} 只")
    
    # 检查是否达到目标
    if len(all_stocks) >= 1693:
        print("🎉 达到或超过目标数据量 1693 条!")
    elif len(all_stocks) >= 1000:
        print("✅ 获取到大量数据 (≥1000条)")
    else:
        print("⚠️ 获取数据量不足1000条")
    
    return all_stocks

def save_stocks_data(stocks, filename='eastmoney_stocks.json'):
    """保存股票数据"""
    if not stocks:
        print("没有数据可保存")
        return
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(stocks, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 {filename}")
        
        # 也保存CSV格式
        csv_filename = filename.replace('.json', '.csv')
        import csv
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['code', 'name', 'full_name', 'list_date', 'industry', 'area', 'market', 'exchange']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for stock in stocks:
                row = {field: stock.get(field, '') for field in fieldnames}
                writer.writerow(row)
        
        print(f"CSV数据已保存到 {csv_filename}")
        
    except Exception as e:
        print(f"保存数据失败: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("东方财富完整股票数据爬虫")
    print("目标：获取1693条A股数据")
    print("=" * 60)
    
    stocks = get_all_stocks_from_eastmoney()
    
    if stocks:
        save_stocks_data(stocks)
        
        print(f"\n最终结果:")
        print(f"获取股票数据: {len(stocks)} 条")
        
        if len(stocks) >= 1693:
            print("✅ 成功达到目标数据量!")
        else:
            print(f"❌ 未达到目标数据量 (差 {1693 - len(stocks)} 条)")
            
        # 显示前10条数据预览
        print("\n前10条数据预览:")
        print("-" * 80)
        for i, stock in enumerate(stocks[:10]):
            print(f"{i+1:2d}. {stock['code']} - {stock['name']} ({stock['exchange']})")
    else:
        print("❌ 未能获取到任何股票数据")