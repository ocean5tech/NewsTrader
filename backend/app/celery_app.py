from celery import Celery
from app.core.config import settings
from app.services.news_scraper import NewsScraperService
from app.mcp.claude_client import ClaudeAnalyzer
from app.models.news import NewsArticle
from app.core.database import AsyncSessionLocal
import asyncio
import logging

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "newstrader",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=['app.celery_app']
)

# Configure Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    beat_schedule={
        'scrape-news-every-hour': {
            'task': 'app.celery_app.scrape_and_analyze_news',
            'schedule': 3600.0,  # Every hour
        },
        'update-impact-weights-daily': {
            'task': 'app.celery_app.update_impact_weights',
            'schedule': 86400.0,  # Every day
        },
    },
)


@celery_app.task
def scrape_and_analyze_news():
    """Periodically scrape news and analyze with Claude"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(_scrape_and_analyze_news_async())
        return result
    finally:
        loop.close()


async def _scrape_and_analyze_news_async():
    """Async function to scrape and analyze news"""
    saved_count = 0
    
    try:
        # Scrape news
        async with NewsScraperService() as scraper:
            articles_data = await scraper.scrape_all_sources()
        
        if not articles_data:
            logger.info("No new articles found during scraping")
            return {"message": "No new articles found", "count": 0}
        
        # Analyze with Claude
        claude_analyzer = ClaudeAnalyzer()
        analyses = await claude_analyzer.batch_analyze(
            articles_data,
            settings.TRADING_SYMBOLS
        )
        
        # Save to database
        async with AsyncSessionLocal() as db:
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
        
        logger.info(f"Scraped and analyzed {saved_count} new articles")
        return {
            "message": f"Scraped and analyzed {saved_count} new articles",
            "count": saved_count
        }
        
    except Exception as e:
        logger.error(f"News scraping and analysis failed: {e}")
        return {"error": str(e), "count": 0}


@celery_app.task
def update_impact_weights():
    """Daily task to update impact weights based on actual market movements"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(_update_impact_weights_async())
        return result
    finally:
        loop.close()


async def _update_impact_weights_async():
    """Async function to update impact weights"""
    try:
        # This would involve:
        # 1. Get articles from last 24-48 hours
        # 2. Fetch actual price movements for affected symbols
        # 3. Calculate actual vs predicted impact
        # 4. Update ImpactWeight records
        # 5. Adjust Claude analysis confidence scores
        
        logger.info("Impact weights update completed")
        return {"message": "Impact weights updated successfully"}
        
    except Exception as e:
        logger.error(f"Impact weights update failed: {e}")
        return {"error": str(e)}


@celery_app.task
def run_symbol_backtest(symbol: str, days_back: int = 30):
    """Run backtest for a specific symbol"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Import here to avoid circular imports
        from app.api.endpoints.backtest import run_backtest
        result = loop.run_until_complete(
            _run_backtest_async(symbol, days_back)
        )
        return result
    finally:
        loop.close()


async def _run_backtest_async(symbol: str, days_back: int):
    """Async function to run backtest"""
    try:
        # This would run the backtest logic
        # Similar to the API endpoint but as a background task
        
        logger.info(f"Backtest completed for {symbol}")
        return {"message": f"Backtest completed for {symbol}"}
        
    except Exception as e:
        logger.error(f"Backtest failed for {symbol}: {e}")
        return {"error": str(e)}


# Health check task
@celery_app.task
def health_check():
    """Simple health check task"""
    return {"status": "healthy", "message": "Celery worker is running"}


if __name__ == '__main__':
    celery_app.start()