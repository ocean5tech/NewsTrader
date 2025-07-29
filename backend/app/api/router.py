from fastapi import APIRouter
from app.api.endpoints import news, analysis, backtest

api_router = APIRouter()

api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(backtest.router, prefix="/backtest", tags=["backtest"])