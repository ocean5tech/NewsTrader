#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速股票数据爬虫 - 获取1693条A股数据
"""

import requests
import json
import time

def get_sina_all_stocks():
    """从新浪财经获取所有A股数据"""
    print("从新浪财经获取A股数据...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # 新浪A股接口，一次性获取所有数据
    url = 'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData'
    
    all_stocks = []
    
    # 分别获取上海和深圳市场
    markets = [
        ('sh_a_stock', '上海证券交易所', 'SH'),
        ('sz_a_stock', '深圳证券交易所', 'SZ')
    ]
    
    for node, exchange_name, market_code in markets:
        print(f"正在获取{exchange_name}数据...")
        
        params = {
            'page': '1',
            'num': '5000',  # 获取大量数据
            'sort': 'symbol',
            'asc': '1',
            'node': node
        }
        
        try:
            response = session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                text = response.text.strip()
                
                # 新浪返回的是JavaScript数组格式
                if text and text.startswith('[') and text.endswith(']'):
                    try:
                        data = json.loads(text)
                        
                        for item in data:
                            if isinstance(item, dict):
                                # 提取股票代码（去掉市场前缀）
                                symbol = item.get('symbol', '')
                                if len(symbol) > 6:
                                    code = symbol[-6:]  # 取后6位作为股票代码
                                else:
                                    code = symbol
                                
                                name = item.get('name', '')
                                
                                # 基本验证
                                if code and name and len(code) == 6 and code.isdigit():
                                    stock_info = {
                                        'code': code,
                                        'name': name,
                                        'full_name': name,
                                        'list_date': '',
                                        'industry': item.get('trade', ''),
                                        'area': '',
                                        'market': market_code,
                                        'exchange': exchange_name
                                    }
                                    all_stocks.append(stock_info)
                        
                        print(f"{exchange_name}获取成功: {len([s for s in all_stocks if s['market'] == market_code])} 只股票")
                        
                    except json.JSONDecodeError as e:
                        print(f"{exchange_name}JSON解析失败: {e}")
                else:
                    print(f"{exchange_name}响应格式不正确")
            else:
                print(f"{exchange_name}HTTP请求失败: {response.status_code}")
                
        except Exception as e:
            print(f"{exchange_name}请求异常: {e}")
        
        time.sleep(1)  # 避免请求过快
    
    return all_stocks

def get_eastmoney_batch():
    """从东方财富批量获取数据"""
    print("从东方财富获取A股数据...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    # 尝试不同的参数组合获取更多数据
    url = 'http://push2.eastmoney.com/api/qt/clist/get'
    
    all_stocks = []
    
    # 尝试分批次获取
    for page in range(1, 21):  # 最多20页
        print(f"获取第{page}页...")
        
        params = {
            'pn': str(page),
            'pz': '100',
            'po': '1',
            'np': '1',
            'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
            'fltt': '2',
            'invt': '2',
            'fid': 'f3',
            'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
            'fields': 'f12,f14'
        }
        
        try:
            response = session.get(url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('rc') == 0 and 'data' in data and 'diff' in data['data']:
                    page_stocks = data['data']['diff']
                    
                    if not page_stocks:
                        print(f"第{page}页无数据，停止获取")
                        break
                    
                    for stock in page_stocks:
                        code = stock.get('f12', '')
                        name = stock.get('f14', '')
                        
                        if code and name and len(code) == 6 and code.isdigit():
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
                                'exchange': exchange
                            }
                            all_stocks.append(stock_info)
                    
                    print(f"第{page}页: {len(page_stocks)} 条数据")
                    
                    if len(page_stocks) < 100:
                        print("当前页数据不足100条，可能已获取完毕")
                        break
                else:
                    print(f"第{page}页API错误")
                    break
            else:
                print(f"第{page}页HTTP错误: {response.status_code}")
                break
                
        except Exception as e:
            print(f"第{page}页异常: {e}")
            break
        
        time.sleep(0.5)
        
        # 如果已经获取足够数据，停止
        if len(all_stocks) > 2000:
            break
    
    return all_stocks

def deduplicate_stocks(stocks):
    """股票数据去重"""
    seen_codes = set()
    unique_stocks = []
    
    for stock in stocks:
        code = stock.get('code')
        if code and code not in seen_codes:
            seen_codes.add(code)
            unique_stocks.append(stock)
    
    return unique_stocks

def main():
    """主函数"""
    print("=" * 60)
    print("快速A股数据爬虫")
    print("目标：获取1693条A股数据")
    print("=" * 60)
    
    all_stocks = []
    
    # 方法1：新浪财经
    print("\n=== 方法1：新浪财经 ===")
    try:
        sina_stocks = get_sina_all_stocks()
        all_stocks.extend(sina_stocks)
        print(f"新浪财经获取: {len(sina_stocks)} 条")
    except Exception as e:
        print(f"新浪财经失败: {e}")
    
    # 如果数据不够，尝试东方财富
    if len(all_stocks) < 1500:
        print("\n=== 方法2：东方财富 ===")
        try:
            eastmoney_stocks = get_eastmoney_batch()
            all_stocks.extend(eastmoney_stocks)
            print(f"东方财富获取: {len(eastmoney_stocks)} 条")
        except Exception as e:
            print(f"东方财富失败: {e}")
    
    # 数据去重
    print(f"\n=== 数据处理 ===")
    print(f"去重前: {len(all_stocks)} 条")
    all_stocks = deduplicate_stocks(all_stocks)
    print(f"去重后: {len(all_stocks)} 条")
    
    # 统计分析
    sh_count = len([s for s in all_stocks if s['market'] == 'SH'])
    sz_count = len([s for s in all_stocks if s['market'] == 'SZ'])
    
    print(f"\n=== 最终结果 ===")
    print(f"总股票数: {len(all_stocks)} 条")
    print(f"上海证券交易所: {sh_count} 只")
    print(f"深圳证券交易所: {sz_count} 只")
    
    if len(all_stocks) >= 1693:
        print("🎉 成功达到目标数据量!")
    elif len(all_stocks) >= 1000:
        print("✅ 获取到大量数据")
    else:
        print("⚠️ 数据量不足")
    
    # 保存数据
    if all_stocks:
        with open('quick_stocks.json', 'w', encoding='utf-8') as f:
            json.dump(all_stocks, f, ensure_ascii=False, indent=2)
        print(f"数据已保存到 quick_stocks.json")
        
        # 显示前10条
        print(f"\n前10条数据预览:")
        for i, stock in enumerate(all_stocks[:10]):
            print(f"{i+1:2d}. {stock['code']} - {stock['name']} ({stock['exchange']})")
    
    return len(all_stocks)

if __name__ == "__main__":
    total = main()
    print(f"\n脚本执行完成，共获取 {total} 条股票数据")