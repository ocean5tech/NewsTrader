from fastapi import FastAPI, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import feedparser
import hashlib
import random
from datetime import datetime, timezone
from typing import List, Dict, Any
from dotenv import load_dotenv
from anthropic import Anthropic

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

@app.get("/api/v1/news/test")
async def test_articles():
    """测试端点，返回静态数据"""
    return [
        {
            "id": "test-1",
            "title": "Test News Article",
            "title_zh": "测试新闻文章",
            "summary": "This is a test news article.",
            "summary_zh": "这是一篇测试新闻文章。",
            "url": "http://example.com",
            "source": "Test Source",
            "published_at": "2025-07-30T10:00:00Z",
            "impact_score": 5.0,
            "sentiment_score": 0.1,
            "affected_symbols": ["SPY", "QQQ"],
            "confidence_score": 0.75,
            "news_type": "factual"
        }
    ]

def analyze_news_with_claude(title: str, summary: str) -> Dict[str, Any]:
    """快速本地新闻分析算法"""
    # 为了快速响应，先使用本地算法，后续可异步调用Claude AI
    import re
    
    # 影响评分算法
    high_impact_keywords = ['央行', '美联储', '加息', '降息', 'GDP', '通胀', '失业率', '贸易战', '制裁']
    medium_impact_keywords = ['财报', '盈利', '收益', '股价', '市值', '并购', 'IPO']
    
    title_lower = title.lower()
    summary_lower = summary.lower() if summary else ""
    text = f"{title_lower} {summary_lower}"
    
    impact_score = 5.0  # 基础评分
    
    # 检查高影响关键词
    for keyword in high_impact_keywords:
        if keyword in text:
            impact_score += 1.5
    
    # 检查中等影响关键词  
    for keyword in medium_impact_keywords:
        if keyword in text:
            impact_score += 0.8
            
    # 限制评分范围
    impact_score = min(10.0, max(1.0, impact_score))
    
    # 情感分析
    positive_words = ['上涨', '增长', '利好', '看涨', 'surge', 'gain', 'profit', 'growth']
    negative_words = ['下跌', '下滑', '利空', '看跌', 'drop', 'fall', 'loss', 'decline']
    
    sentiment_score = 0.0
    for word in positive_words:
        if word in text:
            sentiment_score += 0.2
    for word in negative_words:
        if word in text:
            sentiment_score -= 0.2
            
    sentiment_score = min(1.0, max(-1.0, sentiment_score))
    
    # 受影响品种 - 增强版本
    affected_symbols = []
    
    # 具体公司匹配
    company_symbols = {
        'apple': ['AAPL'], 'tesla': ['TSLA'], 'microsoft': ['MSFT'], 
        'google': ['GOOGL'], 'amazon': ['AMZN'], 'meta': ['META'],
        'nvidia': ['NVDA'], 'netflix': ['NFLX'], 'uber': ['UBER'],
        'goldman sachs': ['GS'], 'jp morgan': ['JPM'], 'wells fargo': ['WFC'],
        'bank of america': ['BAC'], 'citigroup': ['C'],
        'exxon': ['XOM'], 'chevron': ['CVX'], 'conocophillips': ['COP']
    }
    
    for company, symbols in company_symbols.items():
        if company in text:
            affected_symbols.extend(symbols)
            break
    
    # 行业和主题匹配
    if not affected_symbols:
        if any(word in text for word in ['科技', 'tech', '芯片', 'chip', 'ai', 'artificial intelligence', 'semiconductor']):
            affected_symbols.extend(['QQQ', 'XLK', 'NVDA'])
        elif any(word in text for word in ['银行', 'bank', '金融', 'financial', 'lending', '贷款']):
            affected_symbols.extend(['XLF', 'JPM', 'BAC']) 
        elif any(word in text for word in ['石油', 'oil', '能源', 'energy', 'crude', '原油']):
            affected_symbols.extend(['CL=F', 'XLE', 'XOM'])
        elif any(word in text for word in ['黄金', 'gold', '贵金属', 'precious metals']):
            affected_symbols.extend(['GC=F', 'GLD', 'XAUUSD'])
        elif any(word in text for word in ['房地产', 'real estate', 'housing', '住房']):
            affected_symbols.extend(['XLF', 'VNQ'])
        elif any(word in text for word in ['healthcare', '医疗', '制药', 'pharma', 'biotech']):
            affected_symbols.extend(['XLV', 'JNJ', 'PFE'])
        elif any(word in text for word in ['retail', '零售', 'consumer', '消费']):
            affected_symbols.extend(['XLY', 'AMZN', 'WMT'])
        elif any(word in text for word in ['federal reserve', 'fed', '美联储', 'interest rate', '利率']):
            affected_symbols.extend(['SPY', 'TLT', 'USDCNY'])
        elif any(word in text for word in ['china', '中国', 'chinese', '人民币']):
            affected_symbols.extend(['USDCNY', 'FXI', 'ASHR'])
        elif any(word in text for word in ['europe', '欧洲', 'euro', '欧元']):
            affected_symbols.extend(['EURUSD', 'EFA', 'VGK'])
        else:
            affected_symbols = ['SPY', 'QQQ']  # 默认大盘指数
        
    # 计算置信度 - 优化版本
    confidence_score = 0.6  # 提高基础置信度
    
    # 根据关键词匹配程度调整置信度
    keyword_matches = 0
    for keyword in high_impact_keywords + medium_impact_keywords:
        if keyword in text:
            keyword_matches += 1
    
    # 关键词匹配调整（更敏感）
    confidence_score += min(0.25, keyword_matches * 0.08)
    
    # 根据数据具体性调整置信度
    import re
    if re.search(r'\d+(?:\.\d+)?%', text):  # 有具体百分比
        confidence_score += 0.12
    if re.search(r'\$\d+(?:\.\d+)?\s*(?:billion|million|trillion)', text):  # 有具体金额
        confidence_score += 0.12
    if re.search(r'\d+\.\d+', text):  # 有精确数字
        confidence_score += 0.05
    
    # 公司名称识别增加置信度
    company_names = ['apple', 'tesla', 'microsoft', 'google', 'amazon', 'meta', 'nvidia']
    for company in company_names:
        if company in text:
            confidence_score += 0.08
            break
    
    # 时间具体性（季度、年份等）
    if re.search(r'q[1-4]|quarter|2024|2025', text):
        confidence_score += 0.06
    
    # 受影响品种数量调整
    if len(affected_symbols) > 2:
        confidence_score += 0.08
    elif len(affected_symbols) == 2:
        confidence_score += 0.04
    
    # 根据情感强度调整
    if abs(sentiment_score) > 0.4:
        confidence_score += 0.12
    elif abs(sentiment_score) > 0.2:
        confidence_score += 0.06
    
    # 标题长度调整（更长的标题通常包含更多信息）
    if len(title) > 60:
        confidence_score += 0.05
    
    confidence_score = min(0.95, max(0.45, confidence_score))  # 限制在0.45-0.95之间
    
    return {
        "impact_score": round(impact_score, 1),
        "sentiment_score": round(sentiment_score, 2),
        "affected_symbols": affected_symbols[:4],  # 最多4个品种
        "confidence_score": round(confidence_score, 2)
    }

