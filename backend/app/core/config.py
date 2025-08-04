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
    
    # News Sources - Chinese Financial (Real RSS Feeds)
    CHINESE_NEWS_SOURCES: List[str] = [
        # 新浪财经 - Direct RSS feeds
        "http://rss.sina.com.cn/roll/finance/hot_roll.xml",  # 财经热点
        "http://rss.sina.com.cn/news/allnews/finance.xml",   # 财经综合
        "http://rss.sina.com.cn/roll/stock/hot_roll.xml",    # 股票热点
        "http://rss.sina.com.cn/finance/fund.xml",           # 基金新闻
        "http://rss.sina.com.cn/finance/usstock.xml",        # 美股新闻
        "http://rss.sina.com.cn/finance/hkstock.xml",        # 港股新闻
        "http://rss.sina.com.cn/finance/future.xml",         # 期货新闻
        
        # 网易财经
        "http://money.163.com/special/00251HOG/zqschzk.xml", # 证券财经
        "http://money.163.com/special/00251HO9/read_zqsb.xml", # 证券时报
        
        # 第一财经 (通过RSSHub)
        "https://rsshub.app/yicai/headline",                 # 第一财经头条
        "https://rsshub.app/yicai/latest",                   # 第一财经最新
        
        # 财新网 (通过RSSHub)
        "https://rsshub.app/caixin/latest",                  # 财新最新
        
        # 东方财富 (通过RSSHub)
        "https://rsshub.app/eastmoney/report/strategyreport", # 策略报告
        "https://rsshub.app/eastmoney/report/industry",       # 行业报告
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