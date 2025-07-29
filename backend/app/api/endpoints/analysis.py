from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.news import NewsArticle, ImpactWeight
from app.mcp.claude_client import ClaudeAnalyzer
from pydantic import BaseModel

router = APIRouter()


class ArticleAnalysisRequest(BaseModel):
    title: str
    content: str
    symbols: List[str] = []


@router.post("/analyze")
async def analyze_article(
    request: ArticleAnalysisRequest,
    db: AsyncSession = Depends(get_db)
):
    """Analyze a single article for trading impact"""
    try:
        claude_analyzer = ClaudeAnalyzer()
        analysis = await claude_analyzer.analyze_news_impact(
            request.title,
            request.content,
            request.symbols or ["SPY", "QQQ", "GLD"]
        )
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/market-sentiment")
async def get_market_sentiment(
    symbol: str = "SPY",
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get overall market sentiment for a symbol"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    # Get articles affecting the symbol
    query = select(NewsArticle).where(
        NewsArticle.published_at >= since,
        NewsArticle.affected_symbols.contains([symbol])
    )
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    if not articles:
        return {
            "symbol": symbol,
            "sentiment_score": 0.0,
            "impact_score": 0.0,
            "article_count": 0,
            "confidence": 0.0
        }
    
    # Calculate weighted averages
    total_sentiment = sum(a.sentiment_score * a.confidence_score for a in articles)
    total_impact = sum(a.impact_score * a.confidence_score for a in articles)
    total_confidence = sum(a.confidence_score for a in articles)
    
    avg_sentiment = total_sentiment / total_confidence if total_confidence > 0 else 0
    avg_impact = total_impact / total_confidence if total_confidence > 0 else 0
    avg_confidence = total_confidence / len(articles) if articles else 0
    
    return {
        "symbol": symbol,
        "sentiment_score": round(avg_sentiment, 3),
        "impact_score": round(avg_impact, 3),
        "article_count": len(articles),
        "confidence": round(avg_confidence, 3),
        "time_period_hours": hours
    }


@router.get("/impact-summary")
async def get_impact_summary(
    hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Get impact summary for all tracked symbols"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(NewsArticle).where(
        NewsArticle.published_at >= since,
        NewsArticle.impact_score > 0
    )
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    # Group by symbols
    symbol_impacts = {}
    
    for article in articles:
        if not article.affected_symbols:
            continue
            
        for symbol in article.affected_symbols:
            if symbol not in symbol_impacts:
                symbol_impacts[symbol] = {
                    "articles": [],
                    "total_impact": 0,
                    "avg_sentiment": 0,
                    "confidence": 0
                }
            
            symbol_impacts[symbol]["articles"].append(article)
            symbol_impacts[symbol]["total_impact"] += article.impact_score
    
    # Calculate averages
    summary = []
    for symbol, data in symbol_impacts.items():
        articles_list = data["articles"]
        if not articles_list:
            continue
            
        avg_sentiment = sum(a.sentiment_score for a in articles_list) / len(articles_list)
        avg_confidence = sum(a.confidence_score for a in articles_list) / len(articles_list)
        
        summary.append({
            "symbol": symbol,
            "article_count": len(articles_list),
            "total_impact": round(data["total_impact"], 2),
            "avg_impact": round(data["total_impact"] / len(articles_list), 2),
            "avg_sentiment": round(avg_sentiment, 3),
            "avg_confidence": round(avg_confidence, 3),
            "latest_article": max(articles_list, key=lambda x: x.published_at).published_at
        })
    
    # Sort by total impact
    summary.sort(key=lambda x: x["total_impact"], reverse=True)
    
    return {
        "summary": summary,
        "time_period_hours": hours,
        "total_articles": len(articles)
    }


@router.get("/keyword-trends")
async def get_keyword_trends(
    days: int = 7,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get trending keywords from news analysis"""
    since = datetime.utcnow() - timedelta(days=days)
    
    query = select(NewsArticle).where(
        NewsArticle.published_at >= since,
        NewsArticle.keywords.isnot(None)
    )
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    # Count keyword frequency
    keyword_counts = {}
    keyword_impact = {}
    
    for article in articles:
        if not article.keywords:
            continue
            
        for keyword in article.keywords:
            if keyword not in keyword_counts:
                keyword_counts[keyword] = 0
                keyword_impact[keyword] = []
            
            keyword_counts[keyword] += 1
            keyword_impact[keyword].append(article.impact_score)
    
    # Calculate trends
    trends = []
    for keyword, count in keyword_counts.items():
        if count < 2:  # Filter out rare keywords
            continue
            
        avg_impact = sum(keyword_impact[keyword]) / len(keyword_impact[keyword])
        
        trends.append({
            "keyword": keyword,
            "frequency": count,
            "avg_impact": round(avg_impact, 2),
            "total_impact": round(sum(keyword_impact[keyword]), 2)
        })
    
    # Sort by frequency and impact
    trends.sort(key=lambda x: (x["frequency"], x["avg_impact"]), reverse=True)
    
    return {
        "trends": trends[:limit],
        "time_period_days": days,
        "total_articles": len(articles)
    }