def is_factual_news(title: str, summary: str = "") -> bool:
    """判断是否为事实性新闻（非观点评论）"""
    text = f"{title.lower()} {summary.lower()}"
    
    # 观点性新闻的强指标（直接过滤）
    strong_opinion_indicators = [
        # 人物观点（明确的观点表达）
        ' says ', ' thinks ', ' believes ', ' warns ', ' predicts ', 
        ' expects ', ' suggests ', ' argues ', ' claims ', ' tells ',
        # 分析师/专家观点
        'analysts say', 'experts say', 'strategists say', 'economists say',
        'according to', 'interview', 'exclusive:', 'opinion:',
        # 视频/播客内容
        'video)', 'podcast', 'watch:', 'listen:', '(video',
        # CEO/高管观点
        'ceo says', 'cfo says', 'chairman says', 'ermotti says'
    ]
    
    # 事实性新闻的强指标
    strong_factual_indicators = [
        # 数据发布
        'reports', 'announces', 'releases data', 'posts', 'shows',
        # 价格/数据变动
        'rises', 'falls', 'up ', 'down ', 'gains', 'loses', 'drops', 'jumps',
        'hits', 'reaches', 'climbs', 'slides', 'surges', 'plunges',
        # 政策/决定
        'cuts rates', 'raises rates', 'approves', 'rejects', 'launches',
        'halts', 'suspends', 'resumes', 'files', 'settles',
        # 财报/业绩
        'earnings', 'profit', 'revenue', 'quarterly results', 'beats estimates',
        'misses estimates', 'dividend', 'split',
        # 交易/并购
        'acquires', 'merges', 'sells stake', 'buys', 'invests', 'ipo',
        # 监管/法律
        'regulator', 'court', 'lawsuit', 'fine', 'penalty', 'license'
    ]
    
    # 中性词汇（可能是事实也可能是观点）
    neutral_indicators = [
        'shares', 'stocks', 'market', 'trading', 'company', 'sector'
    ]
    
    # 检查强观点指标
    for indicator in strong_opinion_indicators:
        if indicator in text:
            return False
    
    # 检查强事实指标
    for indicator in strong_factual_indicators:
        if indicator in text:
            return True
    
    # 额外过滤规则
    # 过滤包含人名的观点性新闻（通常是某人说了什么）
    import re
    # 检查是否有 "人名 + 动词" 的模式
    name_pattern = r'\b[A-Z][a-z]+ [A-Z][a-z]+\b (says|thinks|believes|warns|expects|calls)'
    if re.search(name_pattern, title):
        return False
    
    # 过滤视频、访谈类内容
    if any(word in text for word in ['video)', '(video', 'interview with', 'exclusive with']):
        return False
    
    # 过滤预测和展望类
    if any(word in text for word in ['forecast', 'prediction', 'what lies ahead', 'road ahead']):
        return False
    
    # 如果没有明确的分类，倾向于保留（默认为事实性）
    return True

def extract_key_entities(title: str, summary: str = "") -> set:
    """提取新闻中的关键实体（公司名、数据、事件）"""
    import re
    
    text = f"{title} {summary}".lower()
    entities = set()
    
    # 提取公司名（常见模式）
    companies = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b(?:\s+(?:Corp|Inc|Ltd|Group|Bank|Holdings?))?', title + " " + summary)
    entities.update([c.lower() for c in companies if len(c) > 2])
    
    # 提取财务关键词
    financial_terms = re.findall(r'\b(profit|earnings|revenue|loss|dividend|ipo|merger|acquisition|bankruptcy)\b', text)
    entities.update(financial_terms)
    
    # 提取百分比和金额
    percentages = re.findall(r'(\d+(?:\.\d+)?%)', text)
    amounts = re.findall(r'(\$\d+(?:\.\d+)?\s*(?:billion|million|trillion))', text)
    entities.update(percentages + amounts)
    
    # 提取季度信息
    quarters = re.findall(r'(q[1-4]|quarter|quarterly)', text)
    entities.update(quarters)
    
    return entities

def calculate_news_similarity(news1: dict, news2: dict) -> float:
    """计算两条新闻的相似度（基于关键实体）"""
    entities1 = extract_key_entities(news1['title'], news1.get('summary', ''))
    entities2 = extract_key_entities(news2['title'], news2.get('summary', ''))
    
    if not entities1 or not entities2:
        return 0.0
    
    # 计算交集比例
    intersection = entities1.intersection(entities2)
    union = entities1.union(entities2)
    
    if not union:
        return 0.0
    
    similarity = len(intersection) / len(union)
    
    # 如果有共同的公司名，增加相似度权重
    company_overlap = len([e for e in intersection if len(e) > 3])
    if company_overlap > 0:
        similarity += 0.2 * company_overlap
    
    return min(1.0, similarity)

def is_primary_factual_news(title: str, summary: str = "") -> bool:
    """判断是否为主要事实性新闻（非衍生评论）"""
    text = f"{title.lower()} {summary.lower()}"
    
    # 主要事实新闻的强指标
    primary_indicators = [
        # 公司直接行动
        'announces', 'reports', 'posts', 'releases', 'launches', 'cuts', 'raises',
        'beats estimates', 'misses estimates', 'files for', 'approves', 'rejects',
        # 市场数据
        'rises', 'falls', 'gains', 'loses', 'hits record', 'reaches', 'drops to',
        # 财报季
        'quarterly earnings', 'q1 results', 'q2 results', 'q3 results', 'q4 results',
        # 重大事件
        'merger', 'acquisition', 'ipo', 'dividend', 'stock split', 'bankruptcy'
    ]
    
    # 衍生评论的指标
    derivative_indicators = [
        'analysis', 'outlook', 'what it means', 'impact of', 'following',
        'after', 'amid', 'on news', 'reaction to', 'responds to',
        'analysts react', 'experts say', 'what', 'mean for', 'numbers mean'
    ]
    
    primary_score = sum(1 for indicator in primary_indicators if indicator in text)
    derivative_score = sum(1 for indicator in derivative_indicators if indicator in text)
    
    # 如果主要指标多于衍生指标，认为是主要新闻
    return primary_score > derivative_score

def deduplicate_news_by_events(articles: list) -> list:
    """基于事件去重：保留事实性新闻，过滤相关评论"""
    if not articles:
        return articles
    
    # 第一步：分类新闻
    factual_news = []
    opinion_news = []
    
    for article in articles:
        if is_primary_factual_news(article['title'], article.get('summary', '')):
            factual_news.append(article)
        else:
            opinion_news.append(article)
    
    # 第二步：为每条事实新闻找到相关的评论新闻
    filtered_articles = []
    covered_topics = set()
    
    # 优先处理事实新闻
    for fact_article in factual_news:
        fact_entities = extract_key_entities(fact_article['title'], fact_article.get('summary', ''))
        
        # 检查是否与已有事实新闻重复
        is_duplicate = False
        for covered_entity_set in covered_topics:
            if len(fact_entities.intersection(covered_entity_set)) >= 2:  # 至少2个共同实体
                is_duplicate = True
                break
        
        if not is_duplicate:
            filtered_articles.append(fact_article)
            covered_topics.add(frozenset(fact_entities))
            print(f"📊 保留主要事实新闻: {fact_article['title']}")
        else:
            print(f"🔄 过滤重复事实新闻: {fact_article['title']}")
    
    # 第三步：检查评论新闻是否与已保留的事实新闻重复
    for opinion_article in opinion_news:
        opinion_entities = extract_key_entities(opinion_article['title'], opinion_article.get('summary', ''))
        
        # 检查是否与任何已保留的事实新闻相关
        is_related_to_fact = False
        for covered_entity_set in covered_topics:
            if len(opinion_entities.intersection(covered_entity_set)) >= 1:  # 至少1个共同实体
                is_related_to_fact = True
                break
        
        if not is_related_to_fact and is_factual_news(opinion_article['title'], opinion_article.get('summary', '')):
            filtered_articles.append(opinion_article)
            print(f"📝 保留独立评论新闻: {opinion_article['title']}")
        else:
            print(f"🗣️  过滤相关评论新闻: {opinion_article['title']}")
    
    return filtered_articles

