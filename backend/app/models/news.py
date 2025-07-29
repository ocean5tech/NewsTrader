from sqlalchemy import Column, String, DateTime, Float, Text, JSON, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
import uuid
from datetime import datetime


class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String, nullable=False, index=True)
    content = Column(Text)
    summary = Column(Text)
    url = Column(String, unique=True, nullable=False)
    source = Column(String, nullable=False)
    published_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # AI Analysis fields
    impact_score = Column(Float, default=0.0)  # 0-10 scale
    sentiment_score = Column(Float, default=0.0)  # -1 to 1
    affected_symbols = Column(JSON)  # List of trading symbols
    keywords = Column(JSON)  # Extracted keywords
    categories = Column(JSON)  # News categories
    
    # Claude AI analysis
    claude_analysis = Column(JSON)  # Full Claude response
    confidence_score = Column(Float, default=0.0)  # 0-1 scale


class ImpactWeight(Base):
    __tablename__ = "impact_weights"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    symbol = Column(String, nullable=False, index=True)
    predicted_impact = Column(Float, nullable=False)  # -1 to 1
    actual_impact = Column(Float)  # Measured after time period
    time_horizon = Column(Integer, default=24)  # Hours
    created_at = Column(DateTime, default=datetime.utcnow)
    measured_at = Column(DateTime)


class BacktestResult(Base):
    __tablename__ = "backtest_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), nullable=False)
    symbol = Column(String, nullable=False)
    predicted_direction = Column(String)  # up/down/neutral
    actual_direction = Column(String)
    predicted_magnitude = Column(Float)
    actual_magnitude = Column(Float)
    accuracy_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)