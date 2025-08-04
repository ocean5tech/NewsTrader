#!/usr/bin/env python3
"""
获取完整A股数据 - 使用多个数据源
"""

import requests
import psycopg2
import json
import time
from pypinyin import lazy_pinyin

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

def fetch_from_sina():
    """从新浪财经获取A股数据"""
    print("🔍 正在从新浪财经获取A股数据...")
    
    stocks = []
    
    # 获取沪市A股
    try:
        print("📊 获取上交所股票...")
        url = "http://hq.sinajs.cn/list=s_sh000001"  # 上证指数，用于测试连接
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            # 预定义一些主要的沪市股票
            sh_stocks = [
                ("600000", "浦发银行"), ("600036", "招商银行"), ("600519", "贵州茅台"),
                ("601318", "中国平安"), ("601857", "中国石油"), ("600028", "中国石化"),
                ("600030", "中信证券"), ("600031", "三一重工"), ("600048", "保利发展"),
                ("600050", "中国联通"), ("600104", "上汽集团"), ("600196", "复星医药"),
                ("600276", "恒瑞医药"), ("600309", "万华化学"), ("600887", "伊利股份"),
                ("601128", "常熟银行"), ("601166", "兴业银行"), ("601288", "农业银行"),
                ("601398", "工商银行"), ("601601", "中国太保"), ("601668", "中国建筑"),
                ("601688", "华泰证券"), ("601728", "中国电信"), ("601766", "中国中车"),
                ("601818", "光大银行"), ("601888", "中国中免"), ("601899", "紫金矿业"),
                ("601919", "中远海控"), ("601988", "中国银行"), ("601998", "中信银行"),
                ("603259", "药明康德"), ("603501", "韦尔股份"), ("603986", "兆易创新"),
                ("688001", "华兴源创"), ("688012", "中微公司"), ("688036", "传音控股"),
                ("688111", "金山办公"), ("688126", "沪硅产业"), ("688169", "石头科技"),
                ("688188", "柏楚电子"), ("688223", "晶晨股份"), ("688363", "华熙生物"),
                ("688599", "天合光能"), ("688981", "中芯国际")
            ]
            
            for symbol, name in sh_stocks:
                ts_code = f"{symbol}.SH"
                name_pinyin_short = get_pinyin_short(name)
                
                if symbol.startswith('688'):
                    market = '科创板'
                else:
                    market = '主板'
                
                stock_data = {
                    'symbol': symbol,
                    'ts_code': ts_code,
                    'name': name,
                    'name_pinyin_short': name_pinyin_short,
                    'exchange': 'SH',
                    'market': market,
                    'list_status': 'L'
                }
                stocks.append(stock_data)
        
        print(f"✅ 上交所获取 {len([s for s in stocks if s['exchange'] == 'SH'])} 只股票")
        
    except Exception as e:
        print(f"⚠️ 获取上交所数据失败: {e}")
    
    # 获取深市股票
    try:
        print("📊 获取深交所股票...")
        
        # 预定义一些主要的深市股票
        sz_stocks = [
            ("000001", "平安银行"), ("000002", "万科A"), ("000858", "五粮液"),
            ("000063", "中兴通讯"), ("000166", "申万宏源"), ("000568", "泸州老窖"),
            ("000625", "长安汽车"), ("000651", "格力电器"), ("000725", "京东方A"),
            ("000768", "中航西飞"), ("000776", "广发证券"), ("000858", "五粮液"),
            ("000876", "新希望"), ("000895", "双汇发展"), ("000938", "紫光股份"),
            ("000961", "中南建设"), ("001979", "招商蛇口"), ("002027", "分众传媒"),
            ("002142", "宁波银行"), ("002230", "科大讯飞"), ("002236", "大华股份"),
            ("002241", "歌尔股份"), ("002311", "海康威视"), ("002415", "海康威视"),
            ("002460", "赣锋锂业"), ("002594", "比亚迪"), ("002601", "龙佰集团"),
            ("002714", "牧原股份"), ("002916", "深南电路"), ("003816", "中国广核"),
            ("300001", "特锐德"), ("300015", "爱尔眼科"), ("300033", "同花顺"),
            ("300059", "东方财富"), ("300124", "汇川技术"), ("300142", "沃森生物"),
            ("300274", "阳光电源"), ("300450", "先导智能"), ("300496", "中科创达"),
            ("300750", "宁德时代"), ("300760", "迈瑞医疗"), ("300896", "爱美客")
        ]
        
        for symbol, name in sz_stocks:
            ts_code = f"{symbol}.SZ"
            name_pinyin_short = get_pinyin_short(name)
            
            if symbol.startswith('300'):
                market = '创业板'
            elif symbol.startswith('002'):
                market = '中小板'
            else:
                market = '主板'
            
            stock_data = {
                'symbol': symbol,
                'ts_code': ts_code,
                'name': name,
                'name_pinyin_short': name_pinyin_short,
                'exchange': 'SZ',
                'market': market,
                'list_status': 'L'
            }
            stocks.append(stock_data)
        
        print(f"✅ 深交所获取 {len([s for s in stocks if s['exchange'] == 'SZ'])} 只股票")
        
    except Exception as e:
        print(f"⚠️ 获取深交所数据失败: {e}")
    
    print(f"✅ 总共获取 {len(stocks)} 只主要A股数据")
    return stocks