def translate_to_chinese(text: str) -> str:
    """使用Claude AI进行高质量中文翻译"""
    try:
        # 如果已经是中文，直接返回
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        if chinese_chars > len(text) * 0.3:  # 如果中文字符超过30%，认为是中文
            return text
            
        # 使用Claude进行翻译
        translation_prompt = f"""请将以下财经新闻文本翻译成自然流畅的中文。要求：
1. 保持财经术语的准确性
2. 语句通顺自然
3. 保留重要的公司名称、数字和日期
4. 翻译要符合中文财经新闻的表达习惯

原文：{text}

请只返回翻译结果，不要添加任何解释："""

        import anthropic
        import os
        
        # 获取API密钥
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            # 如果没有API密钥，使用改进的词典翻译
            return translate_with_enhanced_dict(text)
            
        client = anthropic.Anthropic(api_key=api_key)
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",  # 使用较快的模型
            max_tokens=1000,
            temperature=0.1,
            messages=[{
                "role": "user",
                "content": translation_prompt
            }]
        )
        
        # 更新API调用统计
        _stats["claude_api_calls"] += 1
        
        translation = message.content[0].text.strip()
        return translation if translation else text
        
    except Exception as e:
        print(f"Claude翻译失败: {e}")
        # 降级到改进的词典翻译
        return translate_with_enhanced_dict(text)

def translate_with_enhanced_dict(text: str) -> str:
    """改进的词典翻译方法"""
    import re
    
    # 财经术语字典
    finance_dict = {
        # 公司和机构
        'verizon communications inc': '威瑞森通信公司', 'verizon': '威瑞森',
        'apple': '苹果', 'microsoft': '微软', 'google': '谷歌', 'tesla': '特斯拉',
        'amazon': '亚马逊', 'facebook': 'Facebook', 'meta': 'Meta',
        'goldman sachs': '高盛', 'jp morgan': '摩根大通', 'morgan stanley': '摩根士丹利',
        'federal reserve': '美联储', 'fed': '美联储', 'ecb': '欧央行',
        'bloomberg': '彭博', 'reuters': '路透',
        
        # 财经术语
        'reverse yankee': '反向扬基债券', 'reverse-yankee': '反向扬基债券',
        'two-part bond': '两部分债券', 'two-part sale': '两部分发行',
        'debt market': '债务市场', "europe's debt market": '欧洲债务市场',
        'earnings': '财报', 'profit': '利润', 'revenue': '营收', 'loss': '亏损',
        'quarter': '季度', 'quarterly': '季度', 'second quarter': '第二季度',
        'shares': '股份', 'stock': '股票', 'bond': '债券', 'debt': '债务',
        'market': '市场', 'trading': '交易', 'supply': '供应',
        'growth': '增长', 'economy': '经济', 'economic': '经济的',
        'interest rate': '利率', 'inflation': '通胀', 'gdp': 'GDP',
        'unemployment': '失业率', 'trade': '贸易',
        'euro area': '欧元区', 'euro-area': '欧元区',
        
        # 动作和状态
        'is adding to': '正在增加', 'adding to': '增加了',
        'marks its first foray': '标志着首次进军',
        'first foray into': '首次进军',
        'unexpectedly eked out': '意外实现了',
        'benefiting from': '受益于',
        'better-than-predicted': '超出预期的',
        'performances': '表现',
        'held most of': '保持了大部分',
        'biggest gain': '最大涨幅',
        'reiterated': '重申',
        'may impose': '可能实施',
        'additional economic penalties': '额外经济制裁',
        'unless': '除非',
        'truce is reached': '达成停火协议',
        'struggled': '表现艰难',
        'heavy load': '大量',
        'major company': '主要公司',
        
        # 时间和数量
        'in nearly a year and a half': '在近一年半的时间里',
        'year and a half': '一年半',
        'in six weeks': '六周内',
        'six weeks': '六周',
        'record year': '创纪录的一年',
        'year': '年', 'month': '月', 'week': '周', 'day': '天',
        'nearly': '近', 'half': '半',
        'billion': '十亿', 'million': '百万', 'trillion': '万亿',
        
        # 地点
        "europe's": '欧洲的', 'europe': '欧洲',
        'france': '法国', 'spain': '西班牙',
        'russia': '俄罗斯', 'ukraine': '乌克兰',
        'china': '中国', 'us': '美国', 'united states': '美国',
        
        # 常用词
        'so-called': '所谓的',
        'with': '通过', 'that': '这', 'its': '其',
        'after': '在...之后', 'before': '在...之前',
        'amid': '在...中', 'despite': '尽管',
        'from': '从', 'into': '进入',
        'president': '总统', 'donald trump': '唐纳德·特朗普'
    }
    
    result = text
    
    # 按长度排序，优先匹配长短语
    sorted_dict = sorted(finance_dict.items(), key=lambda x: len(x[0]), reverse=True)
    
    for en, zh in sorted_dict:
        # 使用词边界匹配
        pattern = r'\b' + re.escape(en) + r'\b'
        result = re.sub(pattern, zh, result, flags=re.IGNORECASE)
    
    return result

def get_chinese_translation(title: str, summary: str = "") -> dict:
    """获取新闻的中文翻译"""
    return {
        "title_zh": translate_to_chinese(title),
        "summary_zh": translate_to_chinese(summary) if summary else ""
    }

def get_sample_articles(limit: int = 20):
    """返回示例新闻数据作为后备"""
    sample_articles = [
        {
            "id": "sample-1",
            "title": "Federal Reserve Maintains Interest Rates at Current Level",
            "title_zh": "美联储维持当前利率水平不变",
            "summary": "The Federal Reserve decided to keep interest rates unchanged at their latest meeting, citing economic stability concerns.",
            "summary_zh": "美联储在最新会议中决定保持利率不变，理由是经济稳定性考虑。",
            "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary.htm",
            "source": "Federal Reserve",
            "published_at": "2025-07-31T10:00:00Z",
            "impact_score": 7.5,
            "sentiment_score": 0.0,
            "affected_symbols": ["SPY", "TLT", "DXY"],
            "confidence_score": 0.85,
            "news_type": "factual"
        },
        {
            "id": "sample-2",
            "title": "Tech Stocks Rally on Strong Quarterly Earnings",
            "title_zh": "科技股因强劲季度财报而上涨",
            "summary": "Major technology companies posted better-than-expected quarterly earnings, driving sector gains.",
            "summary_zh": "主要科技公司公布了超出预期的季度财报，推动板块上涨。",
            "url": "https://www.nasdaq.com/market-activity/stocks",
            "source": "NASDAQ",
            "published_at": "2025-07-31T09:30:00Z",
            "impact_score": 6.2,
            "sentiment_score": 0.3,
            "affected_symbols": ["QQQ", "AAPL", "MSFT"],
            "confidence_score": 0.78,
            "news_type": "factual"
        }
    ]
    return sample_articles[:limit]

# 全局变量
_news_cache = {"data": None, "timestamp": 0}
CACHE_DURATION = 300  # 5分钟缓存

# 统计变量
_stats = {
    "news_sources": {},  # 各信源获取的新闻数量
    "claude_api_calls": 0,  # Claude API调用次数
    "last_update": None,  # 最后更新时间
    "total_articles": 0,  # 总新闻数
}

