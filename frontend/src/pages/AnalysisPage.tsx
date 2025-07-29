import React, { useState } from 'react';
import { Row, Col, Card, Select, Button, Space, Table, Tag } from 'antd';
import { useQuery } from 'react-query';
import { ReloadOutlined } from '@ant-design/icons';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { analysisApi } from '../services/api';
import { MarketSentiment } from '../types';

const { Option } = Select;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

const AnalysisPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('SPY');
  const [timeFrame, setTimeFrame] = useState<number>(24);

  const {
    data: sentiment,
    isLoading: sentimentLoading,
    refetch: refetchSentiment,
  } = useQuery(
    ['market-sentiment', selectedSymbol, timeFrame],
    () => analysisApi.getMarketSentiment({ symbol: selectedSymbol, hours: timeFrame }),
    { enabled: !!selectedSymbol }
  );

  const {
    data: impactData,
    isLoading: impactLoading,
    refetch: refetchImpact,
  } = useQuery(
    ['impact-summary', timeFrame],
    () => analysisApi.getImpactSummary({ hours: timeFrame })
  );

  const {
    data: keywordData,
    isLoading: keywordLoading,
    refetch: refetchKeywords,
  } = useQuery('keyword-trends', () => analysisApi.getKeywordTrends({ days: 7, limit: 20 }));

  const handleRefresh = () => {
    refetchSentiment();
    refetchImpact();
    refetchKeywords();
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return '#52c41a';
    if (score < -0.1) return '#ff4d4f';
    return '#1890ff';
  };

  const getImpactLevel = (score: number) => {
    if (score > 7) return 'High';
    if (score > 4) return 'Medium';
    return 'Low';
  };

  const getImpactColor = (score: number) => {
    if (score > 7) return 'red';
    if (score > 4) return 'orange';
    return 'green';
  };

  const prepareImpactChartData = () => {
    if (!impactData?.summary) return [];
    return impactData.summary.slice(0, 10).map(item => ({
      symbol: item.symbol,
      impact: parseFloat(item.avg_impact.toFixed(2)),
      sentiment: parseFloat(item.avg_sentiment.toFixed(3)),
      articles: item.article_count,
    }));
  };

  const prepareKeywordPieData = () => {
    if (!keywordData?.trends) return [];
    return keywordData.trends.slice(0, 5).map(trend => ({
      name: trend.keyword,
      value: trend.frequency,
      impact: trend.avg_impact,
    }));
  };

  const impactColumns = [
    {
      title: 'Symbol',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => <Tag color="blue">{symbol}</Tag>,
    },
    {
      title: 'Articles',
      dataIndex: 'article_count',
      key: 'article_count',
      sorter: (a: any, b: any) => a.article_count - b.article_count,
    },
    {
      title: 'Avg Impact',
      dataIndex: 'avg_impact',
      key: 'avg_impact',
      render: (impact: number) => (
        <Tag color={getImpactColor(impact)}>
          {impact.toFixed(1)} ({getImpactLevel(impact)})
        </Tag>
      ),
      sorter: (a: any, b: any) => a.avg_impact - b.avg_impact,
    },
    {
      title: 'Sentiment',
      dataIndex: 'avg_sentiment',
      key: 'avg_sentiment',
      render: (sentiment: number) => (
        <span style={{ color: getSentimentColor(sentiment) }}>
          {sentiment > 0 ? '+' : ''}{sentiment.toFixed(3)}
        </span>
      ),
      sorter: (a: any, b: any) => a.avg_sentiment - b.avg_sentiment,
    },
    {
      title: 'Confidence',
      dataIndex: 'avg_confidence',
      key: 'avg_confidence',
      render: (confidence: number) => (
        <span style={{ color: confidence > 0.7 ? 'green' : confidence > 0.4 ? 'orange' : 'red' }}>
          {(confidence * 100).toFixed(0)}%
        </span>
      ),
      sorter: (a: any, b: any) => a.avg_confidence - b.avg_confidence,
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Market Analysis</h1>
        <Button 
          type="primary" 
          icon={<ReloadOutlined />} 
          onClick={handleRefresh}
          loading={sentimentLoading || impactLoading || keywordLoading}
        >
          Refresh Analysis
        </Button>
      </div>

      {/* Controls */}
      <Card style={{ marginBottom: 16 }}>
        <Space>
          <span>Symbol:</span>
          <Select
            value={selectedSymbol}
            style={{ width: 120 }}
            onChange={setSelectedSymbol}
          >
            <Option value="SPY">SPY</Option>
            <Option value="QQQ">QQQ</Option>
            <Option value="GLD">GLD</Option>
            <Option value="CL=F">CL=F</Option>
            <Option value="GC=F">GC=F</Option>
            <Option value="ES=F">ES=F</Option>
            <Option value="NQ=F">NQ=F</Option>
          </Select>
          <span>Time Frame:</span>
          <Select
            value={timeFrame}
            style={{ width: 120 }}
            onChange={setTimeFrame}
          >
            <Option value={6}>6 Hours</Option>
            <Option value={24}>24 Hours</Option>
            <Option value={72}>3 Days</Option>
            <Option value={168}>1 Week</Option>
          </Select>
        </Space>
      </Card>

      <Row gutter={[16, 16]}>
        {/* Sentiment Summary */}
        <Col xs={24} lg={8}>
          <Card title={`${selectedSymbol} Sentiment`} loading={sentimentLoading}>
            {sentiment && (
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 48, color: getSentimentColor(sentiment.sentiment_score), marginBottom: 16 }}>
                  {sentiment.sentiment_score > 0 ? '+' : ''}{sentiment.sentiment_score.toFixed(3)}
                </div>
                <div style={{ marginBottom: 8 }}>
                  <strong>Impact Score:</strong> {sentiment.impact_score.toFixed(1)}/10
                </div>
                <div style={{ marginBottom: 8 }}>
                  <strong>Articles:</strong> {sentiment.article_count}
                </div>
                <div>
                  <strong>Confidence:</strong> {(sentiment.confidence * 100).toFixed(0)}%
                </div>
              </div>
            )}
          </Card>
        </Col>

        {/* Impact Chart */}
        <Col xs={24} lg={16}>
          <Card title="Symbol Impact Comparison" loading={impactLoading}>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={prepareImpactChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="symbol" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="impact" fill="#8884d8" name="Average Impact" />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        {/* Impact Summary Table */}
        <Col xs={24} lg={16}>
          <Card title="Symbol Impact Summary" loading={impactLoading}>
            <Table
              columns={impactColumns}
              dataSource={impactData?.summary || []}
              rowKey="symbol"
              pagination={false}
              size="small"
              scroll={{ y: 400 }}
            />
          </Card>
        </Col>

        {/* Keyword Distribution */}
        <Col xs={24} lg={8}>
          <Card title="Top Keywords" loading={keywordLoading}>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={prepareKeywordPieData()}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }: any) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {prepareKeywordPieData().map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Keyword Trends Table */}
      <Row style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="Keyword Trends (Last 7 Days)" loading={keywordLoading}>
            <Table
              columns={[
                {
                  title: 'Keyword',
                  dataIndex: 'keyword',
                  key: 'keyword',
                  render: (keyword: string) => <Tag>{keyword}</Tag>,
                },
                {
                  title: 'Frequency',
                  dataIndex: 'frequency',
                  key: 'frequency',
                  sorter: (a: any, b: any) => a.frequency - b.frequency,
                },
                {
                  title: 'Avg Impact',
                  dataIndex: 'avg_impact',
                  key: 'avg_impact',
                  render: (impact: number) => (
                    <Tag color={getImpactColor(impact)}>
                      {impact.toFixed(1)}
                    </Tag>
                  ),
                  sorter: (a: any, b: any) => a.avg_impact - b.avg_impact,
                },
                {
                  title: 'Total Impact',
                  dataIndex: 'total_impact',
                  key: 'total_impact',
                  render: (impact: number) => impact.toFixed(1),
                  sorter: (a: any, b: any) => a.total_impact - b.total_impact,
                },
              ]}
              dataSource={keywordData?.trends || []}
              rowKey="keyword"
              pagination={{ pageSize: 10 }}
              size="small"
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default AnalysisPage;