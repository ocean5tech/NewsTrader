import React, { useState } from 'react';
import { Table, Card, Button, Input, Select, Tag, Space, Modal, Typography, Spin } from 'antd';
import { useQuery } from 'react-query';
import { ReloadOutlined, EyeOutlined, SearchOutlined } from '@ant-design/icons';
import { newsApi } from '../services/api';
import { NewsArticle } from '../types';
import dayjs from 'dayjs';

const { Search } = Input;
const { Option } = Select;
const { Title, Paragraph, Text } = Typography;

const NewsPage: React.FC = () => {
  const [filters, setFilters] = useState({
    symbol: undefined as string | undefined,
    min_impact: undefined as number | undefined,
  });
  const [selectedArticle, setSelectedArticle] = useState<NewsArticle | null>(null);
  const [modalVisible, setModalVisible] = useState(false);

  const {
    data: articles,
    isLoading,
    refetch,
  } = useQuery(['news', filters], () =>
    newsApi.getArticles({
      limit: 100,
      ...filters,
    })
  );

  const {
    data: detailedArticle,
    isLoading: detailLoading,
  } = useQuery(
    ['article-detail', selectedArticle?.id],
    () => newsApi.getArticle(selectedArticle!.id),
    {
      enabled: !!selectedArticle?.id,
    }
  );

  const handleScrapeNews = async () => {
    try {
      await newsApi.scrapeNews();
      refetch();
    } catch (error) {
      console.error('Failed to scrape news:', error);
    }
  };

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'green';
    if (score < -0.1) return 'red';
    return 'blue';
  };

  const getSentimentText = (score: number) => {
    if (score > 0.1) return 'Positive';
    if (score < -0.1) return 'Negative';
    return 'Neutral';
  };

  const getImpactColor = (score: number) => {
    if (score > 7) return 'red';
    if (score > 4) return 'orange';
    return 'green';
  };

  const columns = [
    {
      title: 'Title',
      dataIndex: 'title',
      key: 'title',
      width: 300,
      render: (text: string, record: NewsArticle) => (
        <Button
          type="link"
          onClick={() => {
            setSelectedArticle(record);
            setModalVisible(true);
          }}
          style={{ textAlign: 'left', padding: 0, height: 'auto', whiteSpace: 'normal' }}
        >
          {text}
        </Button>
      ),
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      width: 120,
    },
    {
      title: 'Published',
      dataIndex: 'published_at',
      key: 'published_at',
      width: 120,
      render: (date: string) => dayjs(date).format('MM/DD HH:mm'),
    },
    {
      title: 'Impact',
      dataIndex: 'impact_score',
      key: 'impact_score',
      width: 80,
      render: (score: number) => (
        <Tag color={getImpactColor(score)}>
          {score.toFixed(1)}
        </Tag>
      ),
      sorter: (a: NewsArticle, b: NewsArticle) => a.impact_score - b.impact_score,
    },
    {
      title: 'Sentiment',
      dataIndex: 'sentiment_score',
      key: 'sentiment_score',
      width: 100,
      render: (score: number) => (
        <Tag color={getSentimentColor(score)}>
          {getSentimentText(score)}
        </Tag>
      ),
    },
    {
      title: 'Symbols',
      dataIndex: 'affected_symbols',
      key: 'affected_symbols',
      width: 150,
      render: (symbols: string[]) => (
        <Space wrap>
          {symbols?.slice(0, 3).map(symbol => (
            <Tag key={symbol} color="blue">
              {symbol}
            </Tag>
          ))}
          {symbols?.length > 3 && <Tag>+{symbols.length - 3}</Tag>}
        </Space>
      ),
    },
    {
      title: 'Confidence',
      dataIndex: 'confidence_score',
      key: 'confidence_score',
      width: 100,
      render: (score: number) => (
        <span style={{ color: score > 0.7 ? 'green' : score > 0.4 ? 'orange' : 'red' }}>
          {(score * 100).toFixed(0)}%
        </span>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 80,
      render: (_: any, record: NewsArticle) => (
        <Button
          type="text"
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedArticle(record);
            setModalVisible(true);
          }}
        />
      ),
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>News Articles</h1>
        <Space>
          <Button type="primary" icon={<ReloadOutlined />} onClick={handleScrapeNews}>
            Scrape News
          </Button>
          <Button icon={<ReloadOutlined />} onClick={() => refetch()}>
            Refresh
          </Button>
        </Space>
      </div>

      {/* Filters */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <Select
            placeholder="Filter by Symbol"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => setFilters({ ...filters, symbol: value })}
          >
            <Option value="SPY">SPY</Option>
            <Option value="QQQ">QQQ</Option>
            <Option value="GLD">GLD</Option>
            <Option value="CL=F">CL=F</Option>
            <Option value="GC=F">GC=F</Option>
            <Option value="ES=F">ES=F</Option>
          </Select>
          <Select
            placeholder="Min Impact Score"
            style={{ width: 150 }}
            allowClear
            onChange={(value) => setFilters({ ...filters, min_impact: value })}
          >
            <Option value={1}>1+</Option>
            <Option value={3}>3+</Option>
            <Option value={5}>5+</Option>
            <Option value={7}>7+</Option>
          </Select>
        </Space>
      </Card>

      {/* Articles Table */}
      <Card>
        <Table
          columns={columns}
          dataSource={articles}
          rowKey="id"
          loading={isLoading}
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
          scroll={{ x: 'max-content' }}
        />
      </Card>

      {/* Article Detail Modal */}
      <Modal
        title="Article Details"
        open={modalVisible}
        onCancel={() => setModalVisible(false)}
        footer={null}
        width={800}
      >
        {detailLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" />
          </div>
        ) : detailedArticle ? (
          <div>
            <Title level={3}>{detailedArticle.title}</Title>
            <Space direction="vertical" style={{ width: '100%', marginBottom: 16 }}>
              <Text type="secondary">
                {detailedArticle.source} • {dayjs(detailedArticle.published_at).format('MMMM D, YYYY HH:mm')}
              </Text>
              <Space wrap>
                <Tag color={getImpactColor(detailedArticle.impact_score)}>
                  Impact: {detailedArticle.impact_score.toFixed(1)}/10
                </Tag>
                <Tag color={getSentimentColor(detailedArticle.sentiment_score)}>
                  Sentiment: {getSentimentText(detailedArticle.sentiment_score)}
                </Tag>
                <Tag>
                  Confidence: {(detailedArticle.confidence_score * 100).toFixed(0)}%
                </Tag>
              </Space>
              <Space wrap>
                {detailedArticle.affected_symbols?.map(symbol => (
                  <Tag key={symbol} color="blue">{symbol}</Tag>
                ))}
              </Space>
            </Space>
            
            <Title level={4}>Summary</Title>
            <Paragraph>{detailedArticle.summary}</Paragraph>
            
            {detailedArticle.content && (
              <>
                <Title level={4}>Full Content</Title>
                <Paragraph style={{ maxHeight: 300, overflow: 'auto' }}>
                  {detailedArticle.content}
                </Paragraph>
              </>
            )}

            {detailedArticle.keywords && detailedArticle.keywords.length > 0 && (
              <>
                <Title level={4}>Keywords</Title>
                <Space wrap>
                  {detailedArticle.keywords.map((keyword, index) => (
                    <Tag key={index}>{keyword}</Tag>
                  ))}
                </Space>
              </>
            )}

            <div style={{ marginTop: 16 }}>
              <Button
                type="primary"
                href={detailedArticle.url}
                target="_blank"
                rel="noopener noreferrer"
              >
                Read Original Article
              </Button>
            </div>
          </div>
        ) : null}
      </Modal>
    </div>
  );
};

export default NewsPage;