"""
智能分析API - 支持正向和反向新闻影响分析
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta

from app.services.chinese_news_analyzer import chinese_analyzer, NewsAnalysisRequest
from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/smart-analysis", tags=["Smart Analysis"])

# Request/Response模型
class NewsAnalysisRequestModel(BaseModel):
    """新闻分析请求模型"""
    title: str
    content: str
    target_symbol: Optional[str] = None
    
class SmartAnalysisResponse(BaseModel):
    """智能分析响应模型"""
    analysis_type: str  # "forward" 或 "reverse"
    primary_symbols: List[Dict[str, Any]]
    secondary_symbols: List[Dict[str, Any]]
    sentiment_score: float
    impact_score: float
    confidence: float
    keywords: List[str]
    analysis_reason: str
    analysis_timestamp: str

class ReverseSearchRequest(BaseModel):
    """反向搜索请求模型"""
    symbol: str
    days_back: int = 7
    min_impact_score: float = 3.0

class ReverseSearchResponse(BaseModel):
    """反向搜索响应模型"""
    symbol: str
    related_news: List[Dict[str, Any]]
    total_found: int
    search_period_days: int
    avg_impact: float
    avg_sentiment: float

@router.post("/analyze-news", response_model=SmartAnalysisResponse)
async def analyze_news_content(request: NewsAnalysisRequestModel):
    """
    智能新闻分析
    
    支持两种模式：
    1. 正向分析：自动判断哪些交易品种最受影响
    2. 反向分析：分析新闻对指定品种的影响程度
    """
    try:
        # 创建分析请求
        analysis_request = NewsAnalysisRequest(
            title=request.title,
            content=request.content,
            target_symbol=request.target_symbol
        )
        
        # 执行分析
        result = chinese_analyzer.analyze_news(analysis_request)
        
        # 确定分析类型
        analysis_type = "reverse" if request.target_symbol else "forward"
        
        return SmartAnalysisResponse(
            analysis_type=analysis_type,
            primary_symbols=result.primary_symbols,
            secondary_symbols=result.secondary_symbols,
            sentiment_score=result.sentiment_score,
            impact_score=result.impact_score,
            confidence=result.confidence,
            keywords=result.keywords,
            analysis_reason=result.analysis_reason,
            analysis_timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"News analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"分析失败: {str(e)}")

@router.get("/reverse-search/{symbol}", response_model=ReverseSearchResponse)
async def reverse_search_news(
    symbol: str,
    days_back: int = Query(7, description="搜索天数", ge=1, le=30),
    min_impact_score: float = Query(3.0, description="最小影响评分", ge=0.0, le=10.0),
    limit: int = Query(20, description="返回数量限制", ge=1, le=100)
):
    """
    反向搜索：根据交易品种查找最相关的新闻
    
    这是一个模拟实现，在实际部署时需要：
    1. 连接真实的新闻数据库
    2. 对历史新闻进行批量分析
    3. 建立品种-新闻关联索引
    """
    try:
        # 模拟数据 - 实际实现中应该查询数据库
        sample_news = _get_sample_news_for_symbol(symbol, days_back, min_impact_score, limit)
        
        # 计算统计信息
        total_found = len(sample_news)
        avg_impact = sum(news["impact_score"] for news in sample_news) / max(total_found, 1)
        avg_sentiment = sum(news["sentiment_score"] for news in sample_news) / max(total_found, 1)
        
        return ReverseSearchResponse(
            symbol=symbol,
            related_news=sample_news,
            total_found=total_found,
            search_period_days=days_back,
            avg_impact=round(avg_impact, 2),
            avg_sentiment=round(avg_sentiment, 3)
        )
        
    except Exception as e:
        logger.error(f"Reverse search failed for {symbol}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"反向搜索失败: {str(e)}")

@router.get("/supported-symbols")
async def get_supported_symbols():
    """获取支持的交易品种列表"""
    return {
        "trading_symbols": settings.TRADING_SYMBOLS,
        "symbol_categories": {
            "us_markets": ["SPY", "QQQ", "GLD", "CL=F", "GC=F", "ES=F"],
            "chinese_markets": ["000001.SS", "399001.SZ", "HSI", "BABA", "JD", "TCEHY"],
            "commodities": ["XAUUSD", "XAGUSD", "USOIL", "BRENT"],
            "currencies": ["USDCNY", "EURUSD", "GBPUSD"]
        },
        "chinese_keywords": settings.CHINESE_MARKET_KEYWORDS
    }

@router.post("/batch-analyze")
async def batch_analyze_news(
    news_list: List[NewsAnalysisRequestModel],
    target_symbol: Optional[str] = None
):
    """
    批量新闻分析
    
    可以一次性分析多条新闻，支持：
    1. 批量正向分析：找出对市场影响最大的新闻
    2. 批量反向分析：分析多条新闻对指定品种的累计影响
    """
    try:
        results = []
        
        for news_item in news_list:
            # 如果指定了全局目标品种，覆盖单个请求的设置
            analysis_target = target_symbol or news_item.target_symbol
            
            analysis_request = NewsAnalysisRequest(
                title=news_item.title,
                content=news_item.content,
                target_symbol=analysis_target
            )
            
            result = chinese_analyzer.analyze_news(analysis_request)
            
            results.append({
                "title": news_item.title[:50] + "..." if len(news_item.title) > 50 else news_item.title,
                "analysis_type": "reverse" if analysis_target else "forward",
                "primary_symbols": result.primary_symbols,
                "impact_score": result.impact_score,
                "sentiment_score": result.sentiment_score,
                "confidence": result.confidence,
                "keywords": result.keywords[:5],  # 只返回前5个关键词
                "analysis_reason": result.analysis_reason
            })
        
        # 如果是反向分析，计算累计影响
        if target_symbol:
            cumulative_impact = sum(r["impact_score"] for r in results) / len(results)
            cumulative_sentiment = sum(r["sentiment_score"] for r in results) / len(results)
            
            return {
                "analysis_type": "batch_reverse",
                "target_symbol": target_symbol,
                "individual_results": results,
                "cumulative_analysis": {
                    "avg_impact": round(cumulative_impact, 2),
                    "avg_sentiment": round(cumulative_sentiment, 3),
                    "total_articles": len(results),
                    "high_impact_count": len([r for r in results if r["impact_score"] > 6]),
                    "positive_sentiment_count": len([r for r in results if r["sentiment_score"] > 0.2])
                }
            }
        else:
            return {
                "analysis_type": "batch_forward",
                "individual_results": results,
                "total_articles": len(results)
            }
        
    except Exception as e:
        logger.error(f"Batch analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"批量分析失败: {str(e)}")

def _get_sample_news_for_symbol(symbol: str, days_back: int, min_impact: float, limit: int) -> List[Dict]:
    """
    获取指定品种的相关新闻样本数据
    
    实际实现中应该：
    1. 查询数据库中的历史新闻
    2. 使用预先分析的结果或实时分析
    3. 按照影响评分和时间排序
    """
    
    # 基于品种生成样本新闻
    sample_news_templates = {
        "USDCNY": [
            {
                "title": "央行宣布调整外汇市场政策，人民币汇率或将面临新变化",
                "content": "中国人民银行今日发布公告，将对外汇市场相关政策进行调整...",
                "impact_score": 8.5,
                "sentiment_score": -0.2
            },
            {
                "title": "美联储加息预期升温，人民币兑美元汇率承压",
                "content": "随着美国通胀数据超预期，市场对美联储加息的预期进一步升温...",
                "impact_score": 7.2,
                "sentiment_score": -0.4
            }
        ],
        "000001.SS": [
            {
                "title": "A股三大股指集体上涨，上证指数重返3000点上方",
                "content": "今日A股市场表现强劲，上证指数、深证成指、创业板指均收涨...",
                "impact_score": 6.8,
                "sentiment_score": 0.6
            },
            {
                "title": "监管层释放积极信号，A股市场信心逐步恢复",
                "content": "证监会相关负责人表示将继续推进资本市场改革...",
                "impact_score": 7.5,
                "sentiment_score": 0.3
            }
        ],
        "GC=F": [
            {
                "title": "地缘政治紧张局势升级，黄金价格创近期新高",
                "content": "受国际地缘政治因素影响，投资者避险情绪升温，现货黄金价格...",
                "impact_score": 8.0,
                "sentiment_score": 0.4
            },
            {
                "title": "美元走强施压，黄金期货价格承压下行",
                "content": "美元指数持续走强，对以美元计价的黄金形成压制...",
                "impact_score": 6.5,
                "sentiment_score": -0.3
            }
        ]
    }
    
    # 获取对应品种的样本数据，如果没有则使用通用模板
    news_templates = sample_news_templates.get(symbol, [
        {
            "title": f"市场分析：{symbol} 相关新闻动态",
            "content": f"关于 {symbol} 的最新市场动态和分析...",
            "impact_score": 5.5,
            "sentiment_score": 0.0
        }
    ])
    
    # 生成指定数量的样本，过滤低影响评分的新闻
    result = []
    for i, template in enumerate(news_templates * ((limit // len(news_templates)) + 1)):
        if len(result) >= limit:
            break
            
        if template["impact_score"] >= min_impact:
            news_item = template.copy()
            news_item.update({
                "id": f"sample_{symbol}_{i}",
                "published_at": (datetime.now() - timedelta(days=i % days_back)).isoformat(),
                "source": "财经新闻",
                "url": f"https://example.com/news/{symbol}_{i}",
                "confidence": 0.75 + (i % 3) * 0.08,  # 0.75-0.91之间
            })
            result.append(news_item)
    
    return result[:limit]