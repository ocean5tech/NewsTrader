import asyncio
import aiohttp
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pypinyin import lazy_pinyin, Style
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
import logging

from app.models.stock import AStock, StockWatchlist
from app.core.database import get_db

logger = logging.getLogger(__name__)


class StockService:
    """股票信息服务"""
    
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def generate_pinyin(self, chinese_text: str) -> tuple[str, str]:
        """生成拼音全拼和首字母"""
        try:
            # 获取全拼音
            full_pinyin = ''.join(lazy_pinyin(chinese_text, style=Style.NORMAL))
            
            # 获取首字母
            first_letters = ''.join(lazy_pinyin(chinese_text, style=Style.FIRST_LETTER))
            
            return full_pinyin.upper(), first_letters.upper()
        except Exception as e:
            logger.error(f"Error generating pinyin for '{chinese_text}': {e}")
            return "", ""
    
    async def fetch_stock_list_from_sina(self) -> List[Dict[str, Any]]:
        """从新浪财经获取A股列表"""
        try:
            # 获取沪市A股
            sh_url = "http://money.163.com/special/002526RN/hsrank.html"
            
            # 使用东方财富接口获取股票列表
            # 沪市主板
            sh_url = "http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery&pn=1&pz=5000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:2,m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
            
            # 深市主板
            sz_url = "http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery&pn=1&pz=5000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:6,m:0+t:80&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
            
            # 创业板
            cy_url = "http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery&pn=1&pz=5000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:0+t:80&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
            
            # 科创板
            kc_url = "http://push2.eastmoney.com/api/qt/clist/get?cb=jQuery&pn=1&pz=5000&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&fid=f3&fs=m:1+t:23&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152"
            
            all_stocks = []
            urls_info = [
                (sh_url, "SH", "主板"),
                (sz_url, "SZ", "主板"), 
                (cy_url, "SZ", "创业板"),
                (kc_url, "SH", "科创板")
            ]
            
            for url, exchange, market in urls_info:
                try:
                    async with self.session.get(url) as response:
                        if response.status == 200:
                            text = await response.text()
                            # 提取JSON数据
                            json_start = text.find('(') + 1
                            json_end = text.rfind(')')
                            if json_start > 0 and json_end > json_start:
                                json_data = json.loads(text[json_start:json_end])
                                
                                if 'data' in json_data and 'diff' in json_data['data']:
                                    for item in json_data['data']['diff']:
                                        if 'f12' in item and 'f14' in item:
                                            symbol = item['f12']  # 股票代码
                                            name = item['f14']    # 股票名称
                                            
                                            if symbol and name and len(symbol) == 6:
                                                # 生成拼音
                                                full_pinyin, short_pinyin = self.generate_pinyin(name)
                                                
                                                stock_info = {
                                                    'symbol': symbol,
                                                    'ts_code': f"{symbol}.{exchange}",
                                                    'name': name,
                                                    'exchange': exchange,
                                                    'market': market,
                                                    'name_pinyin': full_pinyin,
                                                    'name_pinyin_short': short_pinyin,
                                                    'list_status': 'L'
                                                }
                                                all_stocks.append(stock_info)
                        
                        await asyncio.sleep(0.5)  # 避免请求过快
                        
                except Exception as e:
                    logger.error(f"Error fetching from {url}: {e}")
                    continue
            
            logger.info(f"Fetched {len(all_stocks)} stocks from dongfang API")
            return all_stocks
            
        except Exception as e:
            logger.error(f"Error in fetch_stock_list_from_sina: {e}")
            return []
    
    async def fetch_stock_list_backup(self) -> List[Dict[str, Any]]:
        """备用方案：从腾讯财经获取股票列表"""
        try:
            # 腾讯财经股票列表接口
            url = "http://qt.gtimg.cn/q=s_sh000001,s_sz399001"
            
            # 这里简化处理，实际项目中可以实现更完整的备用数据源
            backup_stocks = [
                {
                    'symbol': '000001',
                    'ts_code': '000001.SZ',
                    'name': '平安银行',
                    'exchange': 'SZ',
                    'market': '主板',
                    'name_pinyin': 'PINGANYHANG',
                    'name_pinyin_short': 'PAYH',
                    'list_status': 'L'
                },
                {
                    'symbol': '000002',
                    'ts_code': '000002.SZ', 
                    'name': '万科A',
                    'exchange': 'SZ',
                    'market': '主板',
                    'name_pinyin': 'WANKEA',
                    'name_pinyin_short': 'WKA',
                    'list_status': 'L'
                }
            ]
            
            logger.info(f"Using backup stock list with {len(backup_stocks)} stocks")
            return backup_stocks
            
        except Exception as e:
            logger.error(f"Error in backup stock fetch: {e}")
            return []
    
    async def update_stock_database(self, db: Session) -> Dict[str, int]:
        """更新数据库中的股票信息"""
        try:
            # 获取股票列表
            stocks = await self.fetch_stock_list_from_sina()
            
            if not stocks:
                logger.warning("No stocks fetched from primary source, trying backup")
                stocks = await self.fetch_stock_list_backup()
            
            if not stocks:
                logger.error("Failed to fetch stocks from all sources")
                return {"updated": 0, "added": 0, "total": 0}
            
            updated_count = 0
            added_count = 0
            
            for stock_data in stocks:
                try:
                    # 检查是否已存在
                    existing = db.query(AStock).filter(
                        AStock.symbol == stock_data['symbol']
                    ).first()
                    
                    if existing:
                        # 更新现有记录
                        existing.name = stock_data['name']
                        existing.name_pinyin = stock_data['name_pinyin']
                        existing.name_pinyin_short = stock_data['name_pinyin_short']
                        existing.market = stock_data['market']
                        existing.updated_at = datetime.utcnow()
                        updated_count += 1
                    else:
                        # 添加新记录
                        new_stock = AStock(**stock_data)
                        db.add(new_stock)
                        added_count += 1
                        
                except Exception as e:
                    logger.error(f"Error processing stock {stock_data.get('symbol', 'unknown')}: {e}")
                    continue
            
            db.commit()
            total_count = updated_count + added_count
            
            logger.info(f"Stock database updated: {added_count} added, {updated_count} updated, {total_count} total")
            
            return {
                "added": added_count,
                "updated": updated_count, 
                "total": total_count
            }
            
        except Exception as e:
            logger.error(f"Error updating stock database: {e}")
            db.rollback()
            return {"updated": 0, "added": 0, "total": 0}
    
    def search_stocks(self, db: Session, query: str, limit: int = 20) -> List[AStock]:
        """搜索股票 - 支持代码和拼音搜索"""
        try:
            query = query.upper().strip()
            
            # 构建搜索条件
            conditions = []
            
            # 1. 股票代码搜索
            if query.isdigit():
                conditions.append(AStock.symbol.like(f"{query}%"))
            
            # 2. 拼音首字母搜索
            if query.isalpha():
                conditions.append(AStock.name_pinyin_short.like(f"{query}%"))
                conditions.append(AStock.name_pinyin.like(f"{query}%"))
            
            # 3. 股票名称搜索
            conditions.append(AStock.name.like(f"%{query}%"))
            
            # 只返回上市状态的股票
            results = db.query(AStock).filter(
                and_(
                    AStock.list_status == 'L',
                    or_(*conditions)
                )
            ).limit(limit).all()
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching stocks with query '{query}': {e}")
            return []
    
    def add_to_watchlist(self, db: Session, symbol: str, notes: str = "") -> Optional[StockWatchlist]:
        """添加股票到关注列表"""
        try:
            # 检查股票是否存在
            stock = db.query(AStock).filter(AStock.symbol == symbol).first()
            if not stock:
                logger.error(f"Stock {symbol} not found")
                return None
            
            # 检查是否已在关注列表中
            existing = db.query(StockWatchlist).filter(
                StockWatchlist.symbol == symbol
            ).first()
            
            if existing:
                existing.is_active = True
                existing.notes = notes
                existing.updated_at = datetime.utcnow()
                db.commit()
                return existing
            else:
                # 添加新的关注项
                watchlist_item = StockWatchlist(
                    symbol=stock.symbol,
                    ts_code=stock.ts_code,
                    name=stock.name,
                    notes=notes
                )
                db.add(watchlist_item)
                db.commit()
                return watchlist_item
                
        except Exception as e:
            logger.error(f"Error adding {symbol} to watchlist: {e}")
            db.rollback()
            return None


# 全局服务实例
stock_service = StockService()