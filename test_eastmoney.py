#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试东方财富API获取股票数据
"""

import requests
import json
import time

def test_eastmoney_api():
    """测试东方财富API"""
    print("测试东方财富股票数据API...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    
    # 东方财富A股列表接口
    url = 'http://push2.eastmoney.com/api/qt/clist/get'
    params = {
        'pn': '1',
        'pz': '50',  # 先测试50条
        'po': '1',
        'np': '1',
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': '2',
        'invt': '2',
        'fid': 'f3',
        'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # A股市场
        'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
    }
    
    try:
        print("正在请求东方财富API...")
        response = session.get(url, params=params, timeout=30)
        
        print(f"HTTP状态码: {response.status_code}")
        print(f"响应长度: {len(response.text)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("JSON解析成功")
                print(f"响应结构: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                
                if data.get('rc') == 0 and 'data' in data:
                    if 'diff' in data['data']:
                        stocks_data = data['data']['diff']
                        print(f"获取到股票数据: {len(stocks_data)} 条")
                        
                        # 显示前5条数据
                        print("\n前5条股票数据:")
                        for i, stock in enumerate(stocks_data[:5]):
                            code = stock.get('f12', '')
                            name = stock.get('f14', '')
                            print(f"{i+1}. {code} - {name}")
                        
                        return len(stocks_data)
                    else:
                        print("数据结构中没有找到'diff'字段")
                        print(f"data字段内容: {list(data['data'].keys()) if isinstance(data.get('data'), dict) else data.get('data')}")
                else:
                    print(f"API返回错误: rc={data.get('rc')}, data存在={data.get('data') is not None}")
                    
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"响应前200字符: {response.text[:200]}")
        else:
            print(f"HTTP请求失败: {response.status_code}")
            print(f"响应内容: {response.text[:200]}")
            
    except Exception as e:
        print(f"请求异常: {e}")
        return 0
    
    return 0

def test_full_data():
    """测试获取完整数据"""
    print("\n" + "="*50)
    print("测试获取完整股票数据")
    print("="*50)
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    })
    
    # 尝试获取更多数据
    url = 'http://push2.eastmoney.com/api/qt/clist/get'
    params = {
        'pn': '1',
        'pz': '5000',  # 尝试获取5000条
        'po': '1',
        'np': '1',
        'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
        'fltt': '2',
        'invt': '2',
        'fid': 'f3',
        'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',
        'fields': 'f12,f14'  # 只获取代码和名称
    }
    
    try:
        print("正在获取完整股票数据...")
        response = session.get(url, params=params, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('rc') == 0 and 'data' in data and 'diff' in data['data']:
                stocks_data = data['data']['diff']
                total_count = len(stocks_data)
                
                print(f"✅ 成功获取 {total_count} 条股票数据")
                
                # 统计市场分布
                sh_count = 0
                sz_count = 0
                for stock in stocks_data:
                    code = stock.get('f12', '')
                    if code.startswith('6'):
                        sh_count += 1
                    elif code.startswith(('0', '2', '3')):
                        sz_count += 1
                
                print(f"上海证券交易所: {sh_count} 只")
                print(f"深圳证券交易所: {sz_count} 只")
                
                # 检查是否达到目标
                if total_count >= 1693:
                    print("🎉 达到目标数据量!")
                elif total_count >= 1000:
                    print("✅ 获取到大量数据")
                else:
                    print("⚠️ 数据量不足1000条")
                
                return total_count
                
    except Exception as e:
        print(f"获取完整数据失败: {e}")
    
    return 0

if __name__ == "__main__":
    # 先测试小量数据
    test_count = test_eastmoney_api()
    
    if test_count > 0:
        # 如果测试成功，尝试获取完整数据
        total_count = test_full_data()
        
        if total_count >= 1693:
            print("\n🎉 东方财富API可以获取到目标数量的股票数据!")
            print("可以使用此API进行完整数据爬取。")
        else:
            print(f"\n⚠️ 东方财富API获取到 {total_count} 条数据，未达到1693条目标。")
    else:
        print("\n❌ 东方财富API测试失败")