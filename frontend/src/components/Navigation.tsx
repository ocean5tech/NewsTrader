import React from 'react';
import { Menu } from 'antd';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  FileTextOutlined,
  BarChartOutlined,
  ExperimentOutlined,
} from '@ant-design/icons';

const Navigation: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/news',
      icon: <FileTextOutlined />,
      label: 'News',
    },
    {
      key: '/analysis',
      icon: <BarChartOutlined />,
      label: 'Analysis',
    },
    {
      key: '/backtest',
      icon: <ExperimentOutlined />,
      label: 'Backtest',
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
        style={{ flex: 1, minWidth: 0 }}
      />
    </div>
  );
};

export default Navigation;