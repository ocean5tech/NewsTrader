from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import os
import feedparser
import hashlib
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

@app.get("/api/v1/news/articles")
async def get_articles(limit: int = Query(20, ge=1, le=100)):
    """获取实时新闻文章 - 临时返回示例数据"""
    # 由于RSS抓取超时问题，临时返回示例数据
    print("📰 返回示例新闻数据")
    all_articles = [
        {
            "id": "sample-1",
            "title": "Federal Reserve Maintains Interest Rates at Current Level",
            "title_zh": "美联储维持当前利率水平不变",
            "summary": "The Federal Reserve decided to keep interest rates unchanged at their latest meeting, citing economic stability concerns.",
            "summary_zh": "美联储在最新会议中决定保持利率不变，理由是经济稳定性考虑。",
            "url": "https://www.federalreserve.gov/newsevents/pressreleases/monetary.htm",
            "source": "Federal Reserve",
            "published_at": "2025-07-30T10:00:00Z",
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
            "published_at": "2025-07-30T09:30:00Z",
            "impact_score": 6.2,
            "sentiment_score": 0.3,
            "affected_symbols": ["QQQ", "AAPL", "MSFT"],
            "confidence_score": 0.78,
            "news_type": "factual"
        },
        {
            "id": "sample-3",
            "title": "Oil Prices Rise on Supply Concerns",
            "title_zh": "石油价格因供应担忧而上涨",
            "summary": "Crude oil prices increased following reports of potential supply disruptions in key producing regions.",
            "summary_zh": "原油价格在主要产油地区可能出现供应中断的报告后上涨。",
            "url": "https://www.reuters.com/business/energy/",
            "source": "Reuters",
            "published_at": "2025-07-30T08:45:00Z",
            "impact_score": 6.8,
            "sentiment_score": 0.2,
            "affected_symbols": ["CL=F", "XLE", "CVX"],
            "confidence_score": 0.73,
            "news_type": "factual"
        },
        {
            "id": "sample-4",
            "title": "European Central Bank Signals Policy Changes",
            "title_zh": "欧洲央行发出政策变化信号",
            "summary": "The ECB indicated potential adjustments to monetary policy in response to evolving economic conditions.",
            "summary_zh": "欧央行表示可能根据不断变化的经济状况调整货币政策。",
            "url": "https://www.ecb.europa.eu/press/pr/date/2025/html/",
            "source": "ECB",
            "published_at": "2025-07-30T08:00:00Z",
            "impact_score": 7.2,
            "sentiment_score": -0.1,
            "affected_symbols": ["EURUSD", "EFA", "VGK"],
            "confidence_score": 0.82,
            "news_type": "factual"
        },
        {
            "id": "sample-5",
            "title": "Gold Reaches New High Amid Market Uncertainty",
            "title_zh": "黄金在市场不确定性中创新高",
            "summary": "Gold prices hit record levels as investors seek safe-haven assets during volatile market conditions.",
            "summary_zh": "在市场波动期间，投资者寻求避险资产，黄金价格创历史新高。",
            "url": "https://www.bloomberg.com/markets/commodities",
            "source": "Bloomberg",
            "published_at": "2025-07-30T07:30:00Z",
            "impact_score": 6.5,
            "sentiment_score": 0.0,
            "affected_symbols": ["GLD", "GC=F", "GOLD"],
            "confidence_score": 0.76,
            "news_type": "factual"
        }
    ]
    
    return all_articles[:limit]

@app.get("/api/v1/news/articles_with_rss")  
async def get_articles_with_rss(limit: int = Query(20, ge=1, le=100)):
    """获取实时新闻文章 - RSS版本（可能超时）"""
    # 优先使用可靠的Bloomberg源，减少超时风险
    news_sources = [
        ("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg"),
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

@app.get("/api/v1/smart-analysis/supported-symbols")
async def get_supported_symbols():
    """获取支持的交易品种列表"""
    return {
        "trading_symbols": [
            "SPY", "QQQ", "GLD", "CL=F", "GC=F", "ES=F",
            "000001.SS", "399001.SZ", "HSI", "BABA", "JD", "TCEHY",
            "XAUUSD", "XAGUSD", "USOIL", "BRENT",
            "USDCNY", "EURUSD", "GBPUSD"
        ],
        "symbol_categories": {
            "us_markets": ["SPY", "QQQ", "GLD", "CL=F", "GC=F", "ES=F"],
            "chinese_markets": ["000001.SS", "399001.SZ", "HSI", "BABA", "JD", "TCEHY"],
            "commodities": ["XAUUSD", "XAGUSD", "USOIL", "BRENT"],
            "currencies": ["USDCNY", "EURUSD", "GBPUSD"]
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)