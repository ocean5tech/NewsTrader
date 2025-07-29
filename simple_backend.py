from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("backend/.env")

app = FastAPI(
    title="News Trader API",
    description="AI-powered news analysis for trading decisions",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "News Trader API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/api/v1/news/articles")
async def get_articles():
    """Get sample news articles"""
    return [
        {
            "id": "1",
            "title": "Federal Reserve Hints at Interest Rate Changes",
            "summary": "The Federal Reserve is considering adjustments to interest rates amid economic uncertainty.",
            "url": "https://example.com/news/1",
            "source": "Reuters",
            "published_at": "2025-07-28T09:00:00Z",
            "impact_score": 8.5,
            "sentiment_score": -0.3,
            "affected_symbols": ["SPY", "QQQ"],
            "confidence_score": 0.85
        },
        {
            "id": "2", 
            "title": "Tech Stocks Rally on AI Breakthrough",
            "summary": "Major technology companies surge following announcements of new AI capabilities.",
            "url": "https://example.com/news/2",
            "source": "Bloomberg",
            "published_at": "2025-07-28T08:30:00Z",
            "impact_score": 7.2,
            "sentiment_score": 0.6,
            "affected_symbols": ["QQQ", "MSFT", "GOOGL"],
            "confidence_score": 0.92
        }
    ]

@app.get("/api/v1/news/trending")
async def get_trending_news():
    """Get trending high-impact news"""
    return [
        {
            "id": "1",
            "title": "Federal Reserve Hints at Interest Rate Changes",
            "summary": "The Federal Reserve is considering adjustments to interest rates amid economic uncertainty.",
            "source": "Reuters",
            "published_at": "2025-07-28T09:00:00Z",
            "impact_score": 8.5,
            "sentiment_score": -0.3,
            "affected_symbols": ["SPY", "QQQ"]
        }
    ]

@app.get("/api/v1/analysis/impact-summary")
async def get_impact_summary():
    """Get impact summary for symbols"""
    return {
        "summary": [
            {
                "symbol": "SPY",
                "article_count": 15,
                "total_impact": 85.3,
                "avg_impact": 5.7,
                "avg_sentiment": -0.2,
                "avg_confidence": 0.78,
                "latest_article": "2025-07-28T09:00:00Z"
            },
            {
                "symbol": "QQQ", 
                "article_count": 12,
                "total_impact": 78.4,
                "avg_impact": 6.5,
                "avg_sentiment": 0.1,
                "avg_confidence": 0.82,
                "latest_article": "2025-07-28T08:30:00Z"
            }
        ],
        "time_period_hours": 24,
        "total_articles": 25
    }

@app.get("/api/v1/analysis/keyword-trends")  
async def get_keyword_trends():
    """Get trending keywords"""
    return {
        "trends": [
            {"keyword": "interest rates", "frequency": 8, "avg_impact": 7.2, "total_impact": 57.6},
            {"keyword": "AI", "frequency": 6, "avg_impact": 6.8, "total_impact": 40.8},
            {"keyword": "inflation", "frequency": 5, "avg_impact": 6.1, "total_impact": 30.5}
        ],
        "time_period_days": 7,
        "total_articles": 45
    }

# 智能分析API端点
@app.post("/api/v1/smart-analysis/analyze-news")
async def analyze_news_smart(request: dict):
    """智能新闻分析 - 支持正向和反向分析"""
    # 模拟智能分析结果
    title = request.get("title", "")
    content = request.get("content", "")
    target_symbol = request.get("target_symbol")
    
    # 简化的关键词检测
    chinese_keywords = ["央行", "利率", "A股", "黄金", "原油", "人民币"]
    detected_keywords = [kw for kw in chinese_keywords if kw in title + content]
    
    if target_symbol:
        # 反向分析模式
        return {
            "analysis_type": "reverse",
            "primary_symbols": [{"symbol": target_symbol, "impact": 6.5}],
            "secondary_symbols": [],
            "sentiment_score": 0.2,
            "impact_score": 6.5,
            "confidence": 0.75,
            "keywords": detected_keywords[:5],
            "analysis_reason": f"针对 {target_symbol} 的专项分析；检测到相关要素；整体情感偏向积极；预期产生中等市场影响。",
            "analysis_timestamp": "2025-07-29T16:30:00Z"
        }
    else:
        # 正向分析模式
        return {
            "analysis_type": "forward", 
            "primary_symbols": [
                {"symbol": "USDCNY", "impact": 7.2},
                {"symbol": "000001.SS", "impact": 6.8},
                {"symbol": "GC=F", "impact": 5.5}
            ],
            "secondary_symbols": [
                {"symbol": "SPY", "impact": 4.2},
                {"symbol": "CL=F", "impact": 3.8}
            ],
            "sentiment_score": 0.3,
            "impact_score": 7.0,
            "confidence": 0.82,
            "keywords": detected_keywords[:5],
            "analysis_reason": "检测到关键词：央行, 利率, A股；主要影响品种：USDCNY, 000001.SS；整体情感偏向积极；预期产生重大市场影响。",
            "analysis_timestamp": "2025-07-29T16:30:00Z"
        }

