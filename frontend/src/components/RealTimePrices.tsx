import React, { useState, useEffect, useRef } from 'react';
import { Card, List, Tag, Typography, Space, Alert, Spin } from 'antd';
import {
  RiseOutlined,
  FallOutlined,
  MinusOutlined,
  WifiOutlined,
  DisconnectOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;

interface PriceData {
  [symbol: string]: number;
}

interface PriceUpdate {
  type: string;
  timestamp: string;
  prices: PriceData;
  prices_with_units?: {
    [symbol: string]: {
      price: number;
      unit: string;
    };
  };
}

interface PriceInfo {
  symbol: string;
  price: number;
  change: number;
  changePercent: number;
  trend: 'up' | 'down' | 'neutral';
  unit?: string;
}

const RealTimePrices: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [prices, setPrices] = useState<PriceData>({});
  const [priceChanges, setPriceChanges] = useState<{ [key: string]: number }>({});
  const [priceUnits, setPriceUnits] = useState<{ [key: string]: string }>({});
  const [lastUpdate, setLastUpdate] = useState<string>('');
  const wsRef = useRef<WebSocket | null>(null);
  const previousPricesRef = useRef<PriceData>({});
  const basePricesRef = useRef<PriceData>({}); // 存储基准价格

  const symbolNames = {
    'SPY': 'SPDR S&P 500 ETF',
    'QQQ': 'Invesco QQQ ETF',
    'GLD': 'SPDR Gold Shares',
    'USDCNY': '美元/人民币',
    'EURUSD': '欧元/美元',
    'GC=F': 'Gold Futures',
    'CL=F': 'Crude Oil Futures',
    '000001.SS': '上证指数',
    'BABA': '阿里巴巴',
    'JD': '京东'
  };

  useEffect(() => {
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        setConnected(true);
        console.log('WebSocket连接已建立');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data: PriceUpdate = JSON.parse(event.data);
          
          if (data.type === 'price_update') {
            // 初始化基准价格（第一次接收数据时）
            if (Object.keys(basePricesRef.current).length === 0) {
              basePricesRef.current = { ...data.prices };
            }
            
            // 处理新格式的价格数据（包含单位）
            if (data.prices_with_units) {
              const units: { [key: string]: string } = {};
              const pricesWithUnits = data.prices_with_units;
              Object.keys(pricesWithUnits).forEach(symbol => {
                units[symbol] = pricesWithUnits[symbol].unit || '';
              });
              setPriceUnits(units);
            }
            
            // 计算相对于基准价格的变化
            const changes: { [key: string]: number } = {};
            Object.keys(data.prices).forEach(symbol => {
              const currentPrice = data.prices[symbol];
              const basePrice = basePricesRef.current[symbol];
              
              if (basePrice !== undefined) {
                changes[symbol] = currentPrice - basePrice;
              } else {
                // 如果没有基准价格，设置当前价格为基准
                basePricesRef.current[symbol] = currentPrice;
                changes[symbol] = 0;
              }
            });

            setPrices(data.prices);
            setPriceChanges(changes);
            setLastUpdate(data.timestamp);
            previousPricesRef.current = { ...data.prices };
          }
        } catch (error) {
          console.error('解析WebSocket消息失败:', error);
        }
      };

      wsRef.current.onclose = () => {
        setConnected(false);
        console.log('WebSocket连接已断开');
        
        // 5秒后重连
        setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket错误:', error);
        setConnected(false);
      };
    } catch (error) {
      console.error('WebSocket连接失败:', error);
      setConnected(false);
    }
  };

  const getPriceInfo = (symbol: string): PriceInfo => {
    const price = prices[symbol] || 0;
    const change = priceChanges[symbol] || 0;
    const basePrice = basePricesRef.current[symbol] || price;
    const changePercent = basePrice > 0 ? (change / basePrice) * 100 : 0;
    const unit = priceUnits[symbol] || '';
    
    let trend: 'up' | 'down' | 'neutral' = 'neutral';
    if (change > 0.01) trend = 'up';
    else if (change < -0.01) trend = 'down';

    return {
      symbol,
      price,
      change,
      changePercent,
      trend,
      unit
    };
  };

  const getTrendIcon = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return <RiseOutlined style={{ color: '#52c41a' }} />;
      case 'down':
        return <FallOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <MinusOutlined style={{ color: '#d9d9d9' }} />;
    }
  };

  const getTrendColor = (trend: 'up' | 'down' | 'neutral') => {
    switch (trend) {
      case 'up':
        return '#52c41a';
      case 'down':
        return '#ff4d4f';
      default:
        return '#666';
    }
  };

  const priceInfoList = Object.keys(prices).map(symbol => getPriceInfo(symbol));

  return (
    <Card
      title={
        <Space>
          <Title level={4} style={{ margin: 0 }}>实时报价</Title>
          {connected ? (
            <Tag color="success" icon={<WifiOutlined />}>已连接</Tag>
          ) : (
            <Tag color="error" icon={<DisconnectOutlined />}>连接中...</Tag>
          )}
        </Space>
      }
      size="small"
      style={{ height: '100%' }}
    >
      {!connected ? (
        <div style={{ textAlign: 'center', padding: '20px' }}>
          <Spin size="large" />
          <div style={{ marginTop: 16 }}>
            <Text type="secondary">正在连接实时数据...</Text>
          </div>
        </div>
      ) : priceInfoList.length === 0 ? (
        <Alert
          message="等待数据"
          description="正在等待实时价格数据..."
          type="info"
          showIcon
        />
      ) : (
        <>
          <List
            dataSource={priceInfoList}
            renderItem={(item: PriceInfo) => (
              <List.Item style={{ padding: '8px 0' }}>
                <div style={{ width: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <Text strong>{item.symbol}</Text>
                      <br />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {symbolNames[item.symbol as keyof typeof symbolNames] || item.symbol}
                      </Text>
                    </div>
                    <div style={{ textAlign: 'right' }}>
                      <div style={{ fontSize: '16px', fontWeight: 'bold' }}>
                        {item.price.toFixed(2)}
                        {item.unit && <span style={{ fontSize: '12px', marginLeft: 4, color: '#666' }}>{item.unit}</span>}
                      </div>
                      <div 
                        style={{ 
                          fontSize: '12px', 
                          color: getTrendColor(item.trend),
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'flex-end'
                        }}
                      >
                        {getTrendIcon(item.trend)}
                        <span style={{ marginLeft: 4 }}>
                          {item.change > 0 ? '+' : ''}{item.change.toFixed(2)} 
                          ({item.changePercent > 0 ? '+' : ''}{item.changePercent.toFixed(2)}%)
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </List.Item>
            )}
          />
          {lastUpdate && (
            <div style={{ textAlign: 'center', marginTop: 16, borderTop: '1px solid #f0f0f0', paddingTop: 8 }}>
              <Text type="secondary" style={{ fontSize: '12px' }}>
                最后更新: {new Date(lastUpdate).toLocaleTimeString('zh-CN')}
              </Text>
              <br />
              <Text type="warning" style={{ fontSize: '11px', color: '#ff9500' }}>
                ⚠️ 模拟数据，仅供演示
              </Text>
            </div>
          )}
        </>
      )}
    </Card>
  );
};

export default RealTimePrices;