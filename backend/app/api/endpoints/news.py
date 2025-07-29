from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.news import NewsArticle
from app.services.news_scraper import NewsScraperService
from app.mcp.claude_client import ClaudeAnalyzer
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/articles")
async def get_articles(
    limit: int = 50,
    offset: int = 0,
    symbol: Optional[str] = None,
    min_impact: Optional[float] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get news articles with optional filtering"""
    query = select(NewsArticle).order_by(NewsArticle.published_at.desc())
    
    if symbol:
        query = query.where(NewsArticle.affected_symbols.contains([symbol]))
    
    if min_impact is not None:
        query = query.where(NewsArticle.impact_score >= min_impact)
    
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return [
        {
            "id": str(article.id),
            "title": article.title,
            "summary": article.summary,
            "url": article.url,
            "source": article.source,
            "published_at": article.published_at,
            "impact_score": article.impact_score,
            "sentiment_score": article.sentiment_score,
            "affected_symbols": article.affected_symbols,
            "confidence_score": article.confidence_score,
        }
        for article in articles
    ]


@router.get("/articles/{article_id}")
async def get_article(article_id: str, db: AsyncSession = Depends(get_db)):
    """Get single article with full details"""
    query = select(NewsArticle).where(NewsArticle.id == article_id)
    result = await db.execute(query)
    article = result.scalar_one_or_none()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    
    return {
        "id": str(article.id),
        "title": article.title,
        "content": article.content,
        "summary": article.summary,
        "url": article.url,
        "source": article.source,
        "published_at": article.published_at,
        "created_at": article.created_at,
        "impact_score": article.impact_score,
        "sentiment_score": article.sentiment_score,
        "affected_symbols": article.affected_symbols,
        "keywords": article.keywords,
        "categories": article.categories,
        "claude_analysis": article.claude_analysis,
        "confidence_score": article.confidence_score,
    }


@router.post("/scrape")
async def scrape_news(db: AsyncSession = Depends(get_db)):
    """Manually trigger news scraping"""
    try:
        async with NewsScraperService() as scraper:
            articles_data = await scraper.scrape_all_sources()
        
        if not articles_data:
            return {"message": "No new articles found", "count": 0}
        
        # Analyze articles with Claude
        claude_analyzer = ClaudeAnalyzer()
        analyses = await claude_analyzer.batch_analyze(
            articles_data,
            settings.TRADING_SYMBOLS
        )
        
        # Save to database
        saved_count = 0
        for article_data, analysis in zip(articles_data, analyses):
            # Check if article already exists
            existing_query = select(NewsArticle).where(
                NewsArticle.url == article_data['url']
            )
            existing_result = await db.execute(existing_query)
            if existing_result.scalar_one_or_none():
                continue
            
            # Create new article
            article = NewsArticle(
                title=article_data['title'],
                content=article_data['content'],
                summary=article_data['summary'],
                url=article_data['url'],
                source=article_data['source'],
                published_at=article_data['published_at'],
                impact_score=analysis['impact_score'],
                sentiment_score=analysis['sentiment_score'],
                affected_symbols=[s['symbol'] for s in analysis['affected_symbols']],
                keywords=analysis['key_factors'],
                categories=analysis['categories'],
                claude_analysis=analysis,
                confidence_score=analysis['confidence_score'],
            )
            
            db.add(article)
            saved_count += 1
        
        await db.commit()
        
        return {
            "message": f"Scraped and analyzed {saved_count} new articles",
            "count": saved_count
        }
        
    except Exception as e:
        logger.error(f"News scraping failed: {e}")
        raise HTTPException(status_code=500, detail="Scraping failed")


@router.get("/trending")
async def get_trending_news(
    hours: int = 24,
    min_impact: float = 5.0,
    db: AsyncSession = Depends(get_db)
):
    """Get trending high-impact news from last N hours"""
    since = datetime.utcnow() - timedelta(hours=hours)
    
    query = select(NewsArticle).where(
        NewsArticle.published_at >= since,
        NewsArticle.impact_score >= min_impact
    ).order_by(NewsArticle.impact_score.desc()).limit(20)
    
    result = await db.execute(query)
    articles = result.scalars().all()
    
    return [
        {
            "id": str(article.id),
            "title": article.title,
            "summary": article.summary,
            "source": article.source,
            "published_at": article.published_at,
            "impact_score": article.impact_score,
            "sentiment_score": article.sentiment_score,
            "affected_symbols": article.affected_symbols,
        }
        for article in articles
    ]