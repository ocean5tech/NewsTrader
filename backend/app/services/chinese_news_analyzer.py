"""
中文新闻分析器 - 处理中文财经新闻并分析对交易品种的影响
"""
import re
import jieba
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from collections import Counter
import requests
from bs4 import BeautifulSoup
from app.core.config import settings

# 配置jieba分词
jieba.initialize()

logger = logging.getLogger(__name__)

@dataclass
class ImpactAnalysis:
    """影响分析结果"""
    primary_symbols: List[Dict[str, float]]  # 主要受影响的交易品种
    secondary_symbols: List[Dict[str, float]]  # 次要受影响的交易品种
    sentiment_score: float  # 情感评分 -1 to 1
    impact_score: float  # 影响强度 0-10
    confidence: float  # 置信度 0-1
    keywords: List[str]  # 关键词
    analysis_reason: str  # 分析理由

@dataclass 
class NewsAnalysisRequest:
    """新闻分析请求"""
    content: str
    title: str
    target_symbol: Optional[str] = None  # 如果指定，进行反向分析

class ChineseNewsAnalyzer:
    """中文新闻分析器"""
    
    def __init__(self):
        # 交易品种映射表
        self.symbol_keywords = {
            # A股相关
            "000001.SS": ["上证", "沪指", "A股", "上海证券", "沪市"],
            "399001.SZ": ["深证", "深圳成指", "深市", "中小板"],
            "HSI": ["恒指", "香港", "港股", "恒生指数"],
            
            # 美股
            "SPY": ["标普", "S&P500", "美股", "纳斯达克指数"],
            "QQQ": ["纳斯达克", "科技股", "NASDAQ"],
            "BABA": ["阿里巴巴", "阿里", "电商", "淘宝", "天猫"],
            "JD": ["京东", "刘强东", "电商平台"],
            
            # 商品期货
            "GC=F": ["黄金", "金价", "贵金属", "避险"],
            "CL=F": ["原油", "石油", "油价", "WTI", "布伦特"],
            "XAUUSD": ["现货黄金", "国际金价"],
            "USOIL": ["美油", "原油期货"],
            "BRENT": ["布油", "布伦特原油"],
            
            # 汇率
            "USDCNY": ["人民币", "汇率", "美元兑人民币", "离岸人民币", "在岸人民币"],
            "EURUSD": ["欧元", "美元", "欧美货币对"],
            
            # 行业板块
            "REAL_ESTATE": settings.CHINESE_MARKET_KEYWORDS[19:20],  # 房地产
            "NEW_ENERGY": ["新能源", "电动车", "锂电池", "光伏", "风电"],
            "TECH": ["芯片", "半导体", "人工智能", "5G", "云计算"],
            "PHARMA": ["医药", "生物医药", "疫苗", "中药"],
            "LIQUOR": ["白酒", "茅台", "五粮液", "酒类"],
            "BANKING": ["银行", "金融", "贷款", "存款利率"],
            "INSURANCE": ["保险", "人寿", "财险"],
            "SECURITIES": ["券商", "证券", "经纪业务"]
        }
        
        # 情感词典
        self.positive_words = [
            "上涨", "涨幅", "利好", "盈利", "增长", "突破", "创新高", "买入", 
            "推荐", "看好", "乐观", "超预期", "强势", "反弹", "企稳"
        ]
        
        self.negative_words = [
            "下跌", "跌幅", "利空", "亏损", "下滑", "破位", "创新低", "卖出",
            "看空", "悲观", "不及预期", "疲软", "调整", "暴跌", "恐慌"
        ]
        
        # 影响强度关键词
        self.high_impact_words = [
            "央行", "货币政策", "利率", "重大", "突发", "紧急", "暴涨", "暴跌",
            "停牌", "熔断", "政策", "法规", "制裁", "战争", "疫情"
        ]
        
    def analyze_news(self, request: NewsAnalysisRequest) -> ImpactAnalysis:
        """分析新闻内容"""
        
        if request.target_symbol:
            # 反向分析：查看这条新闻对指定品种的影响
            return self._reverse_analysis(request)
        else:
            # 正向分析：判断哪些品种最受影响
            return self._forward_analysis(request)
    
    def _forward_analysis(self, request: NewsAnalysisRequest) -> ImpactAnalysis:
        """正向分析：自动判断受影响的品种"""
        
        # 合并标题和内容
        full_text = f"{request.title} {request.content}"
        
        # 分词和关键词提取
        keywords = self._extract_keywords(full_text)
        
        # 计算各品种的影响分数
        symbol_scores = {}
        for symbol, symbol_keywords in self.symbol_keywords.items():
            score = self._calculate_symbol_impact(full_text, symbol_keywords, keywords)
            if score > 0:
                symbol_scores[symbol] = score
        
        # 排序并分为主要和次要影响
        sorted_symbols = sorted(symbol_scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_symbols = [{"symbol": s[0], "impact": s[1]} for s in sorted_symbols[:3]]
        secondary_symbols = [{"symbol": s[0], "impact": s[1]} for s in sorted_symbols[3:6]]
        
        # 计算情感评分
        sentiment = self._calculate_sentiment(full_text, keywords)
        
        # 计算总体影响强度
        impact_score = self._calculate_impact_intensity(full_text, keywords)
        
        # 计算置信度
        confidence = self._calculate_confidence(full_text, primary_symbols)
        
        # 生成分析理由
        reason = self._generate_analysis_reason(keywords, primary_symbols, sentiment, impact_score)
        
        return ImpactAnalysis(
            primary_symbols=primary_symbols,
            secondary_symbols=secondary_symbols,
            sentiment_score=sentiment,
            impact_score=impact_score,
            confidence=confidence,
            keywords=keywords[:10],  # 返回前10个关键词
            analysis_reason=reason
        )
    
    def _reverse_analysis(self, request: NewsAnalysisRequest) -> ImpactAnalysis:
        """反向分析：分析新闻对指定品种的影响"""
        
        target_symbol = request.target_symbol
        full_text = f"{request.title} {request.content}"
        
        # 获取目标品种的关键词
        if target_symbol not in self.symbol_keywords:
            # 如果不在预定义列表中，返回默认分析
            return self._forward_analysis(request)
        
        target_keywords = self.symbol_keywords[target_symbol]
        all_keywords = self._extract_keywords(full_text)
        
        # 计算对目标品种的具体影响
        target_impact = self._calculate_symbol_impact(full_text, target_keywords, all_keywords)
        
        # 如果影响很小，降低所有分数
        if target_impact < 0.3:
            impact_multiplier = 0.5
        else:
            impact_multiplier = 1.0
        
        # 重新计算各项指标，但以目标品种为中心
        sentiment = self._calculate_sentiment(full_text, all_keywords) * impact_multiplier
        impact_score = self._calculate_impact_intensity(full_text, all_keywords) * impact_multiplier
        confidence = self._calculate_confidence(full_text, [{"symbol": target_symbol, "impact": target_impact}])
        
        # 生成针对性分析理由
        reason = self._generate_reverse_analysis_reason(
            target_symbol, target_impact, all_keywords, sentiment, impact_score
        )
        
        return ImpactAnalysis(
            primary_symbols=[{"symbol": target_symbol, "impact": target_impact}],
            secondary_symbols=[],
            sentiment_score=sentiment,
            impact_score=impact_score,
            confidence=confidence,
            keywords=all_keywords[:10],
            analysis_reason=reason
        )
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # jieba分词
        words = jieba.cut(text)
        
        # 过滤停用词和短词
        filtered_words = []
        stop_words = {"的", "了", "在", "是", "我", "有", "和", "就", "不", "人", "都", "一", "个"}
        
        for word in words:
            if len(word.strip()) > 1 and word not in stop_words:
                filtered_words.append(word.strip())
        
        # 统计词频并返回高频词
        word_count = Counter(filtered_words)
        return [word for word, count in word_count.most_common(20)]
    
    def _calculate_symbol_impact(self, text: str, symbol_keywords: List[str], all_keywords: List[str]) -> float:
        """计算文本对特定交易品种的影响程度"""
        impact_score = 0.0
        
        # 直接关键词匹配
        for keyword in symbol_keywords:
            if keyword in text:
                impact_score += 2.0
                
        # 关键词在提取的关键词中的权重
        for keyword in all_keywords:
            if any(sk in keyword or keyword in sk for sk in symbol_keywords):
                impact_score += 1.0
        
        # normalize到0-1范围
        return min(impact_score / 10.0, 1.0)
    
    def _calculate_sentiment(self, text: str, keywords: List[str]) -> float:
        """计算情感评分"""
        positive_count = sum(1 for word in self.positive_words if word in text)
        negative_count = sum(1 for word in self.negative_words if word in text)
        
        # 在关键词中查找情感词
        for keyword in keywords:
            if any(pos in keyword for pos in self.positive_words):
                positive_count += 1
            if any(neg in keyword for neg in self.negative_words):
                negative_count += 1
        
        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0
        
        # 计算情感倾向 -1 to 1
        sentiment_score = (positive_count - negative_count) / total_sentiment_words
        return max(-1.0, min(1.0, sentiment_score))
    
    def _calculate_impact_intensity(self, text: str, keywords: List[str]) -> float:
        """计算影响强度"""
        intensity = 0.0
        
        # 高影响关键词检查
        for word in self.high_impact_words:
            if word in text:
                intensity += 2.0
        
        # 数字相关的影响（百分比、金额等）
        numbers = re.findall(r'\d+\.?\d*%|\d+\.?\d*亿|\d+\.?\d*万', text)
        intensity += len(numbers) * 0.5
        
        # 文本长度影响（更长的新闻通常更重要）
        text_length_factor = min(len(text) / 1000, 1.0)
        intensity += text_length_factor
        
        # 关键词密度
        keyword_density = len(keywords) / max(len(text.split()), 1) * 100
        intensity += keyword_density * 0.1
        
        # 标准化到0-10范围
        return min(intensity, 10.0)
    
    def _calculate_confidence(self, text: str, primary_symbols: List[Dict]) -> float:
        """计算分析置信度"""
        confidence = 0.5  # 基础置信度
        
        # 如果有明确的交易品种匹配，提高置信度
        if primary_symbols and len(primary_symbols) > 0:
            max_impact = max(symbol["impact"] for symbol in primary_symbols)
            confidence += max_impact * 0.4
        
        # 文本质量影响置信度
        if len(text) > 100:
            confidence += 0.1
        if len(text) > 500:
            confidence += 0.1
            
        return min(confidence, 1.0)
    
    def _generate_analysis_reason(self, keywords: List[str], primary_symbols: List[Dict], 
                                sentiment: float, impact: float) -> str:
        """生成分析理由"""
        
        reason_parts = []
        
        # 关键词分析
        if keywords:
            reason_parts.append(f"检测到关键词：{', '.join(keywords[:5])}")
        
        # 主要影响品种
        if primary_symbols:
            symbols = [s["symbol"] for s in primary_symbols[:2]]
            reason_parts.append(f"主要影响品种：{', '.join(symbols)}")
        
        # 情感分析
        if sentiment > 0.3:
            reason_parts.append("整体情感偏向积极")
        elif sentiment < -0.3:
            reason_parts.append("整体情感偏向消极")
        else:
            reason_parts.append("情感相对中性")
        
        # 影响强度
        if impact > 7:
            reason_parts.append("预期产生重大市场影响")
        elif impact > 4:
            reason_parts.append("预期产生中等市场影响")
        else:
            reason_parts.append("预期产生较小市场影响")
        
        return "；".join(reason_parts) + "。"
    
    def _generate_reverse_analysis_reason(self, target_symbol: str, target_impact: float,
                                        keywords: List[str], sentiment: float, impact: float) -> str:
        """生成反向分析理由"""
        
        reason_parts = []
        
        reason_parts.append(f"针对 {target_symbol} 的专项分析")
        
        if target_impact > 0.6:
            reason_parts.append("该新闻与目标品种高度相关")
        elif target_impact > 0.3:
            reason_parts.append("该新闻与目标品种存在一定关联")
        else:
            reason_parts.append("该新闻与目标品种关联度较低")
        
        # 关键发现
        relevant_keywords = [kw for kw in keywords[:3] if any(
            target_kw in kw for target_kw in self.symbol_keywords.get(target_symbol, [])
        )]
        
        if relevant_keywords:
            reason_parts.append(f"相关要素：{', '.join(relevant_keywords)}")
        
        if sentiment > 0.2:
            reason_parts.append(f"对 {target_symbol} 偏向利好")
        elif sentiment < -0.2:
            reason_parts.append(f"对 {target_symbol} 偏向利空")
        
        return "；".join(reason_parts) + "。"

# 实例化分析器
chinese_analyzer = ChineseNewsAnalyzer()