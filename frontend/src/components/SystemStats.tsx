import React from 'react';
import { Card, Row, Col, Statistic, Tag, Space, Typography, Divider } from 'antd';
import { useQuery } from 'react-query';
import {
  CloudOutlined,
  ApiOutlined,
  DatabaseOutlined,
  ClockCircleOutlined,
  SyncOutlined
} from '@ant-design/icons';
import axios from 'axios';

const { Text } = Typography;

interface SystemStatsData {
  news_sources: {
    [source: string]: {
      count: number;
      last_fetch: string;
    };
  };
  claude_api_calls: number;
  total_articles: number;
  last_update: string | null;
  cache_status: {
    has_cache: boolean;
    cache_size: number;
    cache_age_seconds: number;
  };
  system_status: {
    uptime_seconds: number;
    cache_duration: number;
  };
}

const SystemStats: React.FC = () => {
  const { data: stats, isLoading, refetch } = useQuery(
    'system-stats',
    async () => {
      const response = await axios.get('/api/v1/stats/dashboard');
      return response.data as SystemStatsData;
    },
    {
      refetchInterval: 30000, // 每30秒刷新一次
    }
  );

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}秒`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}分钟`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}小时`;
    return `${Math.floor(seconds / 86400)}天`;
  };

  const formatTime = (isoString: string | null) => {
    if (!isoString) return '从未';
    return new Date(isoString).toLocaleString('zh-CN');
  };

  if (isLoading || !stats) {
    return (
      <Card title="系统统计" loading={true} size="small">
        <div style={{ height: '200px' }} />
      </Card>
    );
  }

  return (
    <Card 
      title={
        <Space>
          <DatabaseOutlined />
          系统统计
          <Tag color="green" icon={<SyncOutlined spin />}>
            实时
          </Tag>
        </Space>
      }
      size="small"
      extra={
        <Text type="secondary" style={{ fontSize: '12px' }}>
          每30秒更新
        </Text>
      }
    >
      {/* 基础统计 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={12}>
          <Statistic
            title="总新闻数"
            value={stats.total_articles}
            prefix={<CloudOutlined />}
            valueStyle={{ fontSize: '18px' }}
          />
        </Col>
        <Col span={12}>
          <Statistic
            title="Claude API调用"
            value={stats.claude_api_calls}
            prefix={<ApiOutlined />}
            valueStyle={{ fontSize: '18px' }}
          />
        </Col>
      </Row>

      <Divider style={{ margin: '12px 0' }} />

      {/* 新闻源统计 */}
      <div style={{ marginBottom: 16 }}>
        <Text strong style={{ fontSize: '13px' }}>
          <CloudOutlined /> 新闻源统计
        </Text>
        <div style={{ marginTop: 8 }}>
          {Object.keys(stats.news_sources).length === 0 ? (
            <Text type="secondary" style={{ fontSize: '12px' }}>
              暂无数据源统计
            </Text>
          ) : (
            Object.entries(stats.news_sources).map(([source, info]) => (
              <div key={source} style={{ marginBottom: 4 }}>
                <Space size="small">
                  <Tag color="blue">{source}</Tag>
                  <Text style={{ fontSize: '12px' }}>
                    {info.count}条
                  </Text>
                  {info.last_fetch && (
                    <Text type="secondary" style={{ fontSize: '11px' }}>
                      {formatTime(info.last_fetch)}
                    </Text>
                  )}
                </Space>
              </div>
            ))
          )}
        </div>
      </div>

      <Divider style={{ margin: '12px 0' }} />

      {/* 缓存状态 */}
      <div style={{ marginBottom: 16 }}>
        <Text strong style={{ fontSize: '13px' }}>
          <DatabaseOutlined /> 缓存状态
        </Text>
        <div style={{ marginTop: 8 }}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ fontSize: '12px' }}>状态:</Text>
              <Tag 
                color={stats.cache_status.has_cache ? 'success' : 'default'}
              >
                {stats.cache_status.has_cache ? '已缓存' : '无缓存'}
              </Tag>
            </div>
            {stats.cache_status.has_cache && (
              <>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text style={{ fontSize: '12px' }}>缓存大小:</Text>
                  <Text style={{ fontSize: '12px' }}>
                    {stats.cache_status.cache_size}条
                  </Text>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Text style={{ fontSize: '12px' }}>缓存年龄:</Text>
                  <Text style={{ fontSize: '12px' }}>
                    {formatDuration(stats.cache_status.cache_age_seconds)}
                  </Text>
                </div>
              </>
            )}
          </Space>
        </div>
      </div>

      <Divider style={{ margin: '12px 0' }} />

      {/* 系统信息 */}
      <div>
        <Text strong style={{ fontSize: '13px' }}>
          <ClockCircleOutlined /> 系统信息
        </Text>
        <div style={{ marginTop: 8 }}>
          <Space direction="vertical" size="small" style={{ width: '100%' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ fontSize: '12px' }}>最后更新:</Text>
              <Text style={{ fontSize: '12px' }}>
                {formatTime(stats.last_update)}
              </Text>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <Text style={{ fontSize: '12px' }}>缓存周期:</Text>
              <Text style={{ fontSize: '12px' }}>
                {formatDuration(stats.system_status.cache_duration)}
              </Text>
            </div>
          </Space>
        </div>
      </div>
    </Card>
  );
};

export default SystemStats;