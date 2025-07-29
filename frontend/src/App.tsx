import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import Dashboard from './pages/Dashboard';
import NewsPage from './pages/NewsPage';
import AnalysisPage from './pages/AnalysisPage';
import BacktestPage from './pages/BacktestPage';
import Navigation from './components/Navigation';
import './App.css';

const { Header, Content } = Layout;

const App: React.FC = () => {
  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ position: 'fixed', zIndex: 1, width: '100%', padding: 0 }}>
        <Navigation />
      </Header>
      <Content style={{ marginTop: 64, padding: '24px' }}>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/news" element={<NewsPage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
          <Route path="/backtest" element={<BacktestPage />} />
        </Routes>
      </Content>
    </Layout>
  );
};

export default App;