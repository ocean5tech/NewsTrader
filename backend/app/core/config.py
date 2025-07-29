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
    
    # News Sources - English
    NEWS_SOURCES: List[str] = [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://rss.cnn.com/rss/money_news_international.rss",
    ]
    
    # News Sources - Chinese Financial
    CHINESE_NEWS_SOURCES: List[str] = [
        "https://feed.sina.com.cn/api/roll/get?pageid=153&lid=1686&k=&num=50&page=1",  # 新浪财经
        "https://rss.36kr.com/feed",  # 36氪
        "https://wallstreetcn.com/feed",  # 华尔街见闻
        "https://www.jiemian.com/lists/426.html",  # 界面新闻财经
        "https://finance.sina.com.cn/roll/index.d.html?cid=56588",  # 新浪财经滚动
    ]
    
    # Trading symbols to monitor - Extended for Chinese markets
    TRADING_SYMBOLS: List[str] = [
        # US Markets
        "SPY", "QQQ", "GLD", "CL=F", "GC=F", "ES=F",
        # Chinese Markets  
        "000001.SS", "399001.SZ", "HSI", "BABA", "JD", "TCEHY",
        # Commodities
        "XAUUSD", "XAGUSD", "USOIL", "BRENT",
        # Currency
        "USDCNY", "EURUSD", "GBPUSD"
    ]
    
    # Chinese market keywords for impact analysis
    CHINESE_MARKET_KEYWORDS: List[str] = [
        # 市场相关
        "A股", "港股", "沪深", "上证", "深证", "创业板", "科创板", "北交所",
        # 政策相关  
        "央行", "货币政策", "利率", "准备金率", "MLF", "LPR", "QDII", "QFII",
        # 经济指标
        "GDP", "CPI", "PPI", "PMI", "通胀", "通缩", "就业", "消费",
        # 行业板块
        "房地产", "新能源", "芯片", "医药", "白酒", "银行", "保险", "券商",
        # 商品期货
        "原油", "黄金", "白银", "铜", "铁矿石", "螺纹钢", "大豆", "玉米",
        # 国际关系
        "中美", "贸易战", "关税", "制裁", "汇率", "美联储", "加息", "降息"
    ]
    
    class Config:
        env_file = ".env"


settings = Settings()