import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Tag,
  Typography,
  Space,
  Button,
  Alert,
  Spin,
  Row,
  Col,
  Statistic,
  Progress,
  Divider
} from 'antd';
import {
  BulbOutlined,
  RiseOutlined,
  FallOutlined,
  DollarOutlined,
  ClockCircleOutlined,
  FireOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Title, Text } = Typography;

interface TradingAdvice {
  id: string;
  symbol: string;
  direction: 'BUY' | 'SELL' | 'HOLD';
  entry_price: number;
  target_price: number;
  stop_loss: number;
  confidence: number;
  reasoning: string;
  news_sources: string[];
  time_horizon: string;
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH';
  created_at: string;
}

interface TradingAdviceResponse {
  advice: TradingAdvice[];
  market_sentiment: {
    overall: 'BULLISH' | 'BEARISH' | 'NEUTRAL';
    confidence: number;
  };
  generated_at: string;
}

const TradingAdvicePage: React.FC = () => {
  const [advice, setAdvice] = useState<TradingAdvice[]>([]);
  const [marketSentiment, setMarketSentiment] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<string | null>(null);

  const fetchTradingAdvice = async () => {
    setLoading(true);
    try {
      const response = await axios.get('/api/v1/trading-advice');
      const data: TradingAdviceResponse = response.data;
      setAdvice(data.advice);
      setMarketSentiment(data.market_sentiment);
      setLastUpdate(data.generated_at);
    } catch (error) {
      console.error('获取交易建议失败:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTradingAdvice();
  }, []);

  const getDirectionIcon = (direction: string) => {
    switch (direction) {
      case 'BUY':
        return <RiseOutlined style={{ color: '#52c41a' }} />;
      case 'SELL':
        return <FallOutlined style={{ color: '#ff4d4f' }} />;
      default:
        return <DollarOutlined style={{ color: '#faad14' }} />;
    }
  };

  const getDirectionColor = (direction: string) => {
    switch (direction) {
      case 'BUY':
        return 'success';
      case 'SELL':
        return 'error';
      default:
        return 'warning';
    }
  };

  const getRiskColor = (risk: string) => {
    switch (risk) {
      case 'LOW':
        return 'green';
      case 'MEDIUM':
        return 'orange';
      case 'HIGH':
        return 'red';
      default:
        return 'blue';
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'BULLISH':
        return '#52c41a';
      case 'BEARISH':
        return '#ff4d4f';
      default:
        return '#faad14';
    }
  };

  return (
    <div style={{ padding: '0 24px' }}>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Title level={2}>
          <BulbOutlined /> 交易建议
        </Title>
        <Button 
          type="primary" 
          icon={<ReloadOutlined />} 
          onClick={fetchTradingAdvice}
          loading={loading}
        >
          刷新建议
        </Button>
      </div>

      {/* 市场情绪概览 */}
      {marketSentiment && (
        <Card style={{ marginBottom: 24 }}>
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Statistic
                title="市场情绪"
                value={marketSentiment.overall}
                valueStyle={{ color: getSentimentColor(marketSentiment.overall) }}
                prefix={<FireOutlined />}
              />
            </Col>
            <Col span={8}>
              <div>
                <Text strong>情绪强度</Text>
                <Progress
                  percent={marketSentiment.confidence * 100}
                  strokeColor={getSentimentColor(marketSentiment.overall)}
                  size="small"
                  style={{ marginTop: 8 }}
                />
              </div>
            </Col>
            <Col span={8}>
              <Statistic
                title="活跃建议"
                value={advice.length}
                prefix={<BulbOutlined />}
              />
            </Col>
          </Row>
        </Card>
      )}

      {/* 交易建议列表 */}
      <Card
        title={
          <Space>
            <BulbOutlined />
            <span>AI交易建议</span>
            {lastUpdate && (
              <Text type="secondary" style={{ fontSize: '12px' }}>
                更新时间: {new Date(lastUpdate).toLocaleString('zh-CN')}
              </Text>
            )}
          </Space>
        }
        loading={loading}
      >
        {advice.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
            <BulbOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <div>暂无交易建议</div>
            <div style={{ fontSize: '12px', marginTop: '8px' }}>
              系统将基于最新新闻分析生成交易建议
            </div>
          </div>
        ) : (
          <List
            dataSource={advice}
            renderItem={(item: TradingAdvice) => (
              <List.Item
                style={{
                  border: '1px solid #f0f0f0',
                  borderRadius: '8px',
                  marginBottom: '16px',
                  padding: '16px',
                  backgroundColor: '#fafafa'
                }}
              >
                <div style={{ width: '100%' }}>
                  {/* 头部信息 */}
                  <div style={{ marginBottom: 16 }}>
                    <Row align="middle" justify="space-between">
                      <Col>
                        <Space size="large">
                          <Space>
                            <Text strong style={{ fontSize: '18px' }}>{item.symbol}</Text>
                            <Tag 
                              color={getDirectionColor(item.direction)} 
                              icon={getDirectionIcon(item.direction)}
                              style={{ fontSize: '14px', padding: '4px 8px' }}
                            >
                              {item.direction}
                            </Tag>
                          </Space>
                          <Tag color={getRiskColor(item.risk_level)}>
                            风险: {item.risk_level}
                          </Tag>
                          <Tag color="blue">
                            {item.time_horizon}
                          </Tag>
                        </Space>
                      </Col>
                      <Col>
                        <div style={{ textAlign: 'right' }}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            <ClockCircleOutlined /> {new Date(item.created_at).toLocaleString('zh-CN')}
                          </Text>
                          <div>
                            <Text strong>置信度: </Text>
                            <Progress
                              percent={item.confidence * 100}
                              size="small"
                              style={{ width: 100 }}
                              strokeColor="#1890ff"
                            />
                          </div>
                        </div>
                      </Col>
                    </Row>
                  </div>

                  {/* 价格信息 */}
                  <Row gutter={[16, 8]} style={{ marginBottom: 16 }}>
                    <Col span={8}>
                      <Statistic
                        title="入场价格"
                        value={item.entry_price}
                        precision={2}
                        prefix="$"
                        valueStyle={{ fontSize: '16px' }}
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="目标价格"
                        value={item.target_price}
                        precision={2}
                        prefix="$"
                        valueStyle={{ 
                          fontSize: '16px',
                          color: item.direction === 'BUY' ? '#52c41a' : '#ff4d4f'
                        }}
                      />
                    </Col>
                    <Col span={8}>
                      <Statistic
                        title="止损价格"
                        value={item.stop_loss}
                        precision={2}
                        prefix="$"
                        valueStyle={{ fontSize: '16px', color: '#ff4d4f' }}
                      />
                    </Col>
                  </Row>

                  <Divider style={{ margin: '12px 0' }} />

                  {/* 分析理由 */}
                  <div style={{ marginBottom: 12 }}>
                    <Text strong>分析理由:</Text>
                    <div style={{ marginTop: 8, padding: '8px 12px', backgroundColor: '#f6f8fa', borderRadius: '4px' }}>
                      <Text>{item.reasoning}</Text>
                    </div>
                  </div>

                  {/* 新闻来源 */}
                  {item.news_sources.length > 0 && (
                    <div>
                      <Text strong>相关新闻源:</Text>
                      <div style={{ marginTop: 8 }}>
                        <Space wrap>
                          {item.news_sources.map((source, index) => (
                            <Tag key={index} color="geekblue" style={{ fontSize: '11px' }}>
                              {source}
                            </Tag>
                          ))}
                        </Space>
                      </div>
                    </div>
                  )}
                </div>
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
};

export default TradingAdvicePage;