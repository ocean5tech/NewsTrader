import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Button,
  Select,
  Tag,
  Divider,
  Typography,
  Space,
  Alert,
  Spin,
  Modal,
  message,
  Input,
  AutoComplete
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  StarOutlined,
  RiseOutlined,
  FallOutlined,
  SearchOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;
const { Option } = Select;

interface WatchlistItem {
  symbol: string;
  name?: string;
  category?: string;
}

interface NewsItem {
  id: string;
  title: string;
  title_zh: string;
  summary: string;
  summary_zh: string;
  impact_score: number;
  sentiment_score: number;
  relevance_score: number;
  watched_symbols: string[];
  published_at: string;
  source: string;
  url: string;
}

interface WatchlistData {
  symbols: string[];
  created_at: string | null;
  updated_at: string | null;
}

interface SearchResult {
  symbol: string;
  name: string;
  category: string;
  match_type: string;
}

const WatchlistPage: React.FC = () => {
  const [watchlist, setWatchlist] = useState<WatchlistData>({ symbols: [], created_at: null, updated_at: null });
  const [watchlistNews, setWatchlistNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [newsLoading, setNewsLoading] = useState(false);
  const [selectedSymbol, setSelectedSymbol] = useState<string>('');
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchValue, setSearchValue] = useState('');
  const [symbolInfo, setSymbolInfo] = useState<{[key: string]: {name: string, category: string}}>({});

  // 支持的交易品种
  const supportedSymbols = {
    'US Markets': ['SPY', 'QQQ', 'GLD', 'CL=F', 'GC=F', 'ES=F'],
    'Chinese Markets': ['000001.SS', '399001.SZ', 'HSI', 'BABA', 'JD', 'TCEHY'],
    'Commodities': ['XAUUSD', 'XAGUSD', 'USOIL', 'BRENT'],
    'Currencies': ['USDCNY', 'EURUSD', 'GBPUSD']
  };

  const symbolNames = {
    'SPY': 'SPDR S&P 500 ETF',
    'QQQ': 'Invesco QQQ ETF',
    'GLD': 'SPDR Gold Shares',
    'CL=F': 'Crude Oil Futures',
    'GC=F': 'Gold Futures',
    'ES=F': 'E-mini S&P 500',
    '000001.SS': '上证指数',
    '399001.SZ': '深证成指',
    'HSI': '恒生指数',
    'BABA': '阿里巴巴',
    'JD': '京东',
    'TCEHY': '腾讯控股',
    'XAUUSD': 'Gold/USD',
    'XAGUSD': 'Silver/USD',
    'USOIL': 'US Oil',
    'BRENT': 'Brent Oil',
    'USDCNY': '美元/人民币',
    'EURUSD': '欧元/美元',
    'GBPUSD': '英镑/美元'
  };

  const fetchSymbolInfo = async (symbols: string[]) => {
    const newSymbolInfo: {[key: string]: {name: string, category: string}} = {};
    
    for (const symbol of symbols) {
      if (!symbolInfo[symbol]) {
        try {
          const response = await axios.get(`http://localhost:8000/api/v1/symbols/search?q=${symbol}`);
          const results = response.data.results || [];
          const exactMatch = results.find((r: SearchResult) => r.symbol === symbol);
          if (exactMatch) {
            newSymbolInfo[symbol] = {
              name: exactMatch.name,
              category: exactMatch.category
            };
          }
        } catch (error) {
          console.error(`获取品种信息失败: ${symbol}`, error);
        }
      }
    }
    
    if (Object.keys(newSymbolInfo).length > 0) {
      setSymbolInfo(prev => ({ ...prev, ...newSymbolInfo }));
    }
  };

  const fetchWatchlist = async () => {
    try {
      setLoading(true);
      const response = await axios.get('http://localhost:8000/api/v1/watchlist');
      setWatchlist(response.data);
      
      // 获取品种信息
      if (response.data.symbols && response.data.symbols.length > 0) {
        await fetchSymbolInfo(response.data.symbols);
      }
    } catch (error) {
      message.error('加载关注名单失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchWatchlistNews = async () => {
    if (watchlist.symbols.length === 0) return;
    
    try {
      setNewsLoading(true);
      const response = await axios.get('http://localhost:8000/api/v1/watchlist/news');
      setWatchlistNews(response.data.news || []);
    } catch (error) {
      message.error('加载关注新闻失败');
    } finally {
      setNewsLoading(false);
    }
  };

  const addToWatchlist = async () => {
    if (!selectedSymbol) return;

    try {
      const response = await axios.post('http://localhost:8000/api/v1/watchlist/add', {
        symbol: selectedSymbol
      });
      
      if (response.data.success) {
        setWatchlist(response.data.watchlist);
        // 获取新添加品种的信息
        await fetchSymbolInfo([selectedSymbol]);
        setSelectedSymbol('');
        setSearchValue('');
        message.success(`已添加 ${selectedSymbol} 到关注名单`);
        fetchWatchlistNews(); // 刷新新闻
      } else {
        message.error(response.data.error || '添加失败');
      }
    } catch (error) {
      message.error('添加到关注名单失败');
    }
  };

  const removeFromWatchlist = async (symbol: string) => {
    Modal.confirm({
      title: '确认移除',
      content: `确定要从关注名单中移除 ${symbol} 吗？`,
      onOk: async () => {
        try {
          const response = await axios.post('http://localhost:8000/api/v1/watchlist/remove', {
            symbol: symbol
          });
          
          if (response.data.success) {
            setWatchlist(response.data.watchlist);
            message.success(`已从关注名单移除 ${symbol}`);
            fetchWatchlistNews(); // 刷新新闻
          }
        } catch (error) {
          message.error('移除失败');
        }
      }
    });
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'success';
    if (score < -0.1) return 'error';
    return 'default';
  };

  const getSentimentIcon = (score: number) => {
    if (score > 0.1) return <RiseOutlined />;
    if (score < -0.1) return <FallOutlined />;
    return null;
  };

  const searchSymbols = async (query: string) => {
    if (!query || query.length < 1) {
      setSearchResults([]);
      return;
    }
    
    try {
      const response = await axios.get(`http://localhost:8000/api/v1/symbols/search?q=${encodeURIComponent(query)}`);
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('搜索品种失败:', error);
      setSearchResults([]);
    }
  };

  const handleSearch = (value: string) => {
    setSearchValue(value);
    // 清除之前选中的symbol，只有通过选择才设置
    if (value !== searchValue) {
      setSelectedSymbol('');
    }
    searchSymbols(value);
  };

  const handleSelect = (value: string) => {
    const selectedResult = searchResults.find(r => r.symbol === value);
    if (selectedResult) {
      setSelectedSymbol(value);
      setSearchValue(`${selectedResult.symbol} - ${selectedResult.name}`);
      setSearchResults([]);
    }
  };

  const handleClear = () => {
    setSearchValue('');
    setSelectedSymbol('');
    setSearchResults([]);
  };

  useEffect(() => {
    fetchWatchlist();
  }, []);

  useEffect(() => {
    fetchWatchlistNews();
  }, [watchlist.symbols]);

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <StarOutlined /> 关注名单
      </Title>

      {/* 添加品种 */}
      <Card title="添加关注品种" style={{ marginBottom: 24 }}>
        <Space.Compact style={{ width: '100%', maxWidth: 600 }}>
          <AutoComplete
            style={{ flex: 1 }}
            value={searchValue}
            onSearch={handleSearch}
            onSelect={handleSelect}
            onClear={handleClear}
            placeholder="搜索交易品种 (如: 苹果, AAPL, 黄金, SPY)"
            allowClear
            options={searchResults.map(result => ({
              value: result.symbol,
              label: (
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <Text strong>{result.symbol}</Text>
                    <Text style={{ marginLeft: 8, color: '#666' }}>{result.name}</Text>
                  </div>
                  <Tag color="blue">{result.category}</Tag>
                </div>
              )
            }))}
          >
            <Input prefix={<SearchOutlined />} />
          </AutoComplete>
          <Button 
            type="primary" 
            icon={<PlusOutlined />}
            onClick={addToWatchlist}
            disabled={!selectedSymbol || watchlist.symbols.includes(selectedSymbol)}
          >
            添加
          </Button>
        </Space.Compact>
      </Card>

      {/* 关注名单 */}
      <Card 
        title={`我的关注名单 (${watchlist.symbols.length})`}
        style={{ marginBottom: 24 }}
        loading={loading}
      >
        {watchlist.symbols.length === 0 ? (
          <Alert
            message="暂无关注品种"
            description="请添加您想要关注的交易品种，系统将为您筛选相关新闻。"
            type="info"
            showIcon
          />
        ) : (
          <div>
            {watchlist.symbols.map(symbol => (
              <Tag
                key={symbol}
                closable
                onClose={() => removeFromWatchlist(symbol)}
                style={{ marginBottom: 8, fontSize: '14px', padding: '4px 8px' }}
              >
                <strong>{symbol}</strong> - {symbolInfo[symbol]?.name || symbolNames[symbol as keyof typeof symbolNames] || '未知品种'}
              </Tag>
            ))}
            {watchlist.updated_at && (
              <div style={{ marginTop: 16, color: '#666' }}>
                <Text type="secondary">
                  最后更新: {new Date(watchlist.updated_at).toLocaleString('zh-CN')}
                </Text>
              </div>
            )}
          </div>
        )}
      </Card>

      {/* 相关新闻 */}
      {watchlist.symbols.length > 0 && (
        <Card 
          title={`相关新闻 (按影响程度排序)`}
          extra={
            <Button onClick={fetchWatchlistNews} loading={newsLoading}>
              刷新新闻
            </Button>
          }
        >
          <Spin spinning={newsLoading}>
            {watchlistNews.length === 0 ? (
              <Alert
                message="暂无相关新闻"
                description="系统暂未找到与您关注品种相关的新闻。"
                type="info"
                showIcon
              />
            ) : (
              <List
                dataSource={watchlistNews}
                renderItem={(item: NewsItem) => (
                  <List.Item key={item.id}>
                    <Card 
                      size="small" 
                      style={{ width: '100%' }}
                      hoverable
                      onClick={() => window.open(item.url, '_blank')}
                    >
                      <div style={{ marginBottom: 8 }}>
                        <Space>
                          <Tag color="blue">{item.source}</Tag>
                          <Tag color="purple">影响: {item.relevance_score.toFixed(1)}</Tag>
                          <Tag color={getSentimentColor(item.sentiment_score)}>
                            {getSentimentIcon(item.sentiment_score)}
                            情感: {item.sentiment_score > 0 ? '+' : ''}{item.sentiment_score.toFixed(2)}
                          </Tag>
                          {item.watched_symbols.map(symbol => (
                            <Tag key={symbol} color="gold">{symbol}</Tag>
                          ))}
                        </Space>
                      </div>
                      
                      <Title level={5} style={{ margin: 0, marginBottom: 8 }}>
                        {item.title_zh || item.title}
                      </Title>
                      
                      <Text type="secondary">
                        {item.summary_zh || item.summary}
                      </Text>
                      
                      <div style={{ marginTop: 8, textAlign: 'right' }}>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {new Date(item.published_at).toLocaleString('zh-CN')}
                        </Text>
                      </div>
                    </Card>
                  </List.Item>
                )}
              />
            )}
          </Spin>
        </Card>
      )}
    </div>
  );
};

export default WatchlistPage;