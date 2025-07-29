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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)