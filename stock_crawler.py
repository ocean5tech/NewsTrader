#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股股票数据爬取脚本
支持从多个数据源获取股票代码、名称、上市日期等信息
"""

import requests
import json
import time
import csv
from datetime import datetime
from typing import List, Dict, Optional


class StockCrawler:
    """A股股票数据爬虫"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.sse.com.cn/'
        })
        
    def get_sse_stocks_paginated(self, total_pages: int = 68) -> List[Dict]:
        """分页获取上海证券交易所股票数据"""
        print(f"正在分页获取上交所股票数据（共{total_pages}页）...")
        
        all_stocks = []
        page_size = 25  # 每页25条数据
        
        # 分页获取数据
        for page in range(1, total_pages + 1):
            try:
                print(f"正在获取第{page}/{total_pages}页...")
                
                # 上交所分页接口
                url = 'https://query.sse.com.cn/commonQuery.do'
                params = {
                    'jsonCallBack': 'jsonpCallback',
                    'isPagination': 'true',
                    'stockCode': '',
                    'csrcCode': '',
                    'areaName': '',
                    'stockType': '1',
                    'pageHelp.pageCount': str(page_size),
                    'pageHelp.beginPage': str(page),
                    'pageHelp.cacheSize': '1',
                    'pageHelp.endPage': str(page)
                }
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    # 处理JSONP回调
                    text = response.text
                    if 'jsonpCallback(' in text:
                        text = text.replace('jsonpCallback(', '').rstrip(')')
                    
                    try:
                        data = json.loads(text)
                        if data.get('success') == 'true' or data.get('success') is True:
                            page_stocks = self._parse_sse_data(data)
                            all_stocks.extend(page_stocks)
                            print(f"第{page}页获取成功，获得{len(page_stocks)}条数据")
                            
                            # 如果当前页数据少于预期，可能已到最后一页
                            if len(page_stocks) < page_size:
                                print(f"第{page}页数据不足{page_size}条，可能已获取完所有数据")
                                break
                        else:
                            print(f"第{page}页请求失败: {data.get('error', 'Unknown error')}")
                    except json.JSONDecodeError as e:
                        print(f"第{page}页JSON解析失败: {e}")
                        
                else:
                    print(f"第{page}页HTTP请求失败: {response.status_code}")
                
                # 避免请求过快
                time.sleep(1)
                
            except Exception as e:
                print(f"第{page}页请求异常: {e}")
                continue
        
        print(f"上交所分页获取完成，共获得{len(all_stocks)}条数据")
        return all_stocks
    
    def get_sse_stocks(self) -> List[Dict]:
        """获取上海证券交易所股票数据"""
        print("正在获取上交所股票数据...")
        
        # 首先尝试分页获取完整数据
        try:
            stocks = self.get_sse_stocks_paginated(68)
            if stocks:
                return stocks
        except Exception as e:
            print(f"分页获取失败: {e}")
        
        # 尝试一次性获取所有数据
        urls = [
            'https://query.sse.com.cn/security/stock/getStockListData2.do?&jsonCallBack=jsonpCallback&stockCode=&csrcCode=&areaName=&stockType=1',
            'https://query.sse.com.cn/commonQuery.do?jsonCallBack=jsonpCallback&isPagination=false&stockCode=&csrcCode=&areaName=&stockType=1',
            'https://query.sse.com.cn/security/stock/downloadStockListFile.do?csrcCode=&stockCode=&areaName=&stockType=1'
        ]
        
        for url in urls:
            try:
                response = self.session.get(url, timeout=60)  # 增加超时时间
                if response.status_code == 200:
                    # 处理JSONP回调
                    text = response.text
                    if 'jsonpCallback(' in text:
                        text = text.replace('jsonpCallback(', '').rstrip(')')
                    
                    try:
                        data = json.loads(text)
                        if data.get('success') == 'true' or data.get('success') is True:
                            stocks = self._parse_sse_data(data)
                            if stocks:
                                return stocks
                    except json.JSONDecodeError:
                        continue
                        
            except Exception as e:
                print(f"请求失败: {e}")
                continue
                
        print("上交所接口暂时无法访问，使用备用数据源...")
        return self._get_backup_sse_data()
    
    def get_szse_stocks_paginated(self) -> List[Dict]:
        """分页获取深圳证券交易所股票数据"""
        print("正在分页获取深交所股票数据...")
        
        all_stocks = []
        page = 1
        page_size = 100  # 深交所每页更多数据
        
        while True:
            try:
                print(f"正在获取深交所第{page}页...")
                
                # 深交所分页接口
                url = 'http://www.szse.cn/api/report/ShowReport/data'
                params = {
                    'SHOWTYPE': 'JSON',
                    'CATALOGID': '1110',
                    'TABKEY': 'tab1',
                    'pageno': str(page),
                    'pagesize': str(page_size),
                    'random': str(time.time())
                }
                
                response = self.session.get(url, params=params, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    page_stocks = self._parse_szse_data(data)
                    
                    if not page_stocks:  # 没有更多数据
                        break
                        
                    all_stocks.extend(page_stocks)
                    print(f"深交所第{page}页获取成功，获得{len(page_stocks)}条数据")
                    
                    # 如果当前页数据少于页面大小，说明已是最后一页
                    if len(page_stocks) < page_size:
                        break
                        
                    page += 1
                    time.sleep(1)  # 避免请求过快
                else:
                    print(f"深交所第{page}页HTTP请求失败: {response.status_code}")
                    break
                    
            except Exception as e:
                print(f"深交所第{page}页请求异常: {e}")
                break
        
        print(f"深交所分页获取完成，共获得{len(all_stocks)}条数据")
        return all_stocks
    
    def get_szse_stocks(self) -> List[Dict]:
        """获取深圳证券交易所股票数据"""
        print("正在获取深交所股票数据...")
        
        # 首先尝试分页获取完整数据
        try:
            stocks = self.get_szse_stocks_paginated()
            if stocks:
                return stocks
        except Exception as e:
            print(f"深交所分页获取失败: {e}")
        
        # 尝试一次性获取所有数据
        url = 'http://www.szse.cn/api/report/ShowReport/data'
        params = {
            'SHOWTYPE': 'JSON',
            'CATALOGID': '1110',
            'TABKEY': 'tab1',
            'random': str(time.time())
        }
        
        try:
            response = self.session.get(url, params=params, timeout=60)
            if response.status_code == 200:
                data = response.json()
                stocks = self._parse_szse_data(data)
                if stocks:
                    return stocks
        except Exception as e:
            print(f"深交所数据获取失败: {e}")
            
        return self._get_backup_szse_data()
    
    def get_eastmoney_stocks(self) -> List[Dict]:
        """从东方财富获取股票数据"""
        print("正在从东方财富获取股票数据...")
        
        all_stocks = []
        
        try:
            # 东方财富A股列表接口
            url = 'http://push2.eastmoney.com/api/qt/clist/get'
            params = {
                'pn': '1',
                'pz': '5000',  # 获取更多数据
                'po': '1',
                'np': '1',
                'ut': 'bd1d9ddb04089700cf9c27f6f7426281',
                'fltt': '2',
                'invt': '2',
                'fid': 'f3',
                'fs': 'm:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23',  # A股市场
                'fields': 'f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152'
            }
            
            response = self.session.get(url, params=params, timeout=60)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('rc') == 0 and 'data' in data and 'diff' in data['data']:
                    stocks_data = data['data']['diff']
                    
                    for stock in stocks_data:
                        try:
                            code = stock.get('f12', '')  # 股票代码
                            name = stock.get('f14', '')  # 股票名称
                            
                            if code and name:
                                # 判断市场
                                if code.startswith('6'):
                                    market = 'SH'
                                    exchange = '上海证券交易所'
                                elif code.startswith(('0', '2', '3')):
                                    market = 'SZ'
                                    exchange = '深圳证券交易所'
                                else:
                                    continue
                                
                                stock_info = {
                                    'code': code,
                                    'name': name,
                                    'full_name': name,  # 东财接口可能没有全称
                                    'list_date': '',  # 需要其他接口补充
                                    'industry': '',   # 需要其他接口补充
                                    'area': '',       # 需要其他接口补充
                                    'market': market,
                                    'exchange': exchange
                                }
                                all_stocks.append(stock_info)
                                
                        except Exception as e:
                            continue
                    
                    print(f"东方财富获取成功，共{len(all_stocks)}条数据")
                    return all_stocks
                    
        except Exception as e:
            print(f"东方财富数据获取失败: {e}")
            
        return []
    
    def get_sina_stocks(self) -> List[Dict]:
        """从新浪财经获取股票数据"""
        print("正在从新浪财经获取股票数据...")
        
        all_stocks = []
        
        try:
            # 新浪A股列表
            markets = [
                ('sh', '上海证券交易所', 'SH'),
                ('sz', '深圳证券交易所', 'SZ')
            ]
            
            for market_code, exchange_name, market_flag in markets:
                url = f'http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/Market_Center.getHQNodeData?page=1&num=3000&sort=symbol&asc=1&node={market_code}_a_stock'
                
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    # 新浪返回的是JavaScript数组格式
                    text = response.text
                    if text.startswith('[') and text.endswith(']'):
                        try:
                            data = json.loads(text)
                            
                            for item in data:
                                if isinstance(item, dict):
                                    code = item.get('code', '').replace(market_code, '')
                                    name = item.get('name', '')
                                    
                                    if code and name:
                                        stock_info = {
                                            'code': code,
                                            'name': name,
                                            'full_name': name,
                                            'list_date': '',
                                            'industry': item.get('industry', ''),
                                            'area': item.get('area', ''),
                                            'market': market_flag,
                                            'exchange': exchange_name
                                        }
                                        all_stocks.append(stock_info)
                                        
                        except json.JSONDecodeError:
                            continue
                            
                time.sleep(1)  # 避免请求过快
                
            print(f"新浪财经获取成功，共{len(all_stocks)}条数据")
            return all_stocks
            
        except Exception as e:
            print(f"新浪财经数据获取失败: {e}")
            
        return []
    
    def get_163_stocks(self) -> List[Dict]:
        """从网易财经获取股票数据"""
        print("正在从网易财经获取股票数据...")
        
        all_stocks = []
        
        try:
            # 网易A股列表接口
            url = 'http://quotes.money.163.com/hs/service/diyrank.php'
            params = {
                'host': 'http://quotes.money.163.com/hs/service/diyrank.php',
                'page': '0',
                'query': 'STYPE:EQA',
                'fields': 'SYMBOL,NAME,PRICE,PERCENT,UPDOWN,FIVE_MINUTE,OPEN,YESTCLOSE,HIGH,LOW,VOLUME,TURNOVER,HS,LB,WB,ZF,PE,MCAP,TCAP,MFSUM,MFRATIO.MFRATIO2,MFRATIO.MFRATIO10,SNAME,CODE,ANNOUNMT,UVSNEWS',
                'sort': 'SYMBOL',
                'order': 'asc',
                'count': '5000',
                'type': 'query'
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                text = response.text
                # 网易返回的数据格式比较特殊，需要解析
                if 'rank_data' in text:
                    # 简单解析，实际可能需要更复杂的处理
                    lines = text.split('\n')
                    for line in lines:
                        if 'SH' in line or 'SZ' in line:
                            parts = line.split(',')
                            if len(parts) > 2:
                                try:
                                    symbol = parts[0].strip().replace('"', '')
                                    name = parts[1].strip().replace('"', '')
                                    
                                    if len(symbol) == 8:  # 格式如 "SH600000"
                                        market_code = symbol[:2]
                                        code = symbol[2:]
                                        
                                        if market_code == 'SH':
                                            market = 'SH'
                                            exchange = '上海证券交易所'
                                        elif market_code == 'SZ':
                                            market = 'SZ'
                                            exchange = '深圳证券交易所'
                                        else:
                                            continue
                                        
                                        stock_info = {
                                            'code': code,
                                            'name': name,
                                            'full_name': name,
                                            'list_date': '',
                                            'industry': '',
                                            'area': '',
                                            'market': market,
                                            'exchange': exchange
                                        }
                                        all_stocks.append(stock_info)
                                        
                                except:
                                    continue
                
            print(f"网易财经获取成功，共{len(all_stocks)}条数据")
            return all_stocks
            
        except Exception as e:
            print(f"网易财经数据获取失败: {e}")
            
        return []
    
    def get_tushare_stocks(self) -> List[Dict]:
        """从tushare等第三方源获取数据"""
        print("尝试从第三方数据源获取...")
        
        # 尝试多个第三方数据源
        sources = [
            ('东方财富', self.get_eastmoney_stocks),
            ('新浪财经', self.get_sina_stocks),
            ('网易财经', self.get_163_stocks)
        ]
        
        for source_name, get_func in sources:
            try:
                stocks = get_func()
                if stocks:
                    print(f"从{source_name}获取到{len(stocks)}条数据")
                    return stocks
            except Exception as e:
                print(f"从{source_name}获取数据失败: {e}")
                continue
        
        return []
    
    def _parse_sse_data(self, data: Dict) -> List[Dict]:
        """解析上交所数据"""
        stocks = []
        result = data.get('result', [])
        
        for item in result:
            stock = {
                'code': item.get('SECURITY_CODE_A', ''),  # 股票代码
                'name': item.get('SECURITY_ABBR_A', ''),  # 股票简称
                'full_name': item.get('COMPANY_ABBR', ''),  # 公司名称
                'list_date': item.get('LISTING_DATE', ''),  # 上市日期
                'industry': item.get('CSRC_CODE', ''),  # 行业代码
                'area': item.get('AREA_NAME', ''),  # 地区
                'market': 'SH',  # 市场标识：上海
                'exchange': '上海证券交易所'
            }
            
            if stock['code'] and stock['name']:
                stocks.append(stock)
                
        return stocks
    
    def _parse_szse_data(self, data: Dict) -> List[Dict]:
        """解析深交所数据"""
        stocks = []
        
        if 'data' in data:
            for item in data['data']:
                stock = {
                    'code': item.get('gsdm', ''),  # 公司代码
                    'name': item.get('gsqc', ''),  # 公司简称
                    'full_name': item.get('gsqc', ''),  # 公司全称
                    'list_date': item.get('ssrq', ''),  # 上市日期
                    'industry': item.get('sshymc', ''),  # 所属行业
                    'area': item.get('szssxq', ''),  # 所在省市
                    'market': 'SZ',  # 市场标识：深圳
                    'exchange': '深圳证券交易所'
                }
                
                if stock['code'] and stock['name']:
                    stocks.append(stock)
                    
        return stocks
    
    def _get_backup_sse_data(self) -> List[Dict]:
        """备用上交所数据（部分示例数据）"""
        print("使用备用上交所数据...")
        
        backup_data = [
            {'code': '600000', 'name': '浦发银行', 'full_name': '上海浦东发展银行股份有限公司', 
             'list_date': '1999-11-10', 'industry': '银行', 'area': '上海', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '600036', 'name': '招商银行', 'full_name': '招商银行股份有限公司', 
             'list_date': '2002-04-09', 'industry': '银行', 'area': '深圳', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '600519', 'name': '贵州茅台', 'full_name': '贵州茅台酒股份有限公司', 
             'list_date': '2001-08-27', 'industry': '白酒', 'area': '贵州', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '600887', 'name': '伊利股份', 'full_name': '内蒙古伊利实业集团股份有限公司', 
             'list_date': '1996-03-12', 'industry': '乳品', 'area': '内蒙古', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '601318', 'name': '中国平安', 'full_name': '中国平安保险(集团)股份有限公司', 
             'list_date': '2007-03-01', 'industry': '保险', 'area': '深圳', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '601857', 'name': '中国石油', 'full_name': '中国石油天然气股份有限公司', 
             'list_date': '2007-11-05', 'industry': '石油开采', 'area': '北京', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '601888', 'name': '中国中免', 'full_name': '中国中免股份有限公司', 
             'list_date': '2009-07-29', 'industry': '免税零售', 'area': '北京', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '600004', 'name': '白云机场', 'full_name': '广州白云国际机场股份有限公司', 
             'list_date': '2003-02-17', 'industry': '航空机场', 'area': '广东', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '601166', 'name': '兴业银行', 'full_name': '兴业银行股份有限公司', 
             'list_date': '2007-02-05', 'industry': '银行', 'area': '福建', 'market': 'SH', 'exchange': '上海证券交易所'},
            {'code': '600276', 'name': '恒瑞医药', 'full_name': '江苏恒瑞医药股份有限公司', 
             'list_date': '2000-10-18', 'industry': '医药制造', 'area': '江苏', 'market': 'SH', 'exchange': '上海证券交易所'},
        ]
        
        return backup_data
    
    def _get_backup_szse_data(self) -> List[Dict]:
        """备用深交所数据（部分示例数据）"""
        print("使用备用深交所数据...")
        
        backup_data = [
            {'code': '000001', 'name': '平安银行', 'full_name': '平安银行股份有限公司', 
             'list_date': '1991-04-03', 'industry': '银行', 'area': '深圳', 'market': 'SZ', 'exchange': '深圳证券交易所'},
            {'code': '000002', 'name': '万科A', 'full_name': '万科企业股份有限公司', 
             'list_date': '1991-01-29', 'industry': '房地产', 'area': '深圳', 'market': 'SZ', 'exchange': '深圳证券交易所'},
            {'code': '000858', 'name': '五粮液', 'full_name': '宜宾五粮液股份有限公司', 
             'list_date': '1998-04-27', 'industry': '白酒', 'area': '四川', 'market': 'SZ', 'exchange': '深圳证券交易所'},
            {'code': '002594', 'name': '比亚迪', 'full_name': '比亚迪股份有限公司', 
             'list_date': '2011-06-30', 'industry': '汽车制造', 'area': '深圳', 'market': 'SZ', 'exchange': '深圳证券交易所'},
            {'code': '300001', 'name': '特锐德', 'full_name': '青岛特锐德电气股份有限公司', 
             'list_date': '2009-10-30', 'industry': '电气设备', 'area': '山东', 'market': 'SZ', 'exchange': '深圳证券交易所'},
            {'code': '300015', 'name': '爱尔眼科', 'full_name': '爱尔眼科医院集团股份有限公司', 
             'list_date': '2009-10-30', 'industry': '医疗服务', 'area': '湖南', 'market': 'SZ', 'exchange': '深圳证券交易所'},
            {'code': '300059', 'name': '东方财富', 'full_name': '东方财富信息股份有限公司', 
             'list_date': '2010-03-19', 'industry': '金融服务', 'area': '上海', 'market': 'SZ', 'exchange': '深圳证券交易所'},
            {'code': '002415', 'name': '海康威视', 'full_name': '杭州海康威视数字技术股份有限公司', 
             'list_date': '2010-05-28', 'industry': '安防设备', 'area': '浙江', 'market': 'SZ', 'exchange': '深圳证券交易所'},
        ]
        
        return backup_data
    
    def crawl_all_stocks(self) -> List[Dict]:
        """爬取所有A股数据"""
        print("开始爬取A股数据...")
        print("目标：获取完整的1693条股票数据")
        
        all_stocks = []
        
        # 优先尝试第三方数据源获取完整数据
        print("\n=== 尝试第三方数据源 ===")
        try:
            third_party_stocks = self.get_tushare_stocks()
            if third_party_stocks and len(third_party_stocks) > 1000:  # 如果获取到大量数据
                all_stocks = third_party_stocks
                print(f"✅ 第三方数据源获取成功: {len(all_stocks)} 只股票")
            else:
                print("❌ 第三方数据源获取数据不足，尝试官方接口...")
        except Exception as e:
            print(f"❌ 第三方数据源失败: {e}")
        
        # 如果第三方数据源失败或数据不足，尝试官方接口
        if len(all_stocks) < 1000:
            print("\n=== 尝试官方接口 ===")
            
            # 获取上交所数据
            try:
                sse_stocks = self.get_sse_stocks()
                all_stocks.extend(sse_stocks)
                print(f"获取上交所股票 {len(sse_stocks)} 只")
            except Exception as e:
                print(f"上交所数据获取失败: {e}")
            
            time.sleep(2)  # 避免请求过快
            
            # 获取深交所数据
            try:
                szse_stocks = self.get_szse_stocks()
                all_stocks.extend(szse_stocks)
                print(f"获取深交所股票 {len(szse_stocks)} 只")
            except Exception as e:
                print(f"深交所数据获取失败: {e}")
        
        # 数据去重和清洗
        print(f"\n=== 数据清洗 ===")
        print(f"清洗前数据量: {len(all_stocks)} 只")
        all_stocks = self._clean_and_deduplicate(all_stocks)
        print(f"清洗后数据量: {len(all_stocks)} 只")
        
        # 结果分析
        if len(all_stocks) >= 1693:
            print(f"🎉 成功获取到目标数据量: {len(all_stocks)} 只股票 (≥1693)")
        elif len(all_stocks) >= 1000:
            print(f"✅ 获取到大部分数据: {len(all_stocks)} 只股票 (≥1000)")
        else:
            print(f"⚠️  获取数据量较少: {len(all_stocks)} 只股票 (<1000)")
        
        return all_stocks
    
    def _clean_and_deduplicate(self, stocks: List[Dict]) -> List[Dict]:
        """数据清洗和去重"""
        seen_codes = set()
        cleaned_stocks = []
        
        for stock in stocks:
            code = stock.get('code', '').strip()
            name = stock.get('name', '').strip()
            
            # 基本验证
            if not code or not name or code in seen_codes:
                continue
                
            # 代码格式检查（6位数字）
            if not (code.isdigit() and len(code) == 6):
                continue
                
            # 日期格式化
            list_date = stock.get('list_date', '')
            if list_date:
                try:
                    # 尝试解析不同日期格式
                    if '-' in list_date:
                        datetime.strptime(list_date, '%Y-%m-%d')
                    elif '/' in list_date:
                        list_date = datetime.strptime(list_date, '%Y/%m/%d').strftime('%Y-%m-%d')
                        stock['list_date'] = list_date
                except:
                    stock['list_date'] = ''
            
            seen_codes.add(code)
            cleaned_stocks.append(stock)
        
        return cleaned_stocks
    
    def save_to_csv(self, stocks: List[Dict], filename: str = 'a_stock_list.csv'):
        """保存数据到CSV文件"""
        if not stocks:
            print("没有数据可保存")
            return
            
        fieldnames = ['code', 'name', 'full_name', 'list_date', 'industry', 'area', 'market', 'exchange']
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(stocks)
            
        print(f"数据已保存到 {filename}")
    
    def save_to_json(self, stocks: List[Dict], filename: str = 'a_stock_list.json'):
        """保存数据到JSON文件"""
        if not stocks:
            print("没有数据可保存")
            return
            
        with open(filename, 'w', encoding='utf-8') as jsonfile:
            json.dump(stocks, jsonfile, ensure_ascii=False, indent=2)
            
        print(f"数据已保存到 {filename}")


def main():
    """主函数"""
    crawler = StockCrawler()
    
    print("=" * 50)
    print("A股股票数据爬取工具")
    print("=" * 50)
    
    # 爬取股票数据
    stocks = crawler.crawl_all_stocks()
    
    if stocks:
        print(f"\n成功获取 {len(stocks)} 只股票数据")
        
        # 显示前10条数据
        print("\n前10条数据预览:")
        print("-" * 80)
        print(f"{'代码':<10} {'名称':<15} {'上市日期':<12} {'所属市场':<10}")
        print("-" * 80)
        
        for i, stock in enumerate(stocks[:10]):
            print(f"{stock['code']:<10} {stock['name']:<15} {stock['list_date']:<12} {stock['exchange']:<10}")
        
        # 保存数据
        crawler.save_to_csv(stocks)
        crawler.save_to_json(stocks)
        
        # 统计信息
        sh_count = len([s for s in stocks if s['market'] == 'SH'])
        sz_count = len([s for s in stocks if s['market'] == 'SZ'])
        
        print(f"\n统计信息:")
        print(f"上交所股票: {sh_count} 只")
        print(f"深交所股票: {sz_count} 只")
        print(f"总计: {len(stocks)} 只")
        
    else:
        print("未能获取到股票数据，请检查网络连接或稍后重试")


if __name__ == "__main__":
    main()