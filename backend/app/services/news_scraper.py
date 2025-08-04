import asyncio
import aiohttp
import feedparser
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from datetime import datetime, timezone
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class NewsScraperService:
    def __init__(self, use_chinese_sources=True):
        # Use Chinese sources for better local market coverage
        if use_chinese_sources:
            self.sources = settings.CHINESE_NEWS_SOURCES + settings.NEWS_SOURCES
        else:
            self.sources = settings.NEWS_SOURCES
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_all_sources(self) -> List[Dict[str, Any]]:
        """Scrape all configured news sources"""
        all_articles = []
        
        tasks = [self.scrape_rss_feed(source) for source in self.sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Failed to scrape {self.sources[i]}: {result}")
                continue
            all_articles.extend(result)
        
        # Remove duplicates based on URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles
    
    async def scrape_rss_feed(self, feed_url: str) -> List[Dict[str, Any]]:
        """Scrape a single RSS feed"""
        try:
            async with self.session.get(feed_url) as response:
                if response.status != 200:
                    logger.error(f"Failed to fetch {feed_url}: {response.status}")
                    return []
                
                content = await response.text()
                feed = feedparser.parse(content)
                
                articles = []
                for entry in feed.entries:
                    article = await self.process_rss_entry(entry, feed_url)
                    if article:
                        articles.append(article)
                
                return articles
                
        except Exception as e:
            logger.error(f"Error scraping RSS feed {feed_url}: {e}")
            return []
    
    async def process_rss_entry(self, entry, source_url: str) -> Dict[str, Any]:
        """Process a single RSS entry"""
        try:
            # Extract basic info
            title = getattr(entry, 'title', '')
            url = getattr(entry, 'link', '')
            summary = getattr(entry, 'summary', '')
            
            # Parse published date
            published_at = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_at = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published_at = datetime(*entry.updated_parsed[:6], tzinfo=timezone.utc)
            else:
                published_at = datetime.now(timezone.utc)
            
            # Get full article content
            full_content = await self.extract_article_content(url)
            content = full_content if full_content else summary
            
            # Filter for trading-relevant content
            if not self.is_trading_relevant(title + ' ' + content):
                return None
            
            return {
                'title': title,
                'content': content,
                'summary': summary,
                'url': url,
                'source': self.extract_source_name(source_url),
                'published_at': published_at
            }
            
        except Exception as e:
            logger.error(f"Error processing RSS entry: {e}")
            return None
    
    async def extract_article_content(self, url: str) -> str:
        """Extract full article content from URL"""
        try:
            async with self.session.get(url) as response:
                if response.status != 200:
                    return ""
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                
                # Try to find main content
                content_selectors = [
                    'article',
                    '.article-content',
                    '.story-body',
                    '.entry-content',
                    'main',
                    '#content'
                ]
                
                content = ""
                for selector in content_selectors:
                    elements = soup.select(selector)
                    if elements:
                        content = elements[0].get_text(strip=True)
                        break
                
                if not content:
                    # Fallback to body text
                    content = soup.get_text(strip=True)
                
                # Clean up content
                content = ' '.join(content.split())  # Remove extra whitespace
                return content[:5000]  # Limit content length
                
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return ""
    
    def is_trading_relevant(self, text: str) -> bool:
        """Check if content is relevant to trading/markets"""
        # English keywords
        english_keywords = [
            'stock', 'stocks', 'market', 'markets', 'trading', 'trader',
            'investment', 'investor', 'futures', 'commodities', 'forex',
            'earnings', 'revenue', 'profit', 'loss', 'price', 'rates',
            'federal reserve', 'fed', 'central bank', 'inflation',
            'gdp', 'economy', 'economic', 'recession', 'growth',
            'crude oil', 'gold', 'silver', 'bitcoin', 'crypto',
            'nasdaq', 'dow', 's&p', 'sp500', 'russell'
        ]
        
        # Chinese keywords from settings
        chinese_keywords = settings.CHINESE_MARKET_KEYWORDS
        
        # Additional common Chinese trading terms
        extra_chinese_keywords = [
            '股票', '股市', '证券', '基金', '期货', '外汇', '投资', '交易',
            '涨跌', '涨停', '跌停', '买入', '卖出', '持仓', '开盘', '收盘',
            '成交量', '市值', '估值', 'PE', 'PB', '分红', '配股', '增发',
            '财报', '业绩', '营收', '利润', '亏损', '股价', '汇率'
        ]
        
        all_keywords = english_keywords + chinese_keywords + extra_chinese_keywords
        text_lower = text.lower()
        
        return any(keyword.lower() in text_lower for keyword in all_keywords)
    
    def extract_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            return domain.replace('www.', '').replace('feeds.', '')
        except:
            return url


# Celery task for periodic news scraping
async def scrape_news_task():
    """Celery task to scrape news periodically"""
    async with NewsScraperService() as scraper:
        articles = await scraper.scrape_all_sources()
        logger.info(f"Scraped {len(articles)} articles")
        return articles