-- A股股票信息表
CREATE TABLE IF NOT EXISTS a_stocks (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) UNIQUE NOT NULL,
    ts_code VARCHAR(12) UNIQUE NOT NULL,
    name VARCHAR(20) NOT NULL,
    area VARCHAR(10),
    industry VARCHAR(20),
    market VARCHAR(10),
    exchange VARCHAR(10) NOT NULL,
    name_pinyin VARCHAR(100),
    name_pinyin_short VARCHAR(20),
    list_status VARCHAR(1) DEFAULT 'L',
    list_date VARCHAR(8),
    delist_date VARCHAR(8),
    is_hs VARCHAR(1),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_a_stocks_symbol ON a_stocks(symbol);
CREATE INDEX IF NOT EXISTS idx_a_stocks_ts_code ON a_stocks(ts_code);
CREATE INDEX IF NOT EXISTS idx_a_stocks_name_pinyin_short ON a_stocks(name_pinyin_short);
CREATE INDEX IF NOT EXISTS idx_a_stocks_symbol_exchange ON a_stocks(symbol, exchange);
CREATE INDEX IF NOT EXISTS idx_a_stocks_list_status ON a_stocks(list_status);
CREATE INDEX IF NOT EXISTS idx_a_stocks_market_exchange ON a_stocks(market, exchange);

-- 股票关注列表表
CREATE TABLE IF NOT EXISTS stock_watchlist (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    ts_code VARCHAR(12) NOT NULL,
    name VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    alert_enabled BOOLEAN DEFAULT FALSE,
    notes VARCHAR(200),
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_watchlist_symbol ON stock_watchlist(symbol);
CREATE INDEX IF NOT EXISTS idx_watchlist_active ON stock_watchlist(is_active);

-- 添加注释
COMMENT ON TABLE a_stocks IS 'A股股票基础信息表';
COMMENT ON COLUMN a_stocks.symbol IS '股票代码 (如: 000001)';
COMMENT ON COLUMN a_stocks.ts_code IS 'TS代码 (如: 000001.SZ)';
COMMENT ON COLUMN a_stocks.name IS '股票名称';
COMMENT ON COLUMN a_stocks.name_pinyin IS '股票名称全拼音';
COMMENT ON COLUMN a_stocks.name_pinyin_short IS '股票名称拼音首字母';
COMMENT ON COLUMN a_stocks.list_status IS '上市状态 L上市 D退市 P暂停上市';
COMMENT ON COLUMN a_stocks.exchange IS '交易所 SZ/SH';
COMMENT ON COLUMN a_stocks.market IS '市场类型 (主板/中小板/创业板/科创板)';
COMMENT ON COLUMN a_stocks.is_hs IS '是否沪深港通标的 N否 H沪股通 S深股通';

COMMENT ON TABLE stock_watchlist IS '股票关注列表';
COMMENT ON COLUMN stock_watchlist.symbol IS '股票代码';
COMMENT ON COLUMN stock_watchlist.ts_code IS 'TS代码';
COMMENT ON COLUMN stock_watchlist.is_active IS '是否激活监控';
COMMENT ON COLUMN stock_watchlist.alert_enabled IS '是否启用提醒';