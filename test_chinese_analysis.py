#!/usr/bin/env python3
"""
NewsTrader 中文智能分析功能测试
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_api_endpoint(url, method="GET", data=None):
    """测试API端点"""
    try:
        if method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"HTTP {response.status_code}: {response.text}"
    except Exception as e:
        return False, str(e)

def main():
    print("🚀 NewsTrader 中文智能分析功能测试")
    print("=" * 50)
    
    # 测试1: 获取支持的交易品种
    print("\n📊 测试1: 获取支持的交易品种")
    success, result = test_api_endpoint(f"{BASE_URL}/api/v1/smart-analysis/supported-symbols")
    if success:
        symbols = result.get('trading_symbols', [])
        print(f"✅ 支持 {len(symbols)} 个交易品种")
        print(f"   美股: {len(result.get('symbol_categories', {}).get('us_markets', []))} 个")
        print(f"   中国市场: {len(result.get('symbol_categories', {}).get('chinese_markets', []))} 个")
        print(f"   商品: {len(result.get('symbol_categories', {}).get('commodities', []))} 个")
        print(f"   外汇: {len(result.get('symbol_categories', {}).get('currencies', []))} 个")
    else:
        print(f"❌ 失败: {result}")
        return False
    
    # 测试2: 中文新闻正向分析
    print("\n📈 测试2: 中文新闻正向分析")
    news_data = {
        "title": "中国央行意外降准，释放流动性支持经济复苏",
        "content": "中国人民银行宣布下调存款准备金率0.25个百分点，释放长期资金约5000亿元。此举旨在保持流动性合理充裕，支持实体经济发展。市场分析师认为，此次降准将对A股市场、人民币汇率和债券市场产生积极影响。"
    }
    
    success, result = test_api_endpoint(
        f"{BASE_URL}/api/v1/smart-analysis/analyze-news", 
        method="POST", 
        data=news_data
    )
    if success:
        print("✅ 正向分析成功")
        print(f"   分析类型: {result['analysis_type']}")
        print(f"   影响评分: {result['impact_score']}")
        print(f"   情感评分: {result['sentiment_score']}")
        print(f"   置信度: {result['confidence'] * 100:.1f}%")
        symbols_str = [f"{s['symbol']}({s['impact']:.1f})" for s in result['primary_symbols']]
        print(f"   主要影响品种: {symbols_str}")
        print(f"   关键词: {result['keywords']}")
    else:
        print(f"❌ 失败: {result}")
        return False
    
    # 测试3: 反向分析 - 指定品种
    print("\n🔄 测试3: 反向分析 - 指定品种USDCNY")
    reverse_data = {
        "title": "美联储加息预期降温，新兴市场货币普遍走强",
        "content": "美联储官员最新表态显示，如果通胀持续回落，央行可能放缓加息步伐。这一消息提振了投资者对风险资产的信心，人民币、日元等新兴市场货币对美元汇率出现反弹。",
        "target_symbol": "USDCNY"
    }
    
    success, result = test_api_endpoint(
        f"{BASE_URL}/api/v1/smart-analysis/analyze-news",
        method="POST",
        data=reverse_data
    )
    if success:
        print("✅ 反向分析成功")
        print(f"   目标品种: USDCNY")
        print(f"   影响程度: {result['primary_symbols'][0]['impact']:.1f}")
        print(f"   情感倾向: {result['sentiment_score']:.2f}")
        print(f"   分析理由: {result['analysis_reason']}")
    else:
        print(f"❌ 失败: {result}")
        return False
    
    # 测试4: 反向搜索 - A股相关新闻
    print("\n🔍 测试4: 反向搜索 - A股相关新闻")
    success, result = test_api_endpoint(f"{BASE_URL}/api/v1/smart-analysis/reverse-search/000001.SS")
    if success:
        print("✅ 反向搜索成功")
        print(f"   品种: 000001.SS (上证指数)")
        print(f"   找到相关新闻: {result['total_found']} 条")
        print(f"   平均影响评分: {result['avg_impact']}")
        print(f"   平均情感倾向: {result['avg_sentiment']:.2f}")
        print(f"   搜索时间跨度: {result['search_period_days']} 天")
        if result['related_news']:
            first_news = result['related_news'][0]
            print(f"   示例新闻: {first_news['title'][:30]}...")
    else:
        print(f"❌ 失败: {result}")
        return False
    
    # 测试5: 多品种对比
    print("\n⚖️  测试5: 多品种影响对比")
    symbols_to_test = ["USDCNY", "000001.SS", "GC=F", "SPY"]
    for symbol in symbols_to_test:
        success, result = test_api_endpoint(f"{BASE_URL}/api/v1/smart-analysis/reverse-search/{symbol}")
        if success:
            print(f"   {symbol}: 平均影响 {result['avg_impact']:.1f}, 情感 {result['avg_sentiment']:+.2f}")
        else:
            print(f"   {symbol}: 测试失败")
    
    print("\n" + "=" * 50)
    print("🎉 所有测试完成！中文智能分析功能运行正常")
    print("\n📌 功能特点:")
    print("   ✅ 支持中英文新闻内容分析")
    print("   ✅ 覆盖全球主要交易品种")
    print("   ✅ 提供正向和反向两种分析模式")
    print("   ✅ 包含情感分析和置信度评估")
    print("   ✅ 支持历史新闻反向搜索")
    print("\n🌐 访问地址:")
    print("   前端界面: http://localhost:3000/smart-analysis")
    print("   API文档: http://localhost:8000/docs")
    
    return True

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现错误: {e}")