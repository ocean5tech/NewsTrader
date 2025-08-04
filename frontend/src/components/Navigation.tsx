import React from 'react';
import { Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import NewsAlert from './NewsAlert';
import {
  DashboardOutlined,
  FileTextOutlined,
  BarChartOutlined,
  ExperimentOutlined,
  FundOutlined,
  StarOutlined,
  BulbOutlined,
} from '@ant-design/icons';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '仪表板',
    },
    {
      key: '/news',
      icon: <FileTextOutlined />,
      label: '新闻资讯',
    },
    {
      key: '/analysis',
      icon: <BarChartOutlined />,
      label: '分析报告',
    },
    {
      key: '/smart-analysis',
      icon: <FundOutlined />,
      label: '智能分析',
    },
    {
      key: '/watchlist',
      icon: <StarOutlined />,
      label: '关注名单',
    },
    {
      key: '/trading-advice',
      icon: <BulbOutlined />,
      label: '交易建议',
    },
    {
      key: '/backtest',
      icon: <ExperimentOutlined />,
      label: '回测验证',
    },
  ];

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
  };

  return (
    <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
      <div
        style={{
          color: 'white',
          fontSize: '20px',
          fontWeight: 'bold',
          marginRight: '40px',
          marginLeft: '24px',
        }}
      >
        NewsTrader
      </div>
      <Menu
        theme="dark"
        mode="horizontal"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ flex: 1, minWidth: 0, border: 'none' }}
      />
      <div style={{ marginRight: '24px' }}>
        <NewsAlert />
      </div>
    </div>
  );
};

export default Navigation;