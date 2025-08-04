#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票API功能
"""

import requests
import json
import time

def test_stock_apis():
    """测试股票相关API"""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("测试股票API功能")
    print("=" * 60)
    
    # 1. 测试导入股票数据
    print("\n1. 测试导入股票数据...")
    
    # 读取爬取的股票数据
    try:
        with open('a_stock_list.json', 'r', encoding='utf-8') as f:
            stock_data = json.load(f)
        
        import_payload = {"stocks": stock_data}
        
        response = requests.post(f"{base_url}/api/v1/stocks/import", 
                               json=import_payload, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 导入成功: {result}")
        else:
            print(f"❌ 导入失败: {response.status_code} - {response.text}")
            
    except FileNotFoundError:
        print("❌ 未找到股票数据文件，请先运行stock_crawler.py")
        return
    except Exception as e:
        print(f"❌ 导入请求失败: {e}")
        return
    
    time.sleep(1)
    
    # 2. 测试获取股票列表
    print("\n2. 测试获取股票列表...")
    try:
        response = requests.get(f"{base_url}/api/v1/stocks/a-stocks?limit=10")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取股票列表成功，返回 {result['returned_count']} 只股票")
            print("前5只股票:")
            for i, stock in enumerate(result['stocks'][:5]):
                print(f"  {i+1}. {stock['code']} - {stock['name']} ({stock['exchange']})")
        else:
            print(f"❌ 获取股票列表失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取股票列表请求失败: {e}")
    
    time.sleep(1)
    
    # 3. 测试获取单只股票详情
    print("\n3. 测试获取单只股票详情...")
    try:
        test_code = "600519"  # 贵州茅台
        response = requests.get(f"{base_url}/api/v1/stocks/a-stocks/{test_code}")
        if response.status_code == 200:
            stock = response.json()
            print(f"✅ 获取股票详情成功:")
            print(f"  代码: {stock['code']}")
            print(f"  名称: {stock['name']}")
            print(f"  全称: {stock['full_name']}")
            print(f"  上市日期: {stock['list_date']}")
            print(f"  行业: {stock['industry']}")
            print(f"  地区: {stock['area']}")
        else:
            print(f"❌ 获取股票详情失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取股票详情请求失败: {e}")
    
    time.sleep(1)
    
    # 4. 测试股票统计信息
    print("\n4. 测试股票统计信息...")
    try:
        response = requests.get(f"{base_url}/api/v1/stocks/stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 获取统计信息成功:")
            print(f"  总股票数: {stats['total_stocks']}")
            print(f"  按市场分布: {stats['by_market']}")
            print(f"  前5个行业: {dict(list(stats['by_industry'].items())[:5])}")
            print(f"  前5个地区: {dict(list(stats['by_area'].items())[:5])}")
        else:
            print(f"❌ 获取统计信息失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 获取统计信息请求失败: {e}")
    
    time.sleep(1)
    
    # 5. 测试运行爬虫API
    print("\n5. 测试运行爬虫API...")
    try:
        response = requests.post(f"{base_url}/api/v1/stocks/crawler/run", timeout=60)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 爬虫运行结果: {result}")
        else:
            print(f"❌ 爬虫运行失败: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ 爬虫运行请求失败: {e}")
    
    time.sleep(1)
    
    # 6. 测试品种搜索功能
    print("\n6. 测试品种搜索功能...")
    try:
        search_terms = ["茅台", "平安", "银行"]
        
        for term in search_terms:
            response = requests.get(f"{base_url}/api/v1/symbols/search?q={term}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 搜索 '{term}' 结果: 找到 {len(result['results'])} 个匹配项")
                for item in result['results'][:3]:  # 显示前3个结果
                    print(f"  - {item['symbol']}: {item['name']} ({item['category']})")
            else:
                print(f"❌ 搜索 '{term}' 失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 搜索请求失败: {e}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

def check_backend_status():
    """检查后端服务状态"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ 后端服务运行正常")
            return True
        else:
            print(f"❌ 后端服务异常: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到后端服务: {e}")
        print("请确保后端服务已启动: python3 simple_backend.py")
        return False

if __name__ == "__main__":
    if check_backend_status():
        test_stock_apis()
    else:
        print("\n请先启动后端服务，然后重新运行此测试脚本")