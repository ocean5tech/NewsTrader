import React, { useState } from 'react';
import { Row, Col, Card, Select, Button, Space, Table, Tag, Statistic, Progress } from 'antd';
import { useQuery, useMutation } from 'react-query';
import { PlayCircleOutlined, ReloadOutlined } from '@ant-design/icons';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { backtestApi } from '../services/api';
import { BacktestResult } from '../types';
import dayjs from 'dayjs';

const { Option } = Select;

const BacktestPage: React.FC = () => {
  const [selectedSymbol, setSelectedSymbol] = useState<string>('SPY');
  const [backtestParams, setBacktestParams] = useState({
    days_back: 30,
    time_horizon_hours: 24,
  });

  const {
    data: backtestData,
    isLoading: backtestLoading,
    refetch: refetchBacktest,
  } = useQuery(
    ['backtest-results', selectedSymbol],
    () => backtestApi.getBacktestResults(selectedSymbol, { limit: 100 }),
    { enabled: false }
  );

  const runBacktestMutation = useMutation(
    (params: { symbol: string; days_back: number; time_horizon_hours: number }) =>
      backtestApi.runBacktest(params.symbol, {
        days_back: params.days_back,
        time_horizon_hours: params.time_horizon_hours,
      }),
    {
      onSuccess: () => {
        refetchBacktest();
      },
    }
  );

  const handleRunBacktest = () => {
    runBacktestMutation.mutate({
      symbol: selectedSymbol,
      ...backtestParams,
    });
  };

  const getDirectionColor = (predicted: string, actual: string) => {
    if (predicted === actual) return 'green';
    return 'red';
  };

  const getAccuracyColor = (score: number) => {
    if (score > 0.7) return 'green';
    if (score > 0.4) return 'orange';
    return 'red';
  };

  const prepareAccuracyChartData = () => {
    if (!backtestData) return [];
    
    const dailyData: { [key: string]: { total: number; correct: number } } = {};
    
    backtestData.forEach(result => {
      const date = dayjs(result.created_at).format('MM/DD');
      if (!dailyData[date]) {
        dailyData[date] = { total: 0, correct: 0 };
      }
      dailyData[date].total += 1;
      if (result.predicted_direction === result.actual_direction) {
        dailyData[date].correct += 1;
      }
    });

    return Object.entries(dailyData).map(([date, data]) => ({
      date,
      accuracy: data.total > 0 ? (data.correct / data.total) * 100 : 0,
      predictions: data.total,
    }));
  };

  const calculateSummaryStats = () => {
    if (!backtestData || backtestData.length === 0) {
      return {
        totalPredictions: 0,
        correctPredictions: 0,
        accuracy: 0,
        avgAccuracyScore: 0,
      };
    }

    const correctPredictions = backtestData.filter(
      result => result.predicted_direction === result.actual_direction
    ).length;

    const avgAccuracyScore = backtestData.reduce(
      (sum, result) => sum + result.accuracy_score, 0
    ) / backtestData.length;

    return {
      totalPredictions: backtestData.length,
      correctPredictions,
      accuracy: (correctPredictions / backtestData.length) * 100,
      avgAccuracyScore: avgAccuracyScore * 100,
    };
  };

  const stats = calculateSummaryStats();

  const columns = [
    {
      title: 'Date',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => dayjs(date).format('MM/DD HH:mm'),
    },
    {
      title: 'Predicted',
      dataIndex: 'predicted_direction',
      key: 'predicted_direction',
      render: (direction: string, record: BacktestResult) => (
        <Tag color={getDirectionColor(record.predicted_direction, record.actual_direction)}>
          {direction.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Actual',
      dataIndex: 'actual_direction',
      key: 'actual_direction',
      render: (direction: string) => (
        <Tag color={direction === 'up' ? 'green' : direction === 'down' ? 'red' : 'blue'}>
          {direction.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Pred. Magnitude',
      dataIndex: 'predicted_magnitude',
      key: 'predicted_magnitude',
      render: (mag: number) => (mag * 100).toFixed(2) + '%',
    },
    {
      title: 'Actual Magnitude',
      dataIndex: 'actual_magnitude',
      key: 'actual_magnitude',
      render: (mag: number) => (mag * 100).toFixed(2) + '%',
    },
    {
      title: 'Accuracy Score',
      dataIndex: 'accuracy_score',
      key: 'accuracy_score',
      render: (score: number) => (
        <Tag color={getAccuracyColor(score)}>
          {(score * 100).toFixed(0)}%
        </Tag>
      ),
      sorter: (a: BacktestResult, b: BacktestResult) => a.accuracy_score - b.accuracy_score,
    },
  ];

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Backtest Analysis</h1>
        <Space>
          <Button 
            type="primary" 
            icon={<PlayCircleOutlined />} 
            onClick={handleRunBacktest}
            loading={runBacktestMutation.isLoading}
          >
            Run Backtest
          </Button>
          <Button 
            icon={<ReloadOutlined />} 
            onClick={() => refetchBacktest()}
            loading={backtestLoading}
          >
            Refresh
          </Button>
        </Space>
      </div>

      {/* Controls */}
      <Card style={{ marginBottom: 16 }}>
        <Space wrap>
          <span>Symbol:</span>
          <Select
            value={selectedSymbol}
            style={{ width: 120 }}
            onChange={setSelectedSymbol}
          >
            <Option value="SPY">SPY</Option>
            <Option value="QQQ">QQQ</Option>
            <Option value="GLD">GLD</Option>
            <Option value="CL=F">CL=F</Option>
            <Option value="GC=F">GC=F</Option>
            <Option value="ES=F">ES=F</Option>
          </Select>
          
          <span>Days Back:</span>
          <Select
            value={backtestParams.days_back}
            style={{ width: 100 }}
            onChange={(value) => setBacktestParams({ ...backtestParams, days_back: value })}
          >
            <Option value={7}>7</Option>
            <Option value={14}>14</Option>
            <Option value={30}>30</Option>
            <Option value={60}>60</Option>
          </Select>
          
          <span>Time Horizon:</span>
          <Select
            value={backtestParams.time_horizon_hours}
            style={{ width: 120 }}
            onChange={(value) => setBacktestParams({ ...backtestParams, time_horizon_hours: value })}
          >
            <Option value={6}>6 Hours</Option>
            <Option value={24}>24 Hours</Option>
            <Option value={72}>3 Days</Option>
            <Option value={168}>1 Week</Option>
          </Select>
        </Space>
      </Card>

      {/* Summary Statistics */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Total Predictions"
              value={stats.totalPredictions}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Correct Predictions"
              value={stats.correctPredictions}
              valueStyle={{ color: stats.accuracy > 50 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Direction Accuracy"
              value={stats.accuracy}
              precision={1}
              suffix="%"
              valueStyle={{ color: stats.accuracy > 50 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
        <Col xs={12} md={6}>
          <Card>
            <Statistic
              title="Avg Accuracy Score"
              value={stats.avgAccuracyScore}
              precision={1}
              suffix="%"
              valueStyle={{ color: stats.avgAccuracyScore > 50 ? '#3f8600' : '#cf1322' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Accuracy Over Time Chart */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col span={24}>
          <Card title="Accuracy Over Time" loading={backtestLoading}>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={prepareAccuracyChartData()}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip formatter={(value, name) => [`${value}%`, name]} />
                <Line 
                  type="monotone" 
                  dataKey="accuracy" 
                  stroke="#8884d8" 
                  name="Accuracy %" 
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      {/* Accuracy Progress */}
      <Row gutter={[16, 16]} style={{ marginBottom: 16 }}>
        <Col xs={24} md={12}>
          <Card title="Direction Accuracy">
            <Progress 
              percent={stats.accuracy} 
              status={stats.accuracy > 50 ? 'success' : 'exception'}
              strokeColor={stats.accuracy > 50 ? '#52c41a' : '#ff4d4f'}
            />
          </Card>
        </Col>
        <Col xs={24} md={12}>
          <Card title="Overall Score Accuracy">
            <Progress 
              percent={stats.avgAccuracyScore} 
              status={stats.avgAccuracyScore > 50 ? 'success' : 'exception'}
              strokeColor={stats.avgAccuracyScore > 50 ? '#52c41a' : '#ff4d4f'}
            />
          </Card>
        </Col>
      </Row>

      {/* Results Table */}
      <Card title="Backtest Results" loading={backtestLoading}>
        <Table
          columns={columns}
          dataSource={backtestData}
          rowKey="id"
          pagination={{
            pageSize: 20,
            showSizeChanger: true,
            showQuickJumper: true,
          }}
          size="small"
        />
      </Card>

      {/* Running Status */}
      {runBacktestMutation.isLoading && (
        <Card style={{ marginTop: 16 }}>
          <div style={{ textAlign: 'center', padding: 20 }}>
            <Progress percent={50} status="active" />
            <div style={{ marginTop: 16 }}>
              Running backtest for {selectedSymbol}... This may take a few minutes.
            </div>
          </div>
        </Card>
      )}

      {/* Results Summary */}
      {runBacktestMutation.data && (
        <Card title="Latest Backtest Summary" style={{ marginTop: 16 }}>
          <Row gutter={[16, 16]}>
            <Col span={8}>
              <Statistic
                title="Time Period"
                value={runBacktestMutation.data.time_period}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Total Predictions"
                value={runBacktestMutation.data.total_predictions}
              />
            </Col>
            <Col span={8}>
              <Statistic
                title="Overall Accuracy"
                value={runBacktestMutation.data.summary?.overall_accuracy * 100 || 0}
                precision={1}
                suffix="%"
              />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
};

export default BacktestPage;