# 完整的交易品种数据库
TRADING_SYMBOLS_DATABASE = {
    # 美国股票ETF
    "SPY": {"name": "SPDR S&P 500 ETF", "category": "美国ETF", "keywords": ["标普500", "s&p", "spy"]},
    "QQQ": {"name": "Invesco QQQ ETF", "category": "美国ETF", "keywords": ["纳斯达克", "nasdaq", "qqq", "科技"]},
    "IWM": {"name": "iShares Russell 2000 ETF", "category": "美国ETF", "keywords": ["罗素2000", "小盘股"]},
    "GLD": {"name": "SPDR Gold Shares", "category": "贵金属ETF", "keywords": ["黄金", "gold", "贵金属"]},
    "SLV": {"name": "iShares Silver Trust", "category": "贵金属ETF", "keywords": ["白银", "silver"]},
    
    # 美国个股
    "AAPL": {"name": "Apple Inc.", "category": "美国科技股", "keywords": ["苹果", "apple", "iphone"]},
    "MSFT": {"name": "Microsoft Corporation", "category": "美国科技股", "keywords": ["微软", "microsoft"]},
    "GOOGL": {"name": "Alphabet Inc.", "category": "美国科技股", "keywords": ["谷歌", "google", "alphabet"]},
    "AMZN": {"name": "Amazon.com Inc.", "category": "美国科技股", "keywords": ["亚马逊", "amazon"]},
    "TSLA": {"name": "Tesla Inc.", "category": "美国科技股", "keywords": ["特斯拉", "tesla", "电动车"]},
    "NVDA": {"name": "NVIDIA Corporation", "category": "美国科技股", "keywords": ["英伟达", "nvidia", "芯片", "ai"]},
    "META": {"name": "Meta Platforms Inc.", "category": "美国科技股", "keywords": ["脸书", "facebook", "meta"]},
    "NFLX": {"name": "Netflix Inc.", "category": "美国科技股", "keywords": ["奈飞", "netflix"]},
    
    # 中国股票
    "BABA": {"name": "Alibaba Group Holding", "category": "中概股", "keywords": ["阿里巴巴", "alibaba", "淘宝"]},
    "JD": {"name": "JD.com Inc.", "category": "中概股", "keywords": ["京东", "jd"]},
    "PDD": {"name": "PDD Holdings Inc.", "category": "中概股", "keywords": ["拼多多", "pdd"]},
    "TCEHY": {"name": "Tencent Holdings", "category": "中概股", "keywords": ["腾讯", "tencent", "微信"]},
    "NIO": {"name": "NIO Inc.", "category": "中概股", "keywords": ["蔚来", "nio", "电动车"]},
    "LI": {"name": "Li Auto Inc.", "category": "中概股", "keywords": ["理想", "li auto", "电动车"]},
    "XPEV": {"name": "XPeng Inc.", "category": "中概股", "keywords": ["小鹏", "xpeng", "电动车"]},
    
    # A股主要指数和股票
    "000001.SS": {"name": "上证指数", "category": "A股指数", "keywords": ["上证", "上海", "大盘"]},
    "399001.SZ": {"name": "深证成指", "category": "A股指数", "keywords": ["深证", "深圳", "成指"]},
    "399006.SZ": {"name": "创业板指", "category": "A股指数", "keywords": ["创业板", "创指"]},
    "000300.SS": {"name": "沪深300", "category": "A股指数", "keywords": ["沪深300", "hs300"]},
    
    # A股个股 - 与数据库数据对应
    "000001": {"name": "平安银行", "category": "A股银行", "keywords": ["平安银行", "银行", "PAYH", "payh"]},
    "000002": {"name": "万科A", "category": "A股地产", "keywords": ["万科", "地产", "WKA", "wka"]},
    "600000": {"name": "浦发银行", "category": "A股银行", "keywords": ["浦发银行", "银行", "PFYH", "pfyh"]},
    "600519": {"name": "贵州茅台", "category": "A股白酒", "keywords": ["茅台", "白酒", "GZMT", "gzmt"]},
    "000858": {"name": "五粮液", "category": "A股白酒", "keywords": ["五粮液", "白酒", "WLY", "wly"]},
    "601318": {"name": "中国平安", "category": "A股保险", "keywords": ["中国平安", "保险", "ZGPA", "zgpa"]},
    "600036": {"name": "招商银行", "category": "A股银行", "keywords": ["招商银行", "银行", "ZSYH", "zsyh"]},
    "300001": {"name": "特锐德", "category": "A股创业板", "keywords": ["特锐德", "创业板", "TRD", "trd"]},
    "688001": {"name": "华兴源创", "category": "A股科创板", "keywords": ["华兴源创", "科创板", "HXYC", "hxyc"]},
    "601857": {"name": "中国石油", "category": "A股能源", "keywords": ["中国石油", "石油", "ZGSY", "zgsy"]},
    
    # 带交易所后缀的格式（保持兼容性）
    "600519.SS": {"name": "贵州茅台", "category": "A股个股", "keywords": ["茅台", "白酒"]},
    "000858.SZ": {"name": "五粮液", "category": "A股个股", "keywords": ["五粮液", "白酒"]},
    "002594.SZ": {"name": "比亚迪", "category": "A股个股", "keywords": ["比亚迪", "byd", "电动车", "新能源"]},
    
    # 港股
    "HSI": {"name": "恒生指数", "category": "港股指数", "keywords": ["恒生", "港股", "香港"]},
    "0700.HK": {"name": "腾讯控股", "category": "港股个股", "keywords": ["腾讯", "港股腾讯"]},
    "9988.HK": {"name": "阿里巴巴-SW", "category": "港股个股", "keywords": ["阿里", "港股阿里"]},
    
    # 期货
    "GC=F": {"name": "COMEX黄金期货", "category": "贵金属期货", "keywords": ["美国黄金", "comex黄金", "黄金期货"]},
    "SI=F": {"name": "COMEX白银期货", "category": "贵金属期货", "keywords": ["美国白银", "comex白银", "白银期货"]},
    "CL=F": {"name": "WTI原油期货", "category": "能源期货", "keywords": ["原油", "wti", "石油", "油价"]},
    "BZ=F": {"name": "布伦特原油期货", "category": "能源期货", "keywords": ["布伦特", "brent", "原油"]},
    "NG=F": {"name": "天然气期货", "category": "能源期货", "keywords": ["天然气", "natural gas"]},
    "ES=F": {"name": "E-mini S&P 500期货", "category": "股指期货", "keywords": ["标普期货", "es"]},
    "NQ=F": {"name": "E-mini纳斯达克期货", "category": "股指期货", "keywords": ["纳指期货", "nq"]},
    
    # 外汇
    "USDCNY": {"name": "美元/人民币", "category": "外汇", "keywords": ["美元人民币", "汇率", "离岸人民币"]},
    "EURUSD": {"name": "欧元/美元", "category": "外汇", "keywords": ["欧美", "欧元美元"]},
    "GBPUSD": {"name": "英镑/美元", "category": "外汇", "keywords": ["镑美", "英镑美元"]},
    "USDJPY": {"name": "美元/日元", "category": "外汇", "keywords": ["美日", "美元日元"]},
    "AUDUSD": {"name": "澳元/美元", "category": "外汇", "keywords": ["澳美", "澳元美元"]},
    
    # 加密货币
    "BTC-USD": {"name": "比特币", "category": "加密货币", "keywords": ["比特币", "bitcoin", "btc"]},
    "ETH-USD": {"name": "以太坊", "category": "加密货币", "keywords": ["以太坊", "ethereum", "eth"]},
    "BNB-USD": {"name": "币安币", "category": "加密货币", "keywords": ["币安", "bnb"]},
    
    # 上海期货
    "AU0": {"name": "上海黄金", "category": "国内期货", "keywords": ["上海黄金", "沪金", "au"]},
    "AG0": {"name": "上海白银", "category": "国内期货", "keywords": ["上海白银", "沪银", "ag"]},
    "CU0": {"name": "上海铜", "category": "国内期货", "keywords": ["沪铜", "铜", "cu"]},
    "RB0": {"name": "螺纹钢", "category": "国内期货", "keywords": ["螺纹钢", "钢铁", "rb"]},
    "SC0": {"name": "上海原油", "category": "国内期货", "keywords": ["上海原油", "国内原油", "sc"]},
}

# A股股票数据库 (动态更新)
_a_stock_database = {}

# 关注名单存储 (生产环境应使用数据库)
_watchlist = {
    "symbols": ["SPY"],  # 预添加SPY到关注名单
    "created_at": datetime.now(timezone.utc).isoformat(),
    "updated_at": datetime.now(timezone.utc).isoformat()
}

# WebSocket连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket连接建立，当前连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"❌ WebSocket连接断开，当前连接数: {len(self.active_connections)}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except:
            self.disconnect(websocket)

    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except:
                disconnected.append(connection)
        
        # 清理断开的连接
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

