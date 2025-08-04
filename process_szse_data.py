#!/usr/bin/env python3
"""
处理深圳交易所股票数据
支持多种文件格式：CSV、Excel、JSON、TXT
"""

import pandas as pd
import json
import csv
import psycopg2
from pypinyin import lazy_pinyin
import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5433,
    'user': 'postgres',
    'password': 'password',
    'database': 'newstrader'
}

def get_pinyin_short(chinese_text):
    """生成拼音简写"""
    if not chinese_text:
        return ""
    
    # 获取拼音首字母
    pinyin_list = lazy_pinyin(chinese_text, strict=False)
    short = ''.join([py[0].upper() for py in pinyin_list if py])
    return short[:20]  # 限制长度

def process_csv_file(file_path):
    """处理CSV文件"""
    print(f"📄 处理CSV文件: {file_path}")
    
    try:
        # 尝试不同的编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding)
                print(f"   ✅ 使用 {encoding} 编码成功读取")
                break
            except UnicodeDecodeError:
                continue
        
        if df is None:
            print("   ❌ 无法读取CSV文件，请检查编码")
            return []
        
        print(f"   📊 读取到 {len(df)} 行数据")
        print(f"   📋 列名: {list(df.columns)}")
        
        return process_dataframe(df)
        
    except Exception as e:
        print(f"   ❌ 处理CSV文件失败: {e}")
        return []

def process_excel_file(file_path):
    """处理Excel文件"""
    print(f"📄 处理Excel文件: {file_path}")
    
    try:
        # 尝试读取Excel文件的第一个工作表
        df = pd.read_excel(file_path, sheet_name=0)
        print(f"   📊 读取到 {len(df)} 行数据")
        print(f"   📋 列名: {list(df.columns)}")
        
        return process_dataframe(df)
        
    except Exception as e:
        print(f"   ❌ 处理Excel文件失败: {e}")
        return []