@app.get("/api/v1/smart-analysis/reverse-search/{symbol}")
async def reverse_search_news(symbol: str):
    """反向搜索：根据交易品种查找相关新闻"""
    
    # 根据不同品种返回相关的样本新闻
    sample_news = {
        "USDCNY": [
            {
                "id": "news_1",
                "title": "央行宣布调整外汇市场政策，人民币汇率面临新变化",
                "content": "中国人民银行今日发布公告，将对外汇市场相关政策进行调整...",
                "impact_score": 8.5,
                "sentiment_score": -0.2,
                "published_at": "2025-07-29T10:00:00Z",
                "source": "财经新闻",
                "confidence": 0.87
            },
            {
                "id": "news_2", 
                "title": "美联储加息预期升温，人民币兑美元汇率承压",
                "content": "随着美国通胀数据超预期，市场对美联储加息的预期进一步升温...",
                "impact_score": 7.2,
                "sentiment_score": -0.4,
                "published_at": "2025-07-28T15:30:00Z",
                "source": "华尔街见闻",
                "confidence": 0.79
            }
        ],
        "000001.SS": [
            {
                "id": "news_3",
                "title": "A股三大股指集体上涨，上证指数重返3000点上方", 
                "content": "今日A股市场表现强劲，上证指数、深证成指、创业板指均收涨...",
                "impact_score": 6.8,
                "sentiment_score": 0.6,
                "published_at": "2025-07-29T09:30:00Z",
                "source": "新浪财经",
                "confidence": 0.85
            }
        ]
    }
    
    news_list = sample_news.get(symbol, [
        {
            "id": "general_1",
            "title": f"市场分析：{symbol} 相关动态",
            "content": f"关于 {symbol} 的最新市场分析和展望...",
            "impact_score": 5.5,
            "sentiment_score": 0.1,
            "published_at": "2025-07-29T08:00:00Z",
            "source": "财经分析",
            "confidence": 0.70
        }
    ])
    
    return {
        "symbol": symbol,
        "related_news": news_list,
        "total_found": len(news_list),
        "search_period_days": 7,
        "avg_impact": round(sum(n["impact_score"] for n in news_list) / len(news_list), 2),
        "avg_sentiment": round(sum(n["sentiment_score"] for n in news_list) / len(news_list), 3)
    }

@app.get("/api/v1/smart-analysis/supported-symbols")
async def get_supported_symbols():
    """获取支持的交易品种列表"""
    return {
        "trading_symbols": [
            "SPY", "QQQ", "GLD", "CL=F", "GC=F", "ES=F",
            "000001.SS", "399001.SZ", "HSI", "BABA", "JD", "TCEHY",
            "XAUUSD", "XAGUSD", "USOIL", "BRENT",
            "USDCNY", "EURUSD", "GBPUSD"
        ],
        "symbol_categories": {
            "us_markets": ["SPY", "QQQ", "GLD", "CL=F", "GC=F", "ES=F"],
            "chinese_markets": ["000001.SS", "399001.SZ", "HSI", "BABA", "JD", "TCEHY"],
            "commodities": ["XAUUSD", "XAGUSD", "USOIL", "BRENT"],
            "currencies": ["USDCNY", "EURUSD", "GBPUSD"]
        },
        "chinese_keywords": [
            "A股", "港股", "沪深", "上证", "深证", "创业板", "科创板",
            "央行", "货币政策", "利率", "MLF", "LPR",
            "GDP", "CPI", "PPI", "PMI", "通胀", "通缩",
            "房地产", "新能源", "芯片", "医药", "白酒", "银行",
            "原油", "黄金", "白银", "铜", "铁矿石",
            "中美", "贸易战", "关税", "汇率", "美联储"
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)