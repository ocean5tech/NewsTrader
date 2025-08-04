#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将爬取的股票数据导入到Backend系统
"""

import requests
import json
import time

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

def import_stocks_to_backend(stocks_file='quick_stocks.json'):
    """导入股票数据到后端"""
    # 检查后端服务
    if not check_backend_status():
        return False
    
    # 读取股票数据
    try:
        with open(stocks_file, 'r', encoding='utf-8') as f:
            stocks = json.load(f)
        print(f"成功读取 {len(stocks)} 条股票数据")
    except FileNotFoundError:
        print(f"❌ 未找到股票数据文件: {stocks_file}")
        return False
    except Exception as e:
        print(f"❌ 读取股票数据失败: {e}")
        return False
    
    # 导入数据到后端
    try:
        print("正在导入股票数据到后端...")
        
        import_payload = {"stocks": stocks}
        response = requests.post(
            "http://localhost:8000/api/v1/stocks/import",
            json=import_payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 导入成功!")
            print(f"   导入数量: {result.get('imported_count', 0)} 条")
            print(f"   总股票数: {result.get('total_stocks', 0)} 条")
            print(f"   消息: {result.get('message', '')}")
            return True
        else:
            print(f"❌ 导入失败: {response.status_code}")
            print(f"   响应: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 导入请求失败: {e}")
        return False

def verify_import():
    """验证导入结果"""
    try:
        print("\n=== 验证导入结果 ===")
        
        # 1. 获取股票统计信息
        response = requests.get("http://localhost:8000/api/v1/stocks/stats", timeout=10)
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ 统计信息:")
            print(f"   总股票数: {stats.get('total_stocks', 0)}")
            print(f"   上交所: {stats.get('by_market', {}).get('SH', 0)} 只")
            print(f"   深交所: {stats.get('by_market', {}).get('SZ', 0)} 只")
            
            # 显示前5个行业
            industries = stats.get('by_industry', {})
            if industries:
                print("   主要行业:")
                for industry, count in list(industries.items())[:5]:
                    print(f"     {industry}: {count} 只")
        else:
            print(f"❌ 获取统计信息失败: {response.status_code}")
        
        # 2. 获取股票列表样本
        response = requests.get("http://localhost:8000/api/v1/stocks/a-stocks?limit=10", timeout=10)
        if response.status_code == 200:
            result = response.json()
            stocks = result.get('stocks', [])
            print(f"\n✅ 股票列表预览 (前10条):")
            for i, stock in enumerate(stocks[:10]):
                print(f"   {i+1:2d}. {stock.get('code')} - {stock.get('name')} ({stock.get('exchange')})")
        else:
            print(f"❌ 获取股票列表失败: {response.status_code}")
        
        # 3. 测试搜索功能
        test_keywords = ["茅台", "平安", "比亚迪"]
        print(f"\n✅ 搜索功能测试:")
        for keyword in test_keywords:
            response = requests.get(f"http://localhost:8000/api/v1/symbols/search?q={keyword}", timeout=10)
            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])
                print(f"   '{keyword}': 找到 {len(results)} 个结果")
                for r in results[:2]:  # 显示前2个结果
                    print(f"     - {r.get('symbol')}: {r.get('name')}")
            else:
                print(f"   '{keyword}': 搜索失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def run_crawler_api():
    """测试运行爬虫API（可选）"""
    try:
        print("\n=== 测试爬虫API ===")
        response = requests.post("http://localhost:8000/api/v1/stocks/crawler/run", timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 爬虫API测试成功:")
            print(f"   状态: {result.get('success', False)}")
            print(f"   消息: {result.get('message', '')}")
            print(f"   爬取数量: {result.get('crawled_count', 0)}")
            print(f"   更新数量: {result.get('updated_count', 0)}")
            print(f"   总股票数: {result.get('total_stocks', 0)}")
            return True
        else:
            print(f"❌ 爬虫API测试失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 爬虫API测试异常: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("股票数据导入工具")
    print("=" * 60)
    
    # 1. 导入股票数据
    success = import_stocks_to_backend()
    
    if success:
        # 2. 验证导入结果
        verify_import()
        
        # 3. 可选：测试爬虫API
        print(f"\n是否要测试爬虫API？(这将重新运行爬虫)")
        # run_crawler_api()  # 取消注释以启用
        
        print(f"\n🎉 股票数据导入完成!")
        print(f"现在系统中包含完整的A股数据，可以进行新闻分析和交易建议了。")
        
    else:
        print(f"\n❌ 股票数据导入失败")
        print(f"请检查后端服务状态和数据文件是否存在。")

if __name__ == "__main__":
    main()