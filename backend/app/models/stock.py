from sqlalchemy import Column, Integer, String, DateTime, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.core.database import Base


class AStock(Base):
    """A股股票信息表"""
    __tablename__ = "a_stocks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 股票基本信息
    symbol = Column(String(10), unique=True, index=True, nullable=False, comment="股票代码 (如: 000001)")
    ts_code = Column(String(12), unique=True, index=True, nullable=False, comment="TS代码 (如: 000001.SZ)")
    name = Column(String(20), nullable=False, comment="股票名称")
    area = Column(String(10), comment="所在地域")
    industry = Column(String(20), comment="所属行业")
    market = Column(String(10), comment="市场类型 (主板/中小板/创业板/科创板)")
    exchange = Column(String(10), nullable=False, comment="交易所 (SZ/SH)")
    
    # 拼音相关字段
    name_pinyin = Column(String(100), comment="股票名称全拼音")
    name_pinyin_short = Column(String(20), index=True, comment="股票名称拼音首字母")
    
    # 状态信息
    list_status = Column(String(1), default='L', comment="上市状态 L上市 D退市 P暂停上市")
    list_date = Column(String(8), comment="上市日期")
    delist_date = Column(String(8), comment="退市日期")
    is_hs = Column(String(1), comment="是否沪深港通标的 N否 H沪股通 S深股通")
    
    # 系统字段
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    # 创建复合索引
    __table_args__ = (
        Index('idx_symbol_exchange', 'symbol', 'exchange'),
        Index('idx_name_pinyin_short', 'name_pinyin_short'),
        Index('idx_list_status', 'list_status'),
        Index('idx_market_exchange', 'market', 'exchange'),
    )
    
    def __repr__(self):
        return f"<AStock(symbol='{self.symbol}', name='{self.name}', exchange='{self.exchange}')>"


class StockWatchlist(Base):
    """股票关注列表"""
    __tablename__ = "stock_watchlist"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, comment="股票代码")
    ts_code = Column(String(12), nullable=False, comment="TS代码")
    name = Column(String(20), nullable=False, comment="股票名称")
    
    # 关注设置
    is_active = Column(Boolean, default=True, comment="是否激活监控")
    alert_enabled = Column(Boolean, default=False, comment="是否启用提醒")
    notes = Column(String(200), comment="备注信息")
    
    # 系统字段
    added_at = Column(DateTime, default=datetime.utcnow, comment="添加时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment="更新时间")
    
    __table_args__ = (
        Index('idx_watchlist_symbol', 'symbol'),
        Index('idx_watchlist_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<StockWatchlist(symbol='{self.symbol}', name='{self.name}')>"