import React, { useState, useEffect, useRef } from 'react';
import { notification, Badge, Button, Drawer, List, Tag, Typography, Space, Alert as AntAlert } from 'antd';
import {
  BellOutlined,
  AlertOutlined,
  RiseOutlined,
  FallOutlined,
  ExclamationCircleOutlined,
  CloseOutlined
} from '@ant-design/icons';

const { Text, Title } = Typography;

interface NewsAlertData {
  type: string;
  timestamp: string;
  news: {
    id: string;
    title: string;
    summary: string;
    impact_score: number;
    sentiment_score: number;
    watched_symbols: string[];
    source: string;
    url: string;
  };
}

interface AlertItem extends NewsAlertData {
  id: string;
  read: boolean;
}

const NewsAlert: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [connected, setConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const alertIdCounter = useRef(0);

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
        console.log('WebSocket报警连接已建立');
      };

      wsRef.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'news_alert') {
            handleNewsAlert(data);
          }
        } catch (error) {
          console.error('解析报警消息失败:', error);
        }
      };

      wsRef.current.onclose = () => {
        setConnected(false);
        console.log('WebSocket报警连接已断开');
        
        // 5秒后重连
        setTimeout(() => {
          connectWebSocket();
        }, 5000);
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket报警错误:', error);
        setConnected(false);
      };
    } catch (error) {
      console.error('WebSocket报警连接失败:', error);
      setConnected(false);
    }
  };

  const handleNewsAlert = (alertData: NewsAlertData) => {
    const alertItem: AlertItem = {
      ...alertData,
      id: `alert-${alertIdCounter.current++}`,
      read: false
    };

    setAlerts(prev => [alertItem, ...prev.slice(0, 49)]); // 最多保留50条

    // 显示系统通知
    const getSentimentIcon = (score: number) => {
      if (score > 0.1) return <RiseOutlined style={{ color: '#52c41a' }} />;
      if (score < -0.1) return <FallOutlined style={{ color: '#ff4d4f' }} />;
      return <ExclamationCircleOutlined style={{ color: '#faad14' }} />;
    };

    const getSentimentText = (score: number) => {
      if (score > 0.1) return '利好';
      if (score < -0.1) return '利空';
      return '中性';
    };

    notification.warning({
      message: '📢 新闻报警',
      description: (
        <div>
          <div style={{ marginBottom: 8 }}>
            <Text strong>{alertData.news.title}</Text>
          </div>
          <div style={{ marginBottom: 8 }}>
            <Text type="secondary">{alertData.news.summary.substring(0, 100)}...</Text>
          </div>
          <Space>
            <Tag color="red">影响: {alertData.news.impact_score.toFixed(1)}</Tag>
            <Tag color={alertData.news.sentiment_score > 0 ? 'green' : alertData.news.sentiment_score < 0 ? 'red' : 'orange'}>
              {getSentimentIcon(alertData.news.sentiment_score)}
              {getSentimentText(alertData.news.sentiment_score)}
            </Tag>
            {alertData.news.watched_symbols.map(symbol => (
              <Tag key={symbol} color="blue">{symbol}</Tag>
            ))}
          </Space>
        </div>
      ),
      duration: 8,
      placement: 'topRight',
      onClick: () => {
        setDrawerVisible(true);
      }
    });

    // 播放提示音 (可选)
    try {
      const audio = new Audio('/notification.mp3');
      audio.volume = 0.3;
      audio.play().catch(() => {
        // 静默失败，某些浏览器需要用户交互才能播放音频
      });
    } catch (error) {
      // 忽略音频播放错误
    }
  };

  const markAsRead = (alertId: string) => {
    setAlerts(prev => 
      prev.map(alert => 
        alert.id === alertId 
          ? { ...alert, read: true }
          : alert
      )
    );
  };

  const clearAlert = (alertId: string) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const clearAllAlerts = () => {
    setAlerts([]);
  };

  const markAllAsRead = () => {
    setAlerts(prev => prev.map(alert => ({ ...alert, read: true })));
  };

  const unreadCount = alerts.filter(alert => !alert.read).length;

  const getSentimentColor = (score: number) => {
    if (score > 0.1) return '#52c41a';
    if (score < -0.1) return '#ff4d4f';
    return '#faad14';
  };

  const getSentimentIcon = (score: number) => {
    if (score > 0.1) return <RiseOutlined />;
    if (score < -0.1) return <FallOutlined />;
    return <ExclamationCircleOutlined />;
  };

  return (
    <>
      <Badge count={unreadCount} size="small">
        <Button
          type="text"
          icon={<BellOutlined />}
          onClick={() => setDrawerVisible(true)}
          style={{ 
            color: connected ? '#1890ff' : '#d9d9d9',
            fontSize: '16px'
          }}
        />
      </Badge>

      <Drawer
        title={
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Space>
              <AlertOutlined />
              <span>新闻报警 ({alerts.length})</span>
              {unreadCount > 0 && (
                <Badge count={unreadCount} size="small" />
              )}
            </Space>
            <Space>
              {unreadCount > 0 && (
                <Button size="small" onClick={markAllAsRead}>
                  全部已读
                </Button>
              )}
              <Button size="small" onClick={clearAllAlerts} danger>
                清空全部
              </Button>
            </Space>
          </div>
        }
        placement="right"
        width={400}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
      >
        {!connected && (
          <AntAlert
            message="连接状态"
            description="报警系统未连接，正在尝试重连..."
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
          />
        )}

        {alerts.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
            <BellOutlined style={{ fontSize: '48px', marginBottom: '16px' }} />
            <div>暂无报警消息</div>
            <div style={{ fontSize: '12px', marginTop: '8px' }}>
              当关注品种出现高影响新闻时，系统将在此显示报警
            </div>
          </div>
        ) : (
          <List
            dataSource={alerts}
            renderItem={(alert: AlertItem) => (
              <List.Item
                key={alert.id}
                style={{
                  backgroundColor: alert.read ? 'transparent' : '#f6ffed',
                  border: alert.read ? '1px solid #f0f0f0' : '1px solid #b7eb8f',
                  borderRadius: '6px',
                  marginBottom: '8px',
                  padding: '12px',
                  opacity: alert.read ? 0.7 : 1
                }}
                actions={[
                  <Button
                    type="text"
                    size="small"
                    icon={<CloseOutlined />}
                    onClick={() => clearAlert(alert.id)}
                    style={{ color: '#999' }}
                  />
                ]}
              >
                <div
                  style={{ cursor: 'pointer', width: '100%' }}
                  onClick={() => {
                    markAsRead(alert.id);
                    window.open(alert.news.url, '_blank');
                  }}
                >
                  <div style={{ marginBottom: 8 }}>
                    <Text strong={!alert.read} style={{ fontSize: '14px' }}>
                      {alert.news.title}
                    </Text>
                  </div>
                  
                  <div style={{ marginBottom: 8 }}>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      {alert.news.summary.length > 80 
                        ? `${alert.news.summary.substring(0, 80)}...` 
                        : alert.news.summary
                      }
                    </Text>
                  </div>

                  <div style={{ marginBottom: 8 }}>
                    <Space size="small">
                      <Tag color="red">
                        影响: {alert.news.impact_score.toFixed(1)}
                      </Tag>
                      <Tag 
                        color={alert.news.sentiment_score > 0 ? 'green' : alert.news.sentiment_score < 0 ? 'red' : 'orange'}
                      >
                        {getSentimentIcon(alert.news.sentiment_score)}
                        情感: {alert.news.sentiment_score.toFixed(2)}
                      </Tag>
                      <Tag color="blue">
                        {alert.news.source}
                      </Tag>
                    </Space>
                  </div>

                  <div style={{ marginBottom: 8 }}>
                    <Space size="small">
                      {alert.news.watched_symbols.map(symbol => (
                        <Tag key={symbol} color="gold">
                          {symbol}
                        </Tag>
                      ))}
                    </Space>
                  </div>

                  <div style={{ textAlign: 'right' }}>
                    <Text type="secondary" style={{ fontSize: '11px' }}>
                      {new Date(alert.timestamp).toLocaleString('zh-CN')}
                    </Text>
                  </div>
                </div>
              </List.Item>
            )}
          />
        )}
      </Drawer>
    </>
  );
};

export default NewsAlert;