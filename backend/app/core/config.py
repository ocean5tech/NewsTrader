from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://username:password@localhost/newstrader"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Claude AI
    ANTHROPIC_API_KEY: str = ""
    
    # Security
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    ALLOWED_HOSTS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # News Sources
    NEWS_SOURCES: List[str] = [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://rss.cnn.com/rss/money_news_international.rss",
    ]
    
    # Trading symbols to monitor
    TRADING_SYMBOLS: List[str] = ["SPY", "QQQ", "GLD", "CL=F", "GC=F", "ES=F"]
    
    class Config:
        env_file = ".env"


settings = Settings()