def process_json_file(file_path):
    """处理JSON文件"""
    print(f"📄 处理JSON文件: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            # 列表形式的JSON
            df = pd.DataFrame(data)
        elif isinstance(data, dict) and 'data' in data:
            # 包含data字段的JSON
            df = pd.DataFrame(data['data'])
        else:
            print("   ❌ 不支持的JSON格式")
            return []
        
        print(f"   📊 读取到 {len(df)} 行数据")
        print(f"   📋 列名: {list(df.columns)}")
        
        return process_dataframe(df)
        
    except Exception as e:
        print(f"   ❌ 处理JSON文件失败: {e}")
        return []

def process_dataframe(df):
    """处理DataFrame数据"""
    stocks = []
    
    # 常见的列名映射
    column_mapping = {
        # 股票代码
        'code': 'symbol',
        'stock_code': 'symbol',
        'symbol': 'symbol',
        '代码': 'symbol',
        '股票代码': 'symbol',
        '证券代码': 'symbol',
        
        # 股票名称
        'name': 'name',
        'stock_name': 'name',
        'security_name': 'name',
        '名称': 'name',
        '股票名称': 'name',
        '证券名称': 'name',
        '简称': 'name',
        
        # 上市状态
        'status': 'list_status',
        'list_status': 'list_status',
        '状态': 'list_status',
        '上市状态': 'list_status'
    }
    
    # 找到实际的列名
    actual_columns = {}
    for col in df.columns:
        col_lower = str(col).lower()
        for key, value in column_mapping.items():
            if key in col_lower or col == key:
                actual_columns[value] = col
                break
    
    print(f"   🔍 识别的列映射: {actual_columns}")
    
    if 'symbol' not in actual_columns or 'name' not in actual_columns:
        print("   ❌ 未找到股票代码或名称列，请检查数据格式")
        return []
    
    symbol_col = actual_columns['symbol']
    name_col = actual_columns['name']
    status_col = actual_columns.get('list_status', None)
    
    for index, row in df.iterrows():
        try:
            symbol = str(row[symbol_col]).strip()
            name = str(row[name_col]).strip()
            
            # 跳过无效数据
            if not symbol or not name or symbol.lower() in ['nan', 'none']:
                continue
            
            # 处理股票代码格式
            if len(symbol) == 6 and symbol.isdigit():
                # 标准6位数字代码
                pass
            elif '.' in symbol:
                # 可能包含交易所后缀
                symbol = symbol.split('.')[0]
            else:
                # 其他格式，尝试提取数字
                import re
                match = re.search(r'\d{6}', symbol)
                if match:
                    symbol = match.group()
                else:
                    continue
            
            # 生成拼音简写
            name_pinyin_short = get_pinyin_short(name)
            
            # 确定市场类别
            if symbol.startswith('000') or symbol.startswith('001'):
                market = '主板'
            elif symbol.startswith('002'):
                market = '中小板'  
            elif symbol.startswith('300'):
                market = '创业板'
            else:
                market = '其他'
            
            # 确定上市状态
            list_status = 'L'  # 默认为上市
            if status_col and status_col in row:
                status_value = str(row[status_col]).lower()
                if '暂停' in status_value or 'suspend' in status_value:
                    list_status = 'P'
                elif '终止' in status_value or 'delist' in status_value:
                    list_status = 'D'
            
            stock_data = {
                'symbol': symbol,
                'ts_code': f"{symbol}.SZ",
                'name': name,
                'name_pinyin_short': name_pinyin_short,
                'exchange': 'SZ',
                'market': market,
                'list_status': list_status
            }
            
            stocks.append(stock_data)
            
        except Exception as e:
            print(f"   ⚠️  处理第 {index} 行数据时出错: {e}")
            continue
    
    print(f"   ✅ 成功处理 {len(stocks)} 只深交所股票")
    return stocks

def update_database(stocks):
    """更新数据库中的股票数据"""
    if not stocks:
        print("❌ 没有股票数据需要更新")
        return {'added': 0, 'updated': 0, 'total': 0}
    
    print(f"💾 正在更新数据库，共 {len(stocks)} 只股票...")
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        added_count = 0
        updated_count = 0
        
        for stock in stocks:
            try:
                # 检查股票是否已存在
                cursor.execute("SELECT id FROM a_stocks WHERE symbol = %s", (stock['symbol'],))
                existing = cursor.fetchone()
                
                if existing:
                    # 更新现有记录
                    cursor.execute("""
                        UPDATE a_stocks SET 
                            name = %s,
                            name_pinyin_short = %s,
                            ts_code = %s,
                            exchange = %s,
                            market = %s,
                            list_status = %s
                        WHERE symbol = %s
                    """, (
                        stock['name'],
                        stock['name_pinyin_short'],
                        stock['ts_code'],
                        stock['exchange'],
                        stock['market'],
                        stock['list_status'],
                        stock['symbol']
                    ))
                    updated_count += 1
                else:
                    # 插入新记录
                    cursor.execute("""
                        INSERT INTO a_stocks (symbol, ts_code, name, name_pinyin_short, exchange, market, list_status)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (
                        stock['symbol'],
                        stock['ts_code'],
                        stock['name'],
                        stock['name_pinyin_short'],
                        stock['exchange'],
                        stock['market'],
                        stock['list_status']
                    ))
                    added_count += 1
                
                # 批量提交，每100条提交一次
                if (added_count + updated_count) % 100 == 0:
                    conn.commit()
                    print(f"📝 已处理 {added_count + updated_count} 只股票...")
                    
            except Exception as e:
                print(f"⚠️  处理股票 {stock['symbol']} 时出错: {e}")
                continue
        
        # 最终提交
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 数据库更新完成!")
        print(f"   - 新增股票: {added_count} 只")
        print(f"   - 更新股票: {updated_count} 只")
        print(f"   - 处理总数: {added_count + updated_count} 只")
        
        return {
            'added': added_count,
            'updated': updated_count,
            'total': added_count + updated_count
        }
        
    except Exception as e:
        print(f"❌ 数据库更新失败: {e}")
        return {'added': 0, 'updated': 0, 'total': 0, 'error': str(e)}

def main(file_path=None):
    """主函数"""
    print("🚀 开始处理深圳交易所股票数据...")
    
    if not file_path:
        print("请提供文件路径！")
        print("使用方法: python process_szse_data.py [文件路径]")
        return
    
    if not os.path.exists(file_path):
        print(f"❌ 文件不存在: {file_path}")
        return
    
    # 根据文件扩展名选择处理方式
    file_ext = os.path.splitext(file_path)[1].lower()
    
    stocks = []
    if file_ext in ['.csv', '.txt']:
        stocks = process_csv_file(file_path)
    elif file_ext in ['.xlsx', '.xls']:
        stocks = process_excel_file(file_path)
    elif file_ext == '.json':
        stocks = process_json_file(file_path)
    else:
        print(f"❌ 不支持的文件格式: {file_ext}")
        return
    
    if not stocks:
        print("❌ 未获取到股票数据")
        return
    
    # 更新数据库
    result = update_database(stocks)
    print("🎉 深交所股票数据处理完成!")
    
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        # 如果没有提供文件路径，查找项目目录中的相关文件
        project_dir = "/home/wyatt/dev-projects/NewsTrader"
        possible_files = [
            "szse_stocks.csv",
            "深交所股票.csv", 
            "szse_data.xlsx",
            "深交所数据.xlsx",
            "szse.json"
        ]
        
        found_file = None
        for filename in possible_files:
            full_path = os.path.join(project_dir, filename)
            if os.path.exists(full_path):
                found_file = full_path
                break
        
        if found_file:
            print(f"🔍 找到数据文件: {found_file}")
            main(found_file)
        else:
            print("📁 项目目录中未找到深交所数据文件")
            print("请将文件放到以下位置之一:")
            for filename in possible_files:
                print(f"   - {os.path.join(project_dir, filename)}")