# 报警系统
async def check_and_send_alerts(news_item):
    """检查新闻是否触发报警并发送通知"""
    if not _watchlist["symbols"]:
        return
    
    affected_symbols = news_item.get("affected_symbols", [])
    watched_symbols = [s for s in affected_symbols if s in _watchlist["symbols"]]
    
    if not watched_symbols:
        return
    
    # 检查是否是高影响新闻 (影响分数 >= 6.0)
    impact_score = news_item.get("impact_score", 0)
    if impact_score >= 6.0:
        alert_data = {
            "type": "news_alert",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "news": {
                "id": news_item.get("id"),
                "title": news_item.get("title_zh") or news_item.get("title"),
                "summary": news_item.get("summary_zh") or news_item.get("summary"),
                "impact_score": impact_score,
                "sentiment_score": news_item.get("sentiment_score", 0),
                "watched_symbols": watched_symbols,
                "source": news_item.get("source"),
                "url": news_item.get("url")
            }
        }
        
        # 广播报警
        import json
        await manager.broadcast(json.dumps(alert_data))
        print(f"🚨 发送新闻报警: {news_item.get('title', '')[:50]}...")
        print(f"   影响品种: {', '.join(watched_symbols)}")
        print(f"   影响分数: {impact_score}")

def update_cache_background():
    """后台更新缓存"""
    import asyncio
    import time
    
    async def update():
        try:
            print("🔄 后台更新RSS数据...")
            data = await get_articles_with_rss(100)
            _news_cache["data"] = data
            _news_cache["timestamp"] = time.time()
            
            # 更新统计信息
            _stats["total_articles"] = len(data)
            _stats["last_update"] = datetime.now(timezone.utc).isoformat()
            
            # 检查新闻报警
            for article in data:
                await check_and_send_alerts(article)
            
            print("✅ 后台缓存更新完成")
        except Exception as e:
            print(f"❌ 后台RSS更新失败: {e}")
    
    # 在新的事件循环中运行
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update())
    loop.close()

@app.get("/api/v1/news/articles")
async def get_articles(limit: int = Query(20, ge=1, le=100)):
    """获取实时新闻文章 - 快速响应带后台更新"""
    import time
    current_time = time.time()
    
    # 检查缓存是否有效
    if (_news_cache["data"] is not None and 
        current_time - _news_cache["timestamp"] < CACHE_DURATION):
        print("📋 返回缓存的新闻数据")
        return _news_cache["data"][:limit]
    
    # 如果没有缓存，先返回示例数据，然后启动后台更新
    if _news_cache["data"] is None:
        print("⚡ 首次请求，返回示例数据并启动后台更新")
        # 启动后台更新
        from threading import Thread
        thread = Thread(target=update_cache_background)
        thread.daemon = True
        thread.start()
        
        return get_sample_articles(limit)
    
    # 缓存过期，启动后台更新但仍返回旧缓存
    print("🔄 缓存过期，返回旧数据并后台更新")
    from threading import Thread
    thread = Thread(target=update_cache_background)
    thread.daemon = True
    thread.start()
    
    return _news_cache["data"][:limit]

@app.get("/api/v1/news/articles_with_rss")  
async def get_articles_with_rss(limit: int = Query(20, ge=1, le=100)):
    """获取实时新闻文章 - RSS版本（可能超时）"""
    # 国际和中文财经新闻源
    news_sources = [
        ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg"),
        ("https://rss.36kr.com/feed", "36氪"),
        ("https://www.sina.com.cn/mid/feed.xml", "新浪财经"),
        ("https://www.jiemian.com/lists/426.xml", "界面新闻"),
        ("https://feeds.feedburner.com/zhitongcaijing", "智通财经"),
    ]
    
    all_articles = []
    
    for source_url, source_name in news_sources:
        try:
            print(f"正在抓取 {source_name} 新闻...")
            # 设置超时和代理，避免长时间等待
            import socket
            socket.setdefaulttimeout(10)  # 10秒超时
            feed = feedparser.parse(source_url)
            
            if not feed.entries:
                print(f"⚠️ {source_name} 未返回新闻")
                continue
                
            print(f"✅ {source_name} 成功获取 {len(feed.entries)} 条新闻")
            
            # 更新统计信息
            if source_name not in _stats["news_sources"]:
                _stats["news_sources"][source_name] = {"count": 0, "last_fetch": None}
            _stats["news_sources"][source_name]["count"] = len(feed.entries)
            _stats["news_sources"][source_name]["last_fetch"] = datetime.now(timezone.utc).isoformat()
            
            # 处理新闻，增加事实性筛选
            processed_count = 0
            for entry in feed.entries:
                # 如果已经获取足够的事实性新闻就停止
                if len(all_articles) >= limit:
                    break
                    
                # 限制总处理数量以控制响应时间
                if processed_count >= limit * 3:  # 最多处理3倍数量
                    break
                    
                processed_count += 1
                
                try:
                    # 事实性新闻筛选
                    summary = entry.summary if hasattr(entry, 'summary') else ""
                    if not is_factual_news(entry.title, summary):
                        print(f"🗣️  过滤观点性新闻: {entry.title}")
                        continue
                        
                    print(f"📊 保留事实性新闻: {entry.title}")
                    
                    # 生成唯一ID
                    article_id = hashlib.md5(f"{entry.title}{entry.link}".encode()).hexdigest()[:12]
                    
                    # 获取发布时间
                    published_at = entry.published if hasattr(entry, 'published') else datetime.now(timezone.utc).isoformat()
                    
                    # 快速本地分析（毫秒级）
                    analysis = analyze_news_with_claude(entry.title, summary)
                    
                    # 添加中文翻译
                    translation = get_chinese_translation(entry.title, summary)
                    
                    article = {
                        "id": article_id,
                        "title": entry.title,
                        "title_zh": translation["title_zh"],
                        "summary": summary if summary else entry.title[:200] + "...",
                        "summary_zh": translation["summary_zh"] if summary else translation["title_zh"][:200] + "...",
                        "url": entry.link,
                        "source": source_name,
                        "published_at": published_at,
                        "impact_score": analysis["impact_score"],
                        "sentiment_score": analysis["sentiment_score"],
                        "affected_symbols": analysis["affected_symbols"],
                        "confidence_score": analysis["confidence_score"],
                        "news_type": "factual"  # 标记为事实性新闻
                    }
                    
                    all_articles.append(article)
                    
                except Exception as e:
                    print(f"处理单条新闻失败: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ 抓取 {source_name} 失败: {e}")
            continue
    
    # 如果RSS抓取失败，返回一些示例数据确保前端正常工作
    if not all_articles:
        print("📰 RSS抓取失败，返回示例新闻数据")
        all_articles = [
            {
                "id": "sample-1",
                "title": "Federal Reserve Maintains Interest Rates",
                "title_zh": "美联储维持利率不变",
                "summary": "The Federal Reserve decided to keep interest rates unchanged at their latest meeting.",
                "summary_zh": "美联储在最新会议中决定保持利率不变。",
                "url": "https://example.com/fed-rates",
                "source": "Sample News",
                "published_at": "2025-07-30T10:00:00Z",
                "impact_score": 7.5,
                "sentiment_score": 0.0,
                "affected_symbols": ["SPY", "TLT", "DXY"],
                "confidence_score": 0.85,
                "news_type": "factual"
            },
            {
                "id": "sample-2", 
                "title": "Tech Stocks Rally on Earnings Beat",
                "title_zh": "科技股因财报超预期而上涨",
                "summary": "Major technology companies posted better-than-expected quarterly earnings.",
                "summary_zh": "主要科技公司公布了超出预期的季度财报。",
                "url": "https://example.com/tech-rally",
                "source": "Sample News",
                "published_at": "2025-07-30T09:30:00Z",
                "impact_score": 6.2,
                "sentiment_score": 0.3,
                "affected_symbols": ["QQQ", "AAPL", "MSFT"],
                "confidence_score": 0.78,
                "news_type": "factual"
            }
        ]
    
    # 如果没有获取到任何新闻，返回样本数据
    if not all_articles:
        print("⚠️ 未获取到实时新闻，返回样本数据")
        return [
            {
                "id": "sample1",
                "title": "Markets Open Higher on Economic Data",
                "summary": "Stock markets opened higher following positive economic indicators and corporate earnings reports.",
                "url": "https://example.com/news/sample1",
                "source": "Sample News",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "impact_score": 6.5,
                "sentiment_score": 0.3,
                "affected_symbols": ["SPY", "QQQ"],
                "confidence_score": 0.8
            },
            {
                "id": "sample2", 
                "title": "Tech Stocks Show Strong Performance",
                "summary": "Technology sector continues to outperform with major companies reporting solid quarterly results.",
                "url": "https://example.com/news/sample2",
                "source": "Sample News",
                "published_at": datetime.now(timezone.utc).isoformat(),
                "impact_score": 7.2,
                "sentiment_score": 0.5,
                "affected_symbols": ["QQQ", "TSLA", "NVDA"],
                "confidence_score": 0.85
            }
        ]
    
    # 应用事件去重机制
    if all_articles:
        print(f"\n🔄 开始事件去重，原始新闻数量: {len(all_articles)}")
        all_articles = deduplicate_news_by_events(all_articles)
        print(f"✅ 去重后新闻数量: {len(all_articles)}")
    
    # 按发布时间排序，返回最新的文章
    all_articles.sort(key=lambda x: x.get("published_at", ""), reverse=True)
    
    print(f"✅ 最终返回 {len(all_articles)} 条去重新闻")
    return all_articles[:limit]

