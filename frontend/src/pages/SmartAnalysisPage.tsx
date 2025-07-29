import React, { useState } from 'react';
import {
  Card,
  Row,
  Col,
  Button,
  Input,
  Select,
  Form,
  Alert,
  Spin,
  Tag,
  Typography,
  Divider,
  Table,
  Badge,
  Space,
  Tabs
} from 'antd';
import {
  SearchOutlined,
  FundOutlined,
  ReloadOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';

const { TextArea } = Input;
const { Option } = Select;
const { Title, Text, Paragraph } = Typography;
// const { TabPane } = Tabs; // Ant Design 5.x 不再需要TabPane

// 类型定义
interface SmartAnalysisResult {
  analysis_type: 'forward' | 'reverse';
  primary_symbols: Array<{ symbol: string; impact: number }>;
  secondary_symbols: Array<{ symbol: string; impact: number }>;
  sentiment_score: number;
  impact_score: number;
  confidence: number;
  keywords: string[];
  analysis_reason: string;
  analysis_timestamp: string;
}

interface ReverseSearchResult {
  symbol: string;
  related_news: Array<{
    id: string;
    title: string;
    content: string;
    impact_score: number;
    sentiment_score: number;
    published_at: string;
    source: string;
    confidence: number;
  }>;
  total_found: number;
  search_period_days: number;
  avg_impact: number;
  avg_sentiment: number;
}

const SmartAnalysisPage: React.FC = () => {
  const [analysisForm] = Form.useForm();
  const [searchForm] = Form.useForm();
  
  const [analysisResult, setAnalysisResult] = useState<SmartAnalysisResult | null>(null);
  const [searchResult, setSearchResult] = useState<ReverseSearchResult | null>(null);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [searchLoading, setSearchLoading] = useState(false);
  const [supportedSymbols, setSupportedSymbols] = useState<any>(null);

  // 加载支持的交易品种
  React.useEffect(() => {
    const loadSymbols = async () => {
      try {
        const response = await fetch('/api/v1/smart-analysis/supported-symbols');
        const data = await response.json();
        setSupportedSymbols(data);
      } catch (error) {
        console.error('Failed to load supported symbols:', error);
      }
    };
    loadSymbols();
  }, []);

  // 执行智能分析
  const handleAnalyzeNews = async (values: any) => {
    setAnalysisLoading(true);
    try {
      const response = await fetch('/api/v1/smart-analysis/analyze-news', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: values.title,
          content: values.content,
          target_symbol: values.target_symbol || null,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setAnalysisResult(result);
    } catch (error) {
      console.error('Analysis failed:', error);
    } finally {
      setAnalysisLoading(false);
    }
  };

  // 执行反向搜索
  const handleReverseSearch = async (values: any) => {
    setSearchLoading(true);
    try {
      const response = await fetch(`/api/v1/smart-analysis/reverse-search/${values.symbol}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const result = await response.json();
      setSearchResult(result);
    } catch (error) {
      console.error('Reverse search failed:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  // 影响评分颜色
  const getImpactColor = (score: number) => {
    if (score >= 7) return 'red';
    if (score >= 4) return 'orange';
    return 'green';
  };

  // 情感评分颜色
  const getSentimentColor = (score: number) => {
    if (score > 0.1) return 'green';
    if (score < -0.1) return 'red';
    return 'blue';
  };

  // 置信度颜色
  const getConfidenceColor = (score: number) => {
    if (score >= 0.8) return 'green';
    if (score >= 0.6) return 'orange';
    return 'red';
  };

  // 反向搜索结果表格列
  const reverseSearchColumns: ColumnsType<any> = [
    {
      title: '新闻标题',
      dataIndex: 'title',
      key: 'title',
      render: (title: string) => (
        <Text strong style={{ maxWidth: 300, display: 'block' }}>
          {title}
        </Text>
      ),
    },
    {
      title: '影响评分',
      dataIndex: 'impact_score',
      key: 'impact_score',
      width: 100,
      render: (score: number) => (
        <Tag color={getImpactColor(score)}>{score.toFixed(1)}</Tag>
      ),
      sorter: (a, b) => a.impact_score - b.impact_score,
    },
    {
      title: '情感倾向',
      dataIndex: 'sentiment_score',
      key: 'sentiment_score',
      width: 100,
      render: (score: number) => (
        <Tag color={getSentimentColor(score)}>
          {score > 0.1 ? '利好' : score < -0.1 ? '利空' : '中性'}
        </Tag>
      ),
    },
    {
      title: '置信度',
      dataIndex: 'confidence',
      key: 'confidence',
      width: 100,
      render: (score: number) => (
        <Tag color={getConfidenceColor(score)}>{(score * 100).toFixed(0)}%</Tag>
      ),
    },
    {
      title: '发布时间',
      dataIndex: 'published_at',
      key: 'published_at',
      width: 120,
      render: (date: string) => new Date(date).toLocaleDateString('zh-CN'),
    },
    {
      title: '来源',
      dataIndex: 'source',
      key: 'source',
      width: 100,
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <FundOutlined /> 智能新闻分析
      </Title>
      
      <Alert
        message="功能说明"
        description="支持两种分析模式：1) 正向分析 - 自动判断新闻对哪些交易品种影响最大；2) 反向分析 - 分析新闻对指定品种的具体影响程度。"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />

      <Tabs 
        defaultActiveKey="1" 
        size="large"
        items={[
          {
            key: '1',
            label: '智能新闻分析',
            children: (
              <Row gutter={[24, 24]}>
                <Col span={12}>
                  <Card title="新闻内容输入" extra={<InfoCircleOutlined />}>
                    <Form
                      form={analysisForm}
                      layout="vertical"
                      onFinish={handleAnalyzeNews}
                    >
                      <Form.Item
                        name="title"
                        label="新闻标题"
                        rules={[{ required: true, message: '请输入新闻标题' }]}
                      >
                        <Input placeholder="请输入新闻标题（支持中英文）" />
                      </Form.Item>
                      
                      <Form.Item
                        name="content"
                        label="新闻内容"
                        rules={[{ required: true, message: '请输入新闻内容' }]}
                      >
                        <TextArea
                          rows={6}
                          placeholder="请输入新闻正文内容（支持中英文）"
                        />
                      </Form.Item>
                      
                      <Form.Item
                        name="target_symbol"
                        label="目标品种（可选）"
                        help="留空进行正向分析，指定品种进行反向分析"
                      >
                        <Select
                          placeholder="选择目标交易品种（可选）"
                          allowClear
                          showSearch
                        >
                          {supportedSymbols?.trading_symbols?.map((symbol: string) => (
                            <Option key={symbol} value={symbol}>
                              {symbol}
                            </Option>
                          ))}
                        </Select>
                      </Form.Item>
                      
                      <Form.Item>
                        <Space>
                          <Button
                            type="primary"
                            htmlType="submit"
                            loading={analysisLoading}
                            icon={<FundOutlined />}
                          >
                            开始分析
                          </Button>
                          <Button onClick={() => analysisForm.resetFields()}>
                            清空内容
                          </Button>
                        </Space>
                      </Form.Item>
                    </Form>
                  </Card>
                </Col>
                
                <Col span={12}>
                  <Card title="分析结果" extra={analysisResult && (
                    <Tag color={analysisResult.analysis_type === 'forward' ? 'blue' : 'green'}>
                      {analysisResult.analysis_type === 'forward' ? '正向分析' : '反向分析'}
                    </Tag>
                  )}>
                    {analysisLoading && (
                      <div style={{ textAlign: 'center', padding: '40px' }}>
                        <Spin size="large" />
                        <div style={{ marginTop: 16 }}>
                          <Text>正在进行智能分析...</Text>
                        </div>
                      </div>
                    )}
                    
                    {analysisResult && !analysisLoading && (
                      <div>
                        {/* 主要影响品种 */}
                        <div style={{ marginBottom: 16 }}>
                          <Text strong>主要影响品种：</Text>
                          <div style={{ marginTop: 8 }}>
                            {analysisResult.primary_symbols.map((item, index) => (
                              <Tag
                                key={index}
                                color={getImpactColor(item.impact)}
                                style={{ marginBottom: 4 }}
                              >
                                {item.symbol}: {item.impact.toFixed(1)}
                              </Tag>
                            ))}
                          </div>
                        </div>

                        {/* 关键指标 */}
                        <Row gutter={16} style={{ marginBottom: 16 }}>
                          <Col span={8}>
                            <Card size="small">
                              <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                                  {analysisResult.impact_score.toFixed(1)}
                                </div>
                                <div>影响评分</div>
                              </div>
                            </Card>
                          </Col>
                          <Col span={8}>
                            <Card size="small">
                              <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                                  {analysisResult.sentiment_score > 0 ? '+' : ''}{analysisResult.sentiment_score.toFixed(2)}
                                </div>
                                <div>情感评分</div>
                              </div>
                            </Card>
                          </Col>
                          <Col span={8}>
                            <Card size="small">
                              <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '20px', fontWeight: 'bold' }}>
                                  {(analysisResult.confidence * 100).toFixed(0)}%
                                </div>
                                <div>置信度</div>
                              </div>
                            </Card>
                          </Col>
                        </Row>

                        {/* 关键词 */}
                        <div style={{ marginBottom: 16 }}>
                          <Text strong>关键词：</Text>
                          <div style={{ marginTop: 8 }}>
                            {analysisResult.keywords.map((keyword, index) => (
                              <Tag key={index} color="blue">
                                {keyword}
                              </Tag>
                            ))}
                          </div>
                        </div>

                        {/* 分析理由 */}
                        <div>
                          <Text strong>分析理由：</Text>
                          <Paragraph style={{ marginTop: 8, padding: 12, backgroundColor: '#f6f8fa', borderRadius: 4 }}>
                            {analysisResult.analysis_reason}
                          </Paragraph>
                        </div>
                      </div>
                    )}
                  </Card>
                </Col>
              </Row>
            )
          },
          {
            key: '2',
            label: '反向新闻搜索',
            children: (
              <Row gutter={[24, 24]}>
                <Col span={24}>
                  <Card title="根据交易品种查找相关新闻">
                    <Form
                      form={searchForm}
                      layout="inline"
                      onFinish={handleReverseSearch}
                      style={{ marginBottom: 24 }}
                    >
                      <Form.Item
                        name="symbol"
                        rules={[{ required: true, message: '请选择交易品种' }]}
                      >
                        <Select
                          placeholder="选择交易品种"
                          style={{ width: 200 }}
                          showSearch
                        >
                          {supportedSymbols?.trading_symbols?.map((symbol: string) => (
                            <Option key={symbol} value={symbol}>
                              {symbol}
                            </Option>
                          ))}
                        </Select>
                      </Form.Item>
                      
                      <Form.Item>
                        <Button
                          type="primary"
                          htmlType="submit"
                          loading={searchLoading}
                          icon={<SearchOutlined />}
                        >
                          搜索相关新闻
                        </Button>
                      </Form.Item>
                    </Form>

                    {searchResult && (
                      <div>
                        {/* 搜索统计 */}
                        <Row gutter={16} style={{ marginBottom: 24 }}>
                          <Col span={6}>
                            <Card size="small">
                              <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
                                  {searchResult.total_found}
                                </div>
                                <div>相关新闻数量</div>
                              </div>
                            </Card>
                          </Col>
                          <Col span={6}>
                            <Card size="small">
                              <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#52c41a' }}>
                                  {searchResult.avg_impact}
                                </div>
                                <div>平均影响评分</div>
                              </div>
                            </Card>
                          </Col>
                          <Col span={6}>
                            <Card size="small">
                              <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: searchResult.avg_sentiment > 0 ? '#52c41a' : '#ff4d4f' }}>
                                  {searchResult.avg_sentiment > 0 ? '+' : ''}{searchResult.avg_sentiment}
                                </div>
                                <div>平均情感倾向</div>
                              </div>
                            </Card>
                          </Col>
                          <Col span={6}>
                            <Card size="small">
                              <div style={{ textAlign: 'center' }}>
                                <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#faad14' }}>
                                  {searchResult.search_period_days}
                                </div>
                                <div>搜索天数</div>
                              </div>
                            </Card>
                          </Col>
                        </Row>

                        {/* 相关新闻表格 */}
                        <Table
                          columns={reverseSearchColumns}
                          dataSource={searchResult.related_news}
                          rowKey="id"
                          pagination={{ pageSize: 10 }}
                          scroll={{ x: 800 }}
                        />
                      </div>
                    )}
                  </Card>
                </Col>
              </Row>
            )
          }
        ]}
      />
    </div>
  );
};

export default SmartAnalysisPage;