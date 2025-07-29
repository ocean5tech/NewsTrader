export interface NewsArticle {
  id: string;
  title: string;
  content?: string;
  summary: string;
  url: string;
  source: string;
  published_at: string;
  created_at?: string;
  impact_score: number;
  sentiment_score: number;
  affected_symbols: string[];
  keywords?: string[];
  categories?: string[];
  claude_analysis?: any;
  confidence_score: number;
}

export interface MarketSentiment {
  symbol: string;
  sentiment_score: number;
  impact_score: number;
  article_count: number;
  confidence: number;
  time_period_hours: number;
}

export interface ImpactSummary {
  symbol: string;
  article_count: number;
  total_impact: number;
  avg_impact: number;
  avg_sentiment: number;
  avg_confidence: number;
  latest_article: string;
}

export interface BacktestResult {
  id?: string;
  article_id: string;
  article_title?: string;
  published_at?: string;
  predicted_direction: 'up' | 'down' | 'neutral';
  actual_direction: 'up' | 'down' | 'neutral';
  predicted_magnitude: number;
  actual_magnitude: number;
  actual_change_percent?: number;
  accuracy_score: number;
  impact_score?: number;
  confidence_score?: number;
  created_at?: string;
}

export interface BacktestSummary {
  total_predictions: number;
  overall_accuracy: number;
  avg_accuracy_score: number;
  avg_confidence: number;
  direction_breakdown: {
    up_predictions: number;
    down_predictions: number;
    neutral_predictions: number;
    up_accuracy: number;
    down_accuracy: number;
    neutral_accuracy: number;
  };
}

export interface KeywordTrend {
  keyword: string;
  frequency: number;
  avg_impact: number;
  total_impact: number;
}