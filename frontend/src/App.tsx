import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout, ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import Dashboard from './pages/Dashboard';
import NewsPage from './pages/NewsPage';
import AnalysisPage from './pages/AnalysisPage';
import BacktestPage from './pages/BacktestPage';
import SmartAnalysisPage from './pages/SmartAnalysisPage';
import WatchlistPage from './pages/WatchlistPage';
import TradingAdvicePage from './pages/TradingAdvicePage';
import Navigation from './components/Navigation';
import './App.css';

const { Header, Content } = Layout;

const App: React.FC = () => {
  return (
    <ConfigProvider locale={zhCN}>
      <Layout style={{ minHeight: '100vh' }}>
        <Header style={{ position: 'fixed', zIndex: 1, width: '100%', padding: 0 }}>
          <Navigation />
        </Header>
        <Content style={{ marginTop: 64, padding: '24px' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/news" element={<NewsPage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/smart-analysis" element={<SmartAnalysisPage />} />
            <Route path="/watchlist" element={<WatchlistPage />} />
            <Route path="/trading-advice" element={<TradingAdvicePage />} />
            <Route path="/backtest" element={<BacktestPage />} />
          </Routes>
        </Content>
      </Layout>
    </ConfigProvider>
  );
};

export default App;