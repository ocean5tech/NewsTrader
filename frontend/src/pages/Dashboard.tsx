import React from 'react';
import { Row, Col, Card, Statistic, Button, Space, Alert } from 'antd';
import { useQuery } from 'react-query';
import { ReloadOutlined, RiseOutlined, FallOutlined, FileTextOutlined, BarChartOutlined, TagOutlined } from '@ant-design/icons';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { newsApi, analysisApi } from '../services/api';
import { ImpactSummary } from '../types';

const Dashboard: React.FC = () => {
  const {
    data: trendingNews,
    isLoading: trendingLoading,
    refetch: refetchTrending,
  } = useQuery('trending-news', () => newsApi.getTrendingNews({ hours: 24, min_impact: 3 }));

  const {
    data: impactData,
    isLoading: impactLoading,
    refetch: refetchImpact,
  } = useQuery('impact-summary', () => analysisApi.getImpactSummary({ hours: 24 }));

  const {
    data: keywordData,
    isLoading: keywordLoading,
  } = useQuery('keyword-trends', () => analysisApi.getKeywordTrends({ days: 7, limit: 10 }));

  const handleRefresh = () => {
    refetchTrending();
    refetchImpact();
  };

  const prepareChartData = (summary: ImpactSummary[]) => {
    return summary.slice(0, 10).map(item => ({
      symbol: item.symbol,
      impact: item.avg_impact,
      sentiment: item.avg_sentiment,
      articles: item.article_count,
    }));
  };

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>NewsTrader Dashboard</h1>
        <Button 
          type="primary" 
          icon={<ReloadOutlined />} 
          onClick={handleRefresh}
          loading={trendingLoading || impactLoading}
        >
          Refresh Data
        </Button>
      </div>

      {/* Summary Cards */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Articles (24h)"
              value={impactData?.total_articles || 0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="High Impact News"
              value={trendingNews?.length || 0}
              prefix={<RiseOutlined />}
              valueStyle={{ color: '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Symbols Affected"
              value={impactData?.summary?.length || 0}
              prefix={<BarChartOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Keywords Tracked"
              value={keywordData?.trends?.length || 0}
              prefix={<TagOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        {/* Impact Chart */}
        <Col xs={24} lg={12}>
          <Card title="Symbol Impact Analysis" loading={impactLoading}>
            {impactData?.summary && (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={prepareChartData(impactData.summary)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="symbol" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="impact" fill="#8884d8" name="Average Impact" />
                </BarChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>

        {/* Sentiment Chart */}
        <Col xs={24} lg={12}>
          <Card title="Sentiment Trends" loading={impactLoading}>
            {impactData?.summary && (
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={prepareChartData(impactData.summary)}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="symbol" />
                  <YAxis domain={[-1, 1]} />
                  <Tooltip />
                  <Line type="monotone" dataKey="sentiment" stroke="#82ca9d" name="Sentiment" />
                </LineChart>
              </ResponsiveContainer>
            )}
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        {/* Trending News */}
        <Col xs={24} lg={12}>
          <Card title="High Impact News (Last 24h)" loading={trendingLoading}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {trendingNews?.slice(0, 5).map((article) => (
                <Alert
                  key={article.id}
                  message={article.title}
                  description={
                    <div>
                      <div>Impact: {article.impact_score.toFixed(1)}/10</div>
                      <div>Symbols: {article.affected_symbols.join(', ')}</div>
                      <div>Source: {article.source}</div>
                    </div>
                  }
                  type={article.sentiment_score > 0.1 ? 'success' : article.sentiment_score < -0.1 ? 'error' : 'info'}
                  showIcon
                  style={{ marginBottom: 8 }}
                />
              ))}
              {!trendingNews?.length && (
                <div style={{ textAlign: 'center', color: '#999' }}>
                  No high-impact news in the last 24 hours
                </div>
              )}
            </Space>
          </Card>
        </Col>

        {/* Top Keywords */}
        <Col xs={24} lg={12}>
          <Card title="Trending Keywords" loading={keywordLoading}>
            <Space direction="vertical" style={{ width: '100%' }}>
              {keywordData?.trends?.slice(0, 8).map((trend, index) => (
                <div
                  key={trend.keyword}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '8px 0',
                    borderBottom: index < 7 ? '1px solid #f0f0f0' : 'none',
                  }}
                >
                  <span style={{ fontWeight: 500 }}>{trend.keyword}</span>
                  <Space>
                    <span style={{ color: '#666' }}>
                      {trend.frequency} articles
                    </span>
                    <span style={{ color: trend.avg_impact > 5 ? '#cf1322' : '#1890ff' }}>
                      {trend.avg_impact.toFixed(1)} impact
                    </span>
                  </Space>
                </div>
              ))}
            </Space>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;