from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.news import NewsArticle, BacktestResult, ImpactWeight
import yfinance as yf
import asyncio
from concurrent.futures import ThreadPoolExecutor

router = APIRouter()


@router.post("/run/{symbol}")
async def run_backtest(
    symbol: str,
    days_back: int = 30,
    time_horizon_hours: int = 24,
    db: AsyncSession = Depends(get_db)
):
    """Run backtest for a specific symbol"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back)
        
        # Get articles for the symbol in the time period
        query = select(NewsArticle).where(
            and_(
                NewsArticle.published_at >= start_date,
                NewsArticle.published_at <= end_date,
                NewsArticle.affected_symbols.contains([symbol]),
                NewsArticle.impact_score > 0
            )
        ).order_by(NewsArticle.published_at)
        
        result = await db.execute(query)
        articles = result.scalars().all()
        
        if not articles:
            return {
                "message": f"No articles found for {symbol} in the specified period",
                "symbol": symbol,
                "results": []
            }
        
        # Get price data
        price_data = await get_price_data(symbol, start_date, end_date)
        
        # Run backtest for each article
        backtest_results = []
        for article in articles:
            result = await backtest_article(
                article, symbol, price_data, time_horizon_hours, db
            )
            if result:
                backtest_results.append(result)
        
        # Calculate summary statistics
        summary = calculate_backtest_summary(backtest_results)
        
        return {
            "symbol": symbol,
            "time_period": f"{days_back} days",
            "time_horizon_hours": time_horizon_hours,
            "total_predictions": len(backtest_results),
            "summary": summary,
            "results": backtest_results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")


async def get_price_data(symbol: str, start_date: datetime, end_date: datetime) -> Dict:
    """Get price data for backtesting"""
    def fetch_data():
        ticker = yf.Ticker(symbol)
        data = ticker.history(
            start=start_date.date(),
            end=end_date.date(),
            interval="1h"
        )
        return data
    
    # Run in thread pool to avoid blocking
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        data = await loop.run_in_executor(executor, fetch_data)
    
    return data


async def backtest_article(
    article: NewsArticle,
    symbol: str,
    price_data: Dict,
    time_horizon_hours: int,
    db: AsyncSession
) -> Dict[str, Any]:
    """Backtest a single article's prediction"""
    try:
        article_time = article.published_at
        
        # Find the closest price data point before the article
        before_price = None
        after_price = None
        
        # Look for price data around article publication time
        for timestamp, row in price_data.iterrows():
            timestamp_aware = timestamp.tz_localize('UTC') if timestamp.tz is None else timestamp
            
            if timestamp_aware <= article_time:
                before_price = row['Close']
            elif timestamp_aware >= article_time + timedelta(hours=time_horizon_hours):
                after_price = row['Close']
                break
        
        if before_price is None or after_price is None:
            return None
        
        # Calculate actual price change
        actual_change = (after_price - before_price) / before_price
        actual_direction = "up" if actual_change > 0.001 else "down" if actual_change < -0.001 else "neutral"
        
        # Extract predicted direction from Claude analysis
        predicted_direction = "neutral"
        predicted_magnitude = 0.0
        
        if article.claude_analysis and 'affected_symbols' in article.claude_analysis:
            for sym_analysis in article.claude_analysis['affected_symbols']:
                if sym_analysis.get('symbol') == symbol:
                    predicted_direction = sym_analysis.get('impact_direction', 'neutral')
                    predicted_magnitude = sym_analysis.get('impact_magnitude', 0.0)
                    break
        
        # Calculate accuracy
        direction_correct = predicted_direction == actual_direction
        magnitude_error = abs(predicted_magnitude - abs(actual_change))
        
        accuracy_score = 0.0
        if direction_correct:
            accuracy_score += 0.6  # 60% for correct direction
            accuracy_score += max(0, 0.4 * (1 - magnitude_error * 10))  # 40% for magnitude accuracy
        
        # Save backtest result
        backtest_result = BacktestResult(
            article_id=article.id,
            symbol=symbol,
            predicted_direction=predicted_direction,
            actual_direction=actual_direction,
            predicted_magnitude=predicted_magnitude,
            actual_magnitude=abs(actual_change),
            accuracy_score=accuracy_score
        )
        
        db.add(backtest_result)
        
        return {
            "article_id": str(article.id),
            "article_title": article.title,
            "published_at": article.published_at,
            "predicted_direction": predicted_direction,
            "actual_direction": actual_direction,
            "predicted_magnitude": round(predicted_magnitude, 4),
            "actual_magnitude": round(abs(actual_change), 4),
            "actual_change_percent": round(actual_change * 100, 2),
            "accuracy_score": round(accuracy_score, 3),
            "impact_score": article.impact_score,
            "confidence_score": article.confidence_score
        }
        
    except Exception as e:
        print(f"Error backtesting article {article.id}: {e}")
        return None


def calculate_backtest_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate summary statistics for backtest results"""
    if not results:
        return {}
    
    total_predictions = len(results)
    correct_directions = sum(1 for r in results if r["predicted_direction"] == r["actual_direction"])
    
    avg_accuracy = sum(r["accuracy_score"] for r in results) / total_predictions
    avg_confidence = sum(r["confidence_score"] for r in results) / total_predictions if results else 0
    
    # Direction accuracy by prediction type
    up_predictions = [r for r in results if r["predicted_direction"] == "up"]
    down_predictions = [r for r in results if r["predicted_direction"] == "down"]
    neutral_predictions = [r for r in results if r["predicted_direction"] == "neutral"]
    
    up_accuracy = sum(1 for r in up_predictions if r["actual_direction"] == "up") / len(up_predictions) if up_predictions else 0
    down_accuracy = sum(1 for r in down_predictions if r["actual_direction"] == "down") / len(down_predictions) if down_predictions else 0
    neutral_accuracy = sum(1 for r in neutral_predictions if r["actual_direction"] == "neutral") / len(neutral_predictions) if neutral_predictions else 0
    
    return {
        "total_predictions": total_predictions,
        "overall_accuracy": round(correct_directions / total_predictions, 3),
        "avg_accuracy_score": round(avg_accuracy, 3),
        "avg_confidence": round(avg_confidence, 3),
        "direction_breakdown": {
            "up_predictions": len(up_predictions),
            "down_predictions": len(down_predictions),
            "neutral_predictions": len(neutral_predictions),
            "up_accuracy": round(up_accuracy, 3),
            "down_accuracy": round(down_accuracy, 3),
            "neutral_accuracy": round(neutral_accuracy, 3)
        }
    }


@router.get("/results/{symbol}")
async def get_backtest_results(
    symbol: str,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """Get historical backtest results for a symbol"""
    query = select(BacktestResult).where(
        BacktestResult.symbol == symbol
    ).order_by(BacktestResult.created_at.desc()).limit(limit)
    
    result = await db.execute(query)
    results = result.scalars().all()
    
    return [
        {
            "id": str(r.id),
            "article_id": str(r.article_id),
            "predicted_direction": r.predicted_direction,
            "actual_direction": r.actual_direction,
            "predicted_magnitude": r.predicted_magnitude,
            "actual_magnitude": r.actual_magnitude,
            "accuracy_score": r.accuracy_score,
            "created_at": r.created_at
        }
        for r in results
    ]