@app.get("/api/v1/news/articles/{article_id}")
async def get_article_detail(article_id: str):
    """获取单篇新闻详情"""
    try:
        # 先获取所有新闻，然后找到对应的文章
        articles = await get_articles(limit=100)
        
        for article in articles:
            if article["id"] == article_id:
                # 确保summary_zh包含中文翻译
                if not article.get("summary_zh") or article.get("summary_zh") == article.get("summary"):
                    article["summary_zh"] = translate_to_chinese(article.get("summary", ""))
                return article
        
        # 如果没找到，返回404
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="文章未找到")
        
    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(status_code=500, detail=f"获取文章详情失败: {str(e)}")

@app.post("/api/v1/news/translate")
async def translate_news(request: Dict[str, str]):
    """翻译新闻标题和摘要为中文"""
    try:
        title = request.get("title", "")
        summary = request.get("summary", "")
        
        translation = get_chinese_translation(title, summary)
        
        return {
            "original_title": title,
            "translated_title": translation["title_zh"],
            "original_summary": summary,
            "translated_summary": translation["summary_zh"],
            "status": "success"
        }
    except Exception as e:
        return {
            "error": f"翻译失败: {str(e)}",
            "status": "error"
        }

@app.post("/api/v1/news/scrape")
async def scrape_news():
    """手动触发新闻抓取"""
    try:
        # 这里直接调用我们的新闻抓取函数
        articles = await get_articles(limit=50)
        return {
            "message": "新闻抓取成功",
            "count": len(articles),
            "status": "success"
        }
    except Exception as e:
        return {
            "message": f"新闻抓取失败: {str(e)}",
            "count": 0,
            "status": "error"
        }

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

@app.get("/api/v1/symbols/search")
async def search_symbols(q: str = Query(..., description="搜索关键词")):
    """智能搜索交易品种"""
    query = q.lower().strip()
    if not query:
        return {"results": []}
    
    results = []
    for symbol, info in TRADING_SYMBOLS_DATABASE.items():
        # 检查symbol代码匹配
        if query in symbol.lower():
            results.append({
                "symbol": symbol,
                "name": info["name"],
                "category": info["category"],
                "match_type": "symbol"
            })
            continue
        
        # 检查名称匹配
        if query in info["name"].lower():
            results.append({
                "symbol": symbol,
                "name": info["name"],
                "category": info["category"],
                "match_type": "name"
            })
            continue
        
        # 检查关键词匹配
        for keyword in info["keywords"]:
            if query in keyword.lower():
                results.append({
                    "symbol": symbol,
                    "name": info["name"],
                    "category": info["category"],
                    "match_type": "keyword"
                })
                break
    
    # 按匹配类型排序：symbol > name > keyword
    match_order = {"symbol": 0, "name": 1, "keyword": 2}
    results.sort(key=lambda x: match_order.get(x["match_type"], 3))
    
    return {"results": results[:20]}  # 限制返回20个结果

@app.get("/api/v1/symbols/categories")
async def get_symbol_categories():
    """获取品种分类"""
    categories = {}
    for symbol, info in TRADING_SYMBOLS_DATABASE.items():
        category = info["category"]
        if category not in categories:
            categories[category] = []
        categories[category].append({
            "symbol": symbol,
            "name": info["name"]
        })
    
    return {"categories": categories}

