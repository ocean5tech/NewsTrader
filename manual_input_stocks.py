#!/usr/bin/env python3
"""
手动输入股票数据处理脚本
用于处理粘贴的股票数据
"""

import psycopg2
from pypinyin import lazy_pinyin
import re

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

def parse_manual_data(data_text):
    """解析手动输入的数据"""
    stocks = []
    lines = data_text.strip().split('\n')
    
    print(f"📄 解析 {len(lines)} 行数据...")
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
            
        # 尝试不同的分隔符
        parts = None
        for separator in ['\t', ',', '|', ' ']:
            if separator in line:
                parts = [p.strip() for p in line.split(separator) if p.strip()]
                break
        
        if not parts:
            # 可能是固定宽度格式，尝试正则表达式
            match = re.match(r'(\d{6})\s+(.+)', line)
            if match:
                parts = [match.group(1), match.group(2)]
        
        if not parts or len(parts) < 2:
            print(f"   ⚠️  跳过第 {i+1} 行: {line}")
            continue
        
        try:
            symbol = parts[0].strip()
            name = parts[1].strip()
            
            # 验证股票代码格式
            if not (len(symbol) == 6 and symbol.isdigit()):
                print(f"   ⚠️  无效股票代码第 {i+1} 行: {symbol}")
                continue
            
            # 生成拼音简写
            name_pinyin_short = get_pinyin_short(name)
            
            # 确定市场类别 (深交所)
            if symbol.startswith('000') or symbol.startswith('001'):
                market = '主板'
            elif symbol.startswith('002'):
                market = '中小板'  
            elif symbol.startswith('300'):
                market = '创业板'
            else:
                market = '其他'
            
            stock_data = {
                'symbol': symbol,
                'ts_code': f"{symbol}.SZ",
                'name': name,
                'name_pinyin_short': name_pinyin_short,
                'exchange': 'SZ',
                'market': market,
                'list_status': 'L'
            }
            
            stocks.append(stock_data)
            
        except Exception as e:
            print(f"   ⚠️  处理第 {i+1} 行数据时出错: {e}")
            continue
    
    print(f"✅ 成功解析 {len(stocks)} 只深交所股票")
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

def main():
    """主函数"""
    print("🚀 手动输入深交所股票数据...")
    print("请粘贴您的股票数据，格式示例:")
    print("000001  平安银行")
    print("000002  万科A")
    print("...")
    print("输入完成后请输入 'END' 结束")
    print()
    
    lines = []
    while True:
        try:
            line = input(">>> ")
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        except KeyboardInterrupt:
            print("\n用户中断输入")
            break
    
    if not lines:
        print("❌ 没有输入任何数据")
        return
    
    data_text = '\n'.join(lines)
    stocks = parse_manual_data(data_text)
    
    if not stocks:
        print("❌ 未解析到有效股票数据")
        return
    
    # 更新数据库
    result = update_database(stocks)
    print("🎉 深交所股票数据处理完成!")
    
    return result

if __name__ == "__main__":
    main()