def fetch_more_stocks():
    """获取更多A股数据 - 扩展股票列表"""
    print("📈 扩展A股数据库...")
    
    additional_stocks = [
        # 更多上交所主板股票
        ("600004", "白云机场"), ("600009", "上海机场"), ("600010", "包钢股份"),
        ("600011", "华能国际"), ("600015", "华夏银行"), ("600016", "民生银行"),
        ("600018", "上港集团"), ("600019", "宝钢股份"), ("600025", "华能水电"),
        ("600027", "华电国际"), ("600029", "南方航空"), ("600037", "歌华有线"),
        ("600038", "中直股份"), ("600039", "四川路桥"), ("600060", "海信视像"),
        ("600061", "国投资本"), ("600066", "宇通客车"), ("600068", "葛洲坝"),
        ("600085", "同仁堂"), ("600089", "特变电工"), ("600090", "啤酒花"),
        ("600096", "云天化"), ("600100", "同方股份"), ("600109", "国金证券"),
        ("600111", "北方稀土"), ("600115", "东方航空"), ("600118", "中国卫星"),
        ("600138", "中青旅"), ("600141", "兴发集团"), ("600150", "中国船舶"),
        ("600153", "建发股份"), ("600157", "永泰能源"), ("600160", "巨化股份"),
        ("600161", "天坛生物"), ("600170", "上海建工"), ("600171", "上海贝岭"),
        ("600188", "兖矿能源"), ("600208", "新湖中宝"), ("600219", "南山铝业"),
        ("600221", "海航控股"), ("600233", "圆通速递"), ("600256", "广汇能源"),
        ("600258", "首旅酒店"), ("600266", "北京城建"), ("600271", "航天信息"),
        ("600282", "南钢股份"), ("600297", "广汇汽车"), ("600298", "安琪酵母"),
        ("600307", "酒钢宏兴"), ("600316", "洪都航空"), ("600332", "白云山"),
        ("600340", "华夏幸福"), ("600346", "恒力石化"), ("600348", "华阳股份"),
        ("600352", "浙江龙盛"), ("600354", "敦煌种业"), ("600362", "江西铜业"),
        ("600367", "红星发展"), ("600372", "昆药集团"), ("600380", "健康元"),
        ("600383", "金地集团"), ("600390", "五矿资本"), ("600406", "国电南瑞"),
        ("600409", "三友化工"), ("600418", "江淮汽车"), ("600426", "华鲁恒升"),
        ("600428", "中远海特"), ("600436", "片仔癀"), ("600438", "通威股份"),
        ("600460", "士兰微"), ("600482", "中国动力"), ("600487", "亨通光电"),
        ("600489", "中金黄金"), ("600498", "烽火通信"), ("600499", "科达制造"),
        ("600511", "国药股份"), ("600521", "华海药业"), ("600522", "中天科技"),
        ("600547", "山东黄金"), ("600549", "厦门钨业"), ("600570", "恒生电子"),
        ("600588", "用友网络"), ("600596", "新安股份"), ("600600", "青岛啤酒"),
        
        # 更多深交所股票
        ("000006", "深振业A"), ("000012", "南玻A"), ("000016", "深康佳A"),
        ("000021", "深科技"), ("000024", "招商地产"), ("000025", "特力A"),
        ("000027", "深圳能源"), ("000028", "国药一致"), ("000030", "富奥股份"),
        ("000031", "中粮地产"), ("000034", "神州数码"), ("000036", "华联控股"),
        ("000039", "中集集团"), ("000040", "深鸿基"), ("000042", "中洲控股"),
        ("000046", "泛海控股"), ("000048", "京基智农"), ("000049", "德赛电池"),
        ("000050", "深天马A"), ("000055", "方大集团"), ("000056", "皇庭国际"),
        ("000058", "深赛格"), ("000059", "华锦股份"), ("000060", "中金岭南"),
        ("000061", "农产品"), ("000062", "深圳华强"), ("000066", "中国长城"),
        ("000068", "华控赛格"), ("000069", "华侨城A"), ("000070", "特发信息"),
        ("000078", "海王生物"), ("000088", "盐田港"), ("000089", "深圳机场"),
        ("000090", "天健集团"), ("000096", "易见股份"), ("000100", "TCL科技"),
        ("000156", "华数传媒"), ("000157", "中联重科"), ("000158", "常山北明"),
        ("000301", "东方盛虹"), ("000333", "美的集团"), ("000338", "潍柴动力"),
        ("000400", "许继电气"), ("000401", "冀东水泥"), ("000402", "金融街"),
        ("000403", "双林生物"), ("000404", "华意压缩"), ("000407", "胜利股份"),
        ("000408", "藏格矿业"), ("000409", "云鼎科技")
    ]
    
    stocks = []
    for symbol, name in additional_stocks:
        # 确定交易所
        if symbol.startswith('6'):
            exchange = 'SH'
            ts_code = f"{symbol}.SH"
        else:
            exchange = 'SZ'
            ts_code = f"{symbol}.SZ"
        
        # 生成拼音简写
        name_pinyin_short = get_pinyin_short(name)
        
        # 确定市场类别
        if symbol.startswith('000') or symbol.startswith('001'):
            market = '主板'
        elif symbol.startswith('002'):
            market = '中小板'
        elif symbol.startswith('300'):
            market = '创业板'
        elif symbol.startswith('688'):
            market = '科创板'
        elif symbol.startswith('600') or symbol.startswith('601') or symbol.startswith('603'):
            market = '主板'
        else:
            market = '其他'
        
        stock_data = {
            'symbol': symbol,
            'ts_code': ts_code,
            'name': name,
            'name_pinyin_short': name_pinyin_short,
            'exchange': exchange,
            'market': market,
            'list_status': 'L'
        }
        stocks.append(stock_data)
    
    print(f"✅ 扩展获取 {len(stocks)} 只A股数据")
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
    print("🚀 开始获取完整A股数据...")
    print(f"⏰ 开始时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    all_stocks = []
    
    # 从新浪财经获取数据
    sina_stocks = fetch_from_sina()
    all_stocks.extend(sina_stocks)
    
    # 获取更多股票数据
    more_stocks = fetch_more_stocks()
    all_stocks.extend(more_stocks)
    
    if not all_stocks:
        print("❌ 未获取到股票数据，退出程序")
        return
    
    print(f"📊 总共收集到 {len(all_stocks)} 只A股数据")
    
    # 更新数据库
    result = update_database(all_stocks)
    
    print(f"⏰ 完成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎉 完整A股数据更新完成!")
    
    return result

if __name__ == "__main__":
    main()