@app.get("/api/v1/smart-analysis/supported-symbols")
async def get_supported_symbols():
    """获取支持的交易品种列表 (兼容性接口)"""
    return {
        "trading_symbols": list(TRADING_SYMBOLS_DATABASE.keys()),
        "symbol_categories": {
            category: [s for s, info in TRADING_SYMBOLS_DATABASE.items() if info["category"] == category]
            for category in set(info["category"] for info in TRADING_SYMBOLS_DATABASE.values())
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

@app.get("/api/v1/stats/dashboard")
async def get_dashboard_stats():
    """获取Dashboard统计信息"""
    import time
    return {
        "news_sources": _stats["news_sources"],
        "claude_api_calls": _stats["claude_api_calls"],
        "total_articles": _stats["total_articles"],
        "last_update": _stats["last_update"],
        "cache_status": {
            "has_cache": _news_cache["data"] is not None,
            "cache_size": len(_news_cache["data"]) if _news_cache["data"] else 0,
            "cache_age_seconds": int(time.time() - _news_cache["timestamp"]) if _news_cache["timestamp"] else 0
        },
        "system_status": {
            "uptime_seconds": int(time.time()),
            "cache_duration": CACHE_DURATION
        }
    }

# 关注名单API
@app.get("/api/v1/watchlist")
async def get_watchlist():
    """获取关注名单"""
    return _watchlist

@app.post("/api/v1/watchlist/add")
async def add_to_watchlist(request: dict):
    """添加到关注名单"""
    symbol = request.get("symbol", "").upper()
    if not symbol:
        return {"error": "Symbol is required"}
    
    # 验证symbol是否在数据库中
    if symbol not in TRADING_SYMBOLS_DATABASE:
        return {"error": f"Symbol {symbol} not supported"}
    
    if symbol not in _watchlist["symbols"]:
        _watchlist["symbols"].append(symbol)
        _watchlist["updated_at"] = datetime.now(timezone.utc).isoformat()
        if not _watchlist["created_at"]:
            _watchlist["created_at"] = _watchlist["updated_at"]
    
    return {"success": True, "watchlist": _watchlist}

@app.post("/api/v1/watchlist/remove")
async def remove_from_watchlist(request: dict):
    """从关注名单移除"""
    symbol = request.get("symbol", "").upper()
    if symbol in _watchlist["symbols"]:
        _watchlist["symbols"].remove(symbol)
        _watchlist["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    return {"success": True, "watchlist": _watchlist}

@app.get("/api/v1/watchlist/news")
async def get_watchlist_news(hours: int = Query(24, ge=1, le=168)):
    """获取关注品种相关新闻，按影响程度排序"""
    if not _watchlist["symbols"]:
        return {"message": "No symbols in watchlist", "news": []}
    
    # 获取所有缓存的新闻
    all_news = _news_cache["data"] if _news_cache["data"] else []
    
    # 筛选关注品种相关的新闻
    relevant_news = []
    for article in all_news:
        affected_symbols = article.get("affected_symbols", [])
        # 检查是否有交集
        if any(symbol in _watchlist["symbols"] for symbol in affected_symbols):
            # 计算与关注品种的相关性得分
            relevance_score = 0
            for symbol in affected_symbols:
                if symbol in _watchlist["symbols"]:
                    relevance_score += article.get("impact_score", 0)
            
            article_copy = article.copy()
            article_copy["relevance_score"] = relevance_score
            article_copy["watched_symbols"] = [s for s in affected_symbols if s in _watchlist["symbols"]]
            relevant_news.append(article_copy)
    
    # 按影响程度排序 (从大到小)
    relevant_news.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
    
    return {
        "watchlist_symbols": _watchlist["symbols"],
        "total_found": len(relevant_news),
        "news": relevant_news
    }

@app.get("/api/v1/trading-advice")
async def get_trading_advice():
    """获取AI交易建议"""
    try:
        # 获取关注名单中的品种
        watchlist_symbols = _watchlist.get("symbols", [])
        
        if not watchlist_symbols:
            return {
                "advice": [],
                "market_sentiment": {
                    "overall": "NEUTRAL",
                    "confidence": 0.5
                },
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
        
        # 生成模拟交易建议 (实际应基于新闻分析)
        advice = []
        current_time = datetime.now(timezone.utc)
        
        # 模拟价格数据
        price_data = {
            "SPY": 400.0, "QQQ": 350.0, "AAPL": 150.0, "TSLA": 250.0,
            "NVDA": 400.0, "MSFT": 300.0, "GOOGL": 120.0, "GLD": 180.0,
            "USDCNY": 7.2, "BABA": 85.0, "JD": 25.0
        }
        
        for symbol in watchlist_symbols[:5]:  # 最多5个建议
            base_price = price_data.get(symbol, 100.0)
            direction = random.choice(["BUY", "SELL", "HOLD"])
            confidence = random.uniform(0.6, 0.9)
            risk_level = random.choice(["LOW", "MEDIUM", "HIGH"])
            
            if direction == "BUY":
                entry_price = base_price * random.uniform(0.98, 1.02)
                target_price = entry_price * random.uniform(1.05, 1.15)
                stop_loss = entry_price * random.uniform(0.90, 0.95)
                reasoning = f"基于最新财报和市场动态分析，{symbol}显示强劲的上涨动能。技术指标显示突破关键阻力位，建议逢低买入。"
            elif direction == "SELL":
                entry_price = base_price * random.uniform(0.98, 1.02)
                target_price = entry_price * random.uniform(0.85, 0.95)
                stop_loss = entry_price * random.uniform(1.05, 1.10)
                reasoning = f"市场情绪转谨慎，{symbol}面临技术面压力。建议减仓或做空，等待更好的入场时机。"
            else:  # HOLD
                entry_price = base_price
                target_price = base_price * random.uniform(1.02, 1.08)
                stop_loss = base_price * random.uniform(0.92, 0.98)
                reasoning = f"{symbol}目前处于整理阶段，建议持有观望，等待明确的方向性信号。"
            
            advice_item = {
                "id": f"advice_{symbol}_{int(current_time.timestamp())}",
                "symbol": symbol,
                "direction": direction,
                "entry_price": round(entry_price, 2),
                "target_price": round(target_price, 2),
                "stop_loss": round(stop_loss, 2),
                "confidence": round(confidence, 2),
                "reasoning": reasoning,
                "news_sources": ["财经新闻", "技术分析", "市场情报"],
                "time_horizon": random.choice(["短期(1-7天)", "中期(1-4周)", "长期(1-3月)"]),
                "risk_level": risk_level,
                "created_at": current_time.isoformat()
            }
            advice.append(advice_item)
        
        # 模拟市场情绪
        market_sentiment = {
            "overall": random.choice(["BULLISH", "BEARISH", "NEUTRAL"]),
            "confidence": round(random.uniform(0.6, 0.9), 2)
        }
        
        return {
            "advice": advice,
            "market_sentiment": market_sentiment,
            "generated_at": current_time.isoformat()
        }
        
    except Exception as e:
        print(f"获取交易建议失败: {e}")
        return {
            "advice": [],
            "market_sentiment": {
                "overall": "NEUTRAL",
                "confidence": 0.5
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }

# WebSocket端点
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 等待客户端消息
            data = await websocket.receive_text()
            print(f"收到WebSocket消息: {data}")
            
            # 发送确认消息
            await manager.send_personal_message(f"Echo: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 模拟价格数据生成器
async def generate_price_data():
    """生成模拟价格数据 - 基于关注名单"""
    import random
    import json
    
    # 从数据库生成价格数据 (模拟数据，仅供演示)
    all_base_prices = {}
    price_units = {}  # 存储价格单位信息
    
    for symbol in TRADING_SYMBOLS_DATABASE.keys():
        if symbol.startswith("00") and symbol.endswith(".SS"):  # A股指数
            all_base_prices[symbol] = 3000.0
            price_units[symbol] = "点"
        elif symbol.startswith("39") and symbol.endswith(".SZ"):  # 深圳指数
            all_base_prices[symbol] = 12000.0
            price_units[symbol] = "点"
        elif symbol.startswith("60") and symbol.endswith(".SS"):  # 上海股票
            all_base_prices[symbol] = 200.0
            price_units[symbol] = "元"
        elif symbol.startswith("00") and symbol.endswith(".SZ"):  # 深圳股票
            all_base_prices[symbol] = 50.0
            price_units[symbol] = "元"
        elif symbol.endswith(".HK"):  # 港股
            all_base_prices[symbol] = 100.0
            price_units[symbol] = "港元"
        elif symbol.endswith("=F"):  # 期货
            if "GC" in symbol:  # 黄金
                all_base_prices[symbol] = 2000.0
                price_units[symbol] = "美元/盎司"
            elif "CL" in symbol or "BZ" in symbol:  # 原油
                all_base_prices[symbol] = 75.0
                price_units[symbol] = "美元/桶"
            elif "SI" in symbol:  # 白银
                all_base_prices[symbol] = 25.0
                price_units[symbol] = "美元/盎司"
            elif "NG" in symbol:  # 天然气
                all_base_prices[symbol] = 3.5
                price_units[symbol] = "美元/百万英热单位"
            else:
                all_base_prices[symbol] = 4000.0  # 股指期货
                price_units[symbol] = "点"
        elif "USD" in symbol:  # 外汇
            if symbol == "USDCNY":
                all_base_prices[symbol] = 7.2
                price_units[symbol] = "人民币"
            elif symbol == "USDJPY":
                all_base_prices[symbol] = 150.0
                price_units[symbol] = "日元"
            else:
                all_base_prices[symbol] = 1.1
                price_units[symbol] = "汇率"
        elif symbol.endswith("-USD"):  # 加密货币
            if "BTC" in symbol:
                all_base_prices[symbol] = 40000.0
                price_units[symbol] = "美元"
            elif "ETH" in symbol:
                all_base_prices[symbol] = 2500.0
                price_units[symbol] = "美元"
            else:
                all_base_prices[symbol] = 300.0
                price_units[symbol] = "美元"
        elif symbol in ["AU0", "AG0", "CU0", "RB0", "SC0"]:  # 国内期货
            if symbol == "AU0":
                all_base_prices[symbol] = 450.0
                price_units[symbol] = "元/克"
            elif symbol == "AG0":
                all_base_prices[symbol] = 5500.0
                price_units[symbol] = "元/公斤"
            elif symbol == "CU0":
                all_base_prices[symbol] = 70000.0
                price_units[symbol] = "元/吨"
            elif symbol == "RB0":
                all_base_prices[symbol] = 3800.0
                price_units[symbol] = "元/吨"
            elif symbol == "SC0":
                all_base_prices[symbol] = 600.0
                price_units[symbol] = "元/桶"
        else:  # 美股等其他
            if symbol in ["SPY", "QQQ", "IWM", "GLD", "SLV"]:
                all_base_prices[symbol] = {"SPY": 440.0, "QQQ": 380.0, "IWM": 210.0, "GLD": 190.0, "SLV": 24.0}[symbol]
                price_units[symbol] = "美元"
            elif symbol in ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "NFLX"]:
                prices = {"AAPL": 175.0, "MSFT": 350.0, "GOOGL": 140.0, "AMZN": 160.0, "TSLA": 200.0, "NVDA": 850.0, "META": 320.0, "NFLX": 450.0}
                all_base_prices[symbol] = prices.get(symbol, 150.0)
                price_units[symbol] = "美元"
            else:
                all_base_prices[symbol] = 100.0
                price_units[symbol] = "美元"
    
    # 只为关注名单中的品种初始化价格
    def get_watchlist_prices():
        watchlist_symbols = _watchlist.get("symbols", [])
        return {symbol: all_base_prices.get(symbol, 100.0) for symbol in watchlist_symbols}
    
    prices = get_watchlist_prices()
    
    while True:
        # 动态更新价格字典（当关注名单变化时）
        current_watchlist = _watchlist.get("symbols", [])
        
        # 添加新的关注品种
        for symbol in current_watchlist:
            if symbol not in prices:
                prices[symbol] = all_base_prices.get(symbol, 100.0)
        
        # 移除不在关注名单中的品种
        prices = {k: v for k, v in prices.items() if k in current_watchlist}
        
        # 更新价格 (模拟市场波动)
        for symbol in prices:
            change_pct = random.uniform(-0.5, 0.5) / 100  # -0.5% 到 +0.5%
            prices[symbol] *= (1 + change_pct)
            prices[symbol] = round(prices[symbol], 2)
        
        # 准备价格数据 (包含单位信息)
        prices_with_units = {}
        for symbol, price in prices.items():
            prices_with_units[symbol] = {
                "price": price,
                "unit": price_units.get(symbol, "")
            }
        
        price_data = {
            "type": "price_update",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "prices": prices.copy(),  # 兼容性
            "prices_with_units": prices_with_units  # 新格式包含单位
        }
        
        # 广播给所有连接的客户端
        await manager.broadcast(json.dumps(price_data))
        
        # 等待5秒
        await asyncio.sleep(5)

# A股股票数据管理API
@app.get("/api/v1/stocks/a-stocks")
async def get_a_stocks(limit: int = Query(100, ge=1, le=1000)):
    """获取A股股票列表"""
    stocks = list(_a_stock_database.values())[:limit]
    return {
        "stocks": stocks,
        "total_count": len(_a_stock_database),
        "returned_count": len(stocks)
    }

@app.get("/api/v1/stocks/a-stocks/{stock_code}")
async def get_a_stock_detail(stock_code: str):
    """获取单只A股详细信息"""
    stock = _a_stock_database.get(stock_code)
    if not stock:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="股票未找到")
    return stock

@app.post("/api/v1/stocks/crawler/run")
async def run_stock_crawler():
    """运行股票数据爬虫"""
    try:
        print("开始执行股票数据爬取...")
        
        # 动态导入爬虫模块
        import sys
        import os
        sys.path.append(os.path.dirname(__file__))
        
        from stock_crawler import StockCrawler
        
        crawler = StockCrawler()
        stocks = crawler.crawl_all_stocks()
        
        # 更新内存数据库
        updated_count = 0
        for stock in stocks:
            code = stock.get('code')
            if code:
                _a_stock_database[code] = stock
                updated_count += 1
        
        # 同步更新交易品种数据库
        sync_trading_symbols_with_a_stocks()
        
        return {
            "success": True,
            "message": "股票数据爬取完成",
            "crawled_count": len(stocks),
            "updated_count": updated_count,
            "total_stocks": len(_a_stock_database)
        }
        
    except Exception as e:
        print(f"股票爬取失败: {e}")
        return {
            "success": False,
            "message": f"股票数据爬取失败: {str(e)}",
            "crawled_count": 0,
            "updated_count": 0,
            "total_stocks": len(_a_stock_database)
        }

@app.post("/api/v1/stocks/import")
async def import_stock_data(request: dict):
    """导入股票数据"""
    try:
        stocks = request.get("stocks", [])
        if not stocks:
            return {"success": False, "message": "没有提供股票数据"}
        
        imported_count = 0
        for stock in stocks:
            code = stock.get("code")
            if code and isinstance(stock, dict):
                _a_stock_database[code] = {
                    "code": code,
                    "name": stock.get("name", ""),
                    "full_name": stock.get("full_name", ""),
                    "list_date": stock.get("list_date", ""),
                    "industry": stock.get("industry", ""),
                    "area": stock.get("area", ""),
                    "market": stock.get("market", ""),
                    "exchange": stock.get("exchange", ""),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
                imported_count += 1
        
        # 同步更新交易品种数据库
        sync_trading_symbols_with_a_stocks()
        
        return {
            "success": True,
            "message": f"成功导入 {imported_count} 只股票",
            "imported_count": imported_count,
            "total_stocks": len(_a_stock_database)
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"导入失败: {str(e)}"
        }

def sync_trading_symbols_with_a_stocks():
    """同步A股数据到交易品种数据库"""
    global TRADING_SYMBOLS_DATABASE
    
    for code, stock in _a_stock_database.items():
        symbol_key = code  # 使用股票代码作为key
        market = stock.get('market', 'SZ')
        
        # 为上交所股票添加.SS后缀，深交所添加.SZ后缀
        if market == 'SH':
            symbol_with_suffix = f"{code}.SS"
        else:
            symbol_with_suffix = f"{code}.SZ"
        
        # 生成关键词
        keywords = [stock.get('name', ''), code]
        if stock.get('industry'):
            keywords.append(stock.get('industry'))
        
        # 更新交易品种数据库
        TRADING_SYMBOLS_DATABASE[code] = {
            "name": stock.get('name', ''),
            "category": f"A股{stock.get('industry', '个股')}",
            "keywords": [kw for kw in keywords if kw]
        }
        
        # 同时添加带后缀的版本
        TRADING_SYMBOLS_DATABASE[symbol_with_suffix] = {
            "name": stock.get('name', ''),
            "category": f"A股{stock.get('industry', '个股')}",
            "keywords": [kw for kw in keywords if kw]
        }

@app.get("/api/v1/stocks/stats")
async def get_stock_stats():
    """获取股票数据统计"""
    if not _a_stock_database:
        return {
            "total_stocks": 0,
            "by_market": {},
            "by_industry": {},
            "by_area": {}
        }
    
    # 按市场统计
    market_stats = {}
    industry_stats = {}
    area_stats = {}
    
    for stock in _a_stock_database.values():
        # 市场统计
        market = stock.get('market', 'Unknown')
        market_stats[market] = market_stats.get(market, 0) + 1
        
        # 行业统计
        industry = stock.get('industry', 'Unknown')
        industry_stats[industry] = industry_stats.get(industry, 0) + 1
        
        # 地区统计
        area = stock.get('area', 'Unknown')
        area_stats[area] = area_stats.get(area, 0) + 1
    
    return {
        "total_stocks": len(_a_stock_database),
        "by_market": market_stats,
        "by_industry": dict(sorted(industry_stats.items(), key=lambda x: x[1], reverse=True)[:20]),
        "by_area": dict(sorted(area_stats.items(), key=lambda x: x[1], reverse=True)[:20])
    }

# 启动事件处理器
@app.on_event("startup")
async def startup_event():
    # 启动价格数据推送任务
    asyncio.create_task(generate_price_data())
    print("🚀 实时价格推送服务已启动")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)