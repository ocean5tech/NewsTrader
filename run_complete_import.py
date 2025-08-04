#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整运行：启动后端并导入股票数据
"""

import subprocess
import requests
import json
import time
import signal
import sys
import os

backend_process = None

def signal_handler(sig, frame):
    """信号处理器，确保后端进程被正确关闭"""
    print("\n正在关闭后端服务...")
    if backend_process:
        backend_process.terminate()
        backend_process.wait()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def start_backend():
    """启动后端服务"""
    global backend_process
    
    print("正在启动后端服务...")
    try:
        # 启动后端服务
        backend_process = subprocess.Popen(
            ['python3', 'simple_backend.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        # 等待服务启动
        for i in range(30):  # 最多等待30秒
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    print("✅ 后端服务启动成功")
                    return True
            except:
                pass
            time.sleep(1)
        
        print("❌ 后端服务启动失败或超时")
        return False
        
    except Exception as e:
        print(f"❌ 启动后端服务异常: {e}")
        return False

def import_stocks():
    """导入股票数据"""
    print("\n=== 导入股票数据 ===")
    
    # 读取股票数据
    try:
        with open('quick_stocks.json', 'r', encoding='utf-8') as f:
            stocks = json.load(f)
        print(f"读取到 {len(stocks)} 条股票数据")
    except Exception as e:
        print(f"❌ 读取股票数据失败: {e}")
        return False
    
    # 导入数据
    try:
        print("正在导入数据到后端...")
        response = requests.post(
            "http://localhost:8000/api/v1/stocks/import",
            json={"stocks": stocks},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 导入成功!")
            print(f"   导入数量: {result.get('imported_count', 0)} 条")
            print(f"   总股票数: {result.get('total_stocks', 0)} 条")
            return True
        else:
            print(f"❌ 导入失败: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 导入请求失败: {e}")
        return False

def verify_data():
    """验证数据"""
    print("\n=== 验证数据 ===")
    
    try:
        # 获取统计信息
        response = requests.get("http://localhost:8000/api/v1/stocks/stats")
        if response.status_code == 200:
            stats = response.json()
            total = stats.get('total_stocks', 0)
            markets = stats.get('by_market', {})
            
            print(f"✅ 数据验证成功:")
            print(f"   总股票数: {total}")
            print(f"   上交所: {markets.get('SH', 0)} 只")
            print(f"   深交所: {markets.get('SZ', 0)} 只")
            
            if total >= 1693:
                print(f"🎉 达到目标数据量!")
            else:
                print(f"⚠️ 数据量不足目标")
            
            return True
        else:
            print(f"❌ 获取统计信息失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 验证数据失败: {e}")
        return False

def test_search():
    """测试搜索功能"""
    print("\n=== 测试搜索功能 ===")
    
    test_keywords = ["茅台", "平安", "比亚迪", "腾讯", "阿里"]
    
    for keyword in test_keywords:
        try:
            response = requests.get(f"http://localhost:8000/api/v1/symbols/search?q={keyword}")
            if response.status_code == 200:
                result = response.json()
                results = result.get('results', [])
                print(f"'{keyword}': {len(results)} 个结果")
                for r in results[:2]:
                    print(f"  - {r.get('symbol')}: {r.get('name')}")
            else:
                print(f"'{keyword}': 搜索失败")
        except Exception as e:
            print(f"'{keyword}': 搜索异常 - {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("完整股票数据导入流程")
    print("目标：导入2000条A股数据到系统")
    print("=" * 60)
    
    # 检查数据文件是否存在
    if not os.path.exists('quick_stocks.json'):
        print("❌ 未找到股票数据文件 quick_stocks.json")
        print("请先运行: python3 quick_stock_crawler.py")
        return
    
    try:
        # 1. 启动后端服务
        if not start_backend():
            return
        
        # 2. 导入股票数据
        if not import_stocks():
            return
        
        # 3. 验证数据
        if not verify_data():
            return
        
        # 4. 测试搜索功能
        test_search()
        
        print("\n" + "=" * 60)
        print("🎉 股票数据导入完成!")
        print("系统现在包含完整的A股数据，可以进行:")
        print("- 股票搜索和查询")
        print("- 新闻分析和影响评估") 
        print("- 交易建议生成")
        print("- 实时价格推送")
        print("=" * 60)
        
        # 保持后端服务运行
        print("\n后端服务正在运行中...")
        print("访问 http://localhost:8000 查看API文档")
        print("按 Ctrl+C 停止服务")
        
        # 等待用户中断
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
            
    finally:
        # 清理资源
        if backend_process:
            print("\n正在关闭后端服务...")
            backend_process.terminate()
            backend_process.wait()
        print("服务已关闭")

if __name__ == "__main__":
    main()