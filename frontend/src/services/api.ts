import axios from 'axios';
import { NewsArticle, MarketSentiment, ImpactSummary, BacktestResult, KeywordTrend } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 30000,
});

// News API
export const newsApi = {
  getArticles: async (params?: {
    limit?: number;
    offset?: number;
    symbol?: string;
    min_impact?: number;
  }): Promise<NewsArticle[]> => {
    const response = await api.get('/news/articles', { params });
    return response.data;
  },

  getArticle: async (id: string): Promise<NewsArticle> => {
    const response = await api.get(`/news/articles/${id}`);
    return response.data;
  },

  scrapeNews: async (): Promise<{ message: string; count: number }> => {
    const response = await api.post('/news/scrape');
    return response.data;
  },

  getTrendingNews: async (params?: {
    hours?: number;
    min_impact?: number;
  }): Promise<NewsArticle[]> => {
    const response = await api.get('/news/trending', { params });
    return response.data;
  },
};

// Analysis API
export const analysisApi = {
  analyzeArticle: async (data: {
    title: string;
    content: string;
    symbols?: string[];
  }): Promise<any> => {
    const response = await api.post('/analysis/analyze', data);
    return response.data;
  },

  getMarketSentiment: async (params?: {
    symbol?: string;
    hours?: number;
  }): Promise<MarketSentiment> => {
    const response = await api.get('/analysis/market-sentiment', { params });
    return response.data;
  },

  getImpactSummary: async (params?: {
    hours?: number;
  }): Promise<{ summary: ImpactSummary[]; time_period_hours: number; total_articles: number }> => {
    const response = await api.get('/analysis/impact-summary', { params });
    return response.data;
  },

  getKeywordTrends: async (params?: {
    days?: number;
    limit?: number;
  }): Promise<{ trends: KeywordTrend[]; time_period_days: number; total_articles: number }> => {
    const response = await api.get('/analysis/keyword-trends', { params });
    return response.data;
  },
};

// Backtest API
export const backtestApi = {
  runBacktest: async (
    symbol: string,
    params?: {
      days_back?: number;
      time_horizon_hours?: number;
    }
  ): Promise<{
    symbol: string;
    time_period: string;
    time_horizon_hours: number;
    total_predictions: number;
    summary: any;
    results: BacktestResult[];
  }> => {
    const response = await api.post(`/backtest/run/${symbol}`, null, { params });
    return response.data;
  },

  getBacktestResults: async (
    symbol: string,
    params?: {
      limit?: number;
    }
  ): Promise<BacktestResult[]> => {
    const response = await api.get(`/backtest/results/${symbol}`, { params });
    return response.data;
  },
};

export default api;