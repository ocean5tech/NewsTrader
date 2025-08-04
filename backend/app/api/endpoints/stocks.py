from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.services.stock_service import stock_service
from app.models.stock import AStock, StockWatchlist

router = APIRouter()


# Pydantic模型
class StockResponse(BaseModel):
    """股票信息响应模型"""
    symbol: str
    ts_code: str
    name: str
    exchange: str
    market: Optional[str] = None
    name_pinyin: Optional[str] = None
    name_pinyin_short: Optional[str] = None
    list_status: str = "L"
    
    class Config:
        from_attributes = True


class StockSearchResponse(BaseModel):
    """股票搜索响应模型"""
    total: int
    results: List[StockResponse]


class WatchlistItemResponse(BaseModel):
    """关注列表项响应模型"""
    id: int
    symbol: str
    ts_code: str
    name: str
    is_active: bool
    alert_enabled: bool
    notes: Optional[str] = None
    added_at: str
    
    class Config:
        from_attributes = True


class WatchlistRequest(BaseModel):
    """关注列表请求模型"""
    symbol: str
    notes: Optional[str] = ""


class StockUpdateResponse(BaseModel):
    """股票更新响应模型"""
    added: int
    updated: int
    total: int
    message: str


@router.get("/search", response_model=StockSearchResponse)
async def search_stocks(
    q: str = Query(..., description="搜索关键词，支持股票代码、拼音首字母或股票名称"),
    limit: int = Query(default=20, le=100, description="返回结果数量限制"),
    db: Session = Depends(get_db)
):
    """
    搜索股票
    
    支持的搜索方式：
    - 股票代码: 000001, 00000
    - 拼音首字母: PAYH (平安银行), WK (万科)
    - 股票名称: 平安, 万科
    """
    try:
        results = stock_service.search_stocks(db, q, limit)
        
        return StockSearchResponse(
            total=len(results),
            results=[StockResponse.from_orm(stock) for stock in results]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@router.get("/list", response_model=List[StockResponse])
async def get_stock_list(
    exchange: Optional[str] = Query(None, description="交易所代码 (SH/SZ)"),
    market: Optional[str] = Query(None, description="市场类型 (主板/创业板/科创板)"),
    limit: int = Query(default=100, le=1000, description="返回结果数量"),
    offset: int = Query(default=0, description="偏移量"),
    db: Session = Depends(get_db)
):
    """获取股票列表"""
    try:
        query = db.query(AStock).filter(AStock.list_status == 'L')
        
        if exchange:
            query = query.filter(AStock.exchange == exchange.upper())
        
        if market:
            query = query.filter(AStock.market == market)
        
        results = query.offset(offset).limit(limit).all()
        
        return [StockResponse.from_orm(stock) for stock in results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票列表失败: {str(e)}")


@router.get("/{symbol}", response_model=StockResponse)
async def get_stock_info(
    symbol: str,
    db: Session = Depends(get_db)
):
    """获取单个股票信息"""
    try:
        stock = db.query(AStock).filter(AStock.symbol == symbol).first()
        
        if not stock:
            raise HTTPException(status_code=404, detail=f"股票 {symbol} 不存在")
        
        return StockResponse.from_orm(stock)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取股票信息失败: {str(e)}")


@router.post("/update", response_model=StockUpdateResponse)
async def update_stock_data(
    db: Session = Depends(get_db)
):
    """更新股票数据（从数据源获取最新股票信息）"""
    try:
        async with stock_service as service:
            result = await service.update_stock_database(db)
        
        return StockUpdateResponse(
            added=result["added"],
            updated=result["updated"],
            total=result["total"],
            message=f"成功更新股票数据：新增 {result['added']} 只，更新 {result['updated']} 只"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新股票数据失败: {str(e)}")


# 关注列表相关接口
@router.get("/watchlist/", response_model=List[WatchlistItemResponse])
async def get_watchlist(
    active_only: bool = Query(default=True, description="仅返回激活的关注项"),
    db: Session = Depends(get_db)
):
    """获取股票关注列表"""
    try:
        query = db.query(StockWatchlist)
        
        if active_only:
            query = query.filter(StockWatchlist.is_active == True)
        
        results = query.order_by(StockWatchlist.added_at.desc()).all()
        
        return [
            WatchlistItemResponse(
                id=item.id,
                symbol=item.symbol,
                ts_code=item.ts_code,
                name=item.name,
                is_active=item.is_active,
                alert_enabled=item.alert_enabled,
                notes=item.notes,
                added_at=item.added_at.isoformat()
            ) for item in results
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关注列表失败: {str(e)}")


@router.post("/watchlist/", response_model=WatchlistItemResponse)
async def add_to_watchlist(
    request: WatchlistRequest,
    db: Session = Depends(get_db)
):
    """添加股票到关注列表"""
    try:
        result = stock_service.add_to_watchlist(db, request.symbol, request.notes)
        
        if not result:
            raise HTTPException(status_code=404, detail=f"股票 {request.symbol} 不存在")
        
        return WatchlistItemResponse(
            id=result.id,
            symbol=result.symbol,
            ts_code=result.ts_code,
            name=result.name,
            is_active=result.is_active,
            alert_enabled=result.alert_enabled,
            notes=result.notes,
            added_at=result.added_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"添加到关注列表失败: {str(e)}")


@router.delete("/watchlist/{item_id}")
async def remove_from_watchlist(
    item_id: int,
    db: Session = Depends(get_db)
):
    """从关注列表移除股票"""
    try:
        item = db.query(StockWatchlist).filter(StockWatchlist.id == item_id).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="关注项不存在")
        
        db.delete(item)
        db.commit()
        
        return {"message": f"已从关注列表移除 {item.name} ({item.symbol})"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"移除失败: {str(e)}")


@router.put("/watchlist/{item_id}")
async def update_watchlist_item(
    item_id: int,
    notes: Optional[str] = None,
    alert_enabled: Optional[bool] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """更新关注列表项"""
    try:
        item = db.query(StockWatchlist).filter(StockWatchlist.id == item_id).first()
        
        if not item:
            raise HTTPException(status_code=404, detail="关注项不存在")
        
        if notes is not None:
            item.notes = notes
        if alert_enabled is not None:
            item.alert_enabled = alert_enabled
        if is_active is not None:
            item.is_active = is_active
        
        item.updated_at = datetime.utcnow()
        db.commit()
        
        return {"message": f"已更新关注项 {item.name} ({item.symbol})"}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {str(e)}")