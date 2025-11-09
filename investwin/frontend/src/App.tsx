import React, { useState, useEffect } from 'react'
import { Layout, Card, Table, Button, Space, message, Typography, Tag, Statistic } from 'antd'
import './App.css'

const { Header, Content } = Layout
const { Title } = Typography

interface Asset {
  symbol: string
  name: string
  sector: string
  industry: string
  current_price: number
  change: number
  change_percent: number
}

interface ApiResponse {
  success: boolean
  assets: Asset[]
  count: number
}

interface HealthResponse {
  status: string
  version: string
  database: string
}

function App() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(false)
  const [systemStatus, setSystemStatus] = useState<HealthResponse | null>(null)

  const fetchAssets = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/assets')
      const data: ApiResponse = await response.json()

      if (data.success) {
        setAssets(data.assets)
        message.success(`成功加载 ${data.count} 只股票！`)
      } else {
        message.error('数据加载失败')
      }
    } catch (error) {
      message.error('加载数据失败，请检查后端服务是否启动')
      console.error('Error fetching assets:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchSystemStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/health')
      const data: HealthResponse = await response.json()
      setSystemStatus(data)
    } catch (error) {
      console.error('Error fetching system status:', error)
    }
  }

  useEffect(() => {
    fetchAssets()
    fetchSystemStatus()

    // 设置定时刷新
    const interval = setInterval(() => {
      fetchAssets()
      fetchSystemStatus()
    }, 30000) // 每30秒刷新一次

    return () => clearInterval(interval)
  }, [])

  const columns = [
    {
      title: '股票代码',
      dataIndex: 'symbol',
      key: 'symbol',
      render: (symbol: string) => (
        <Tag color="blue">{symbol}</Tag>
      ),
    },
    {
      title: '公司名称',
      dataIndex: 'name',
      key: 'name',
      ellipsis: true,
    },
    {
      title: '行业',
      dataIndex: 'sector',
      key: 'sector',
      render: (sector: string) => (
        <Tag color="green">{sector}</Tag>
      ),
    },
    {
      title: '当前价格',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (price: number, record: Asset) => (
        <Statistic
          value={price}
          precision={2}
          prefix="$"
          valueStyle={{
            color: record.change >= 0 ? '#3f8600' : '#cf1322',
            fontSize: '14px'
          }}
        />
      ),
    },
    {
      title: '涨跌额',
      dataIndex: 'change',
      key: 'change',
      render: (change: number) => (
        <span style={{
          color: change >= 0 ? '#3f8600' : '#cf1322',
          fontWeight: 'bold'
        }}>
          {change >= 0 ? '+' : ''}{change.toFixed(2)}
        </span>
      ),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_percent',
      key: 'change_percent',
      render: (percent: number) => (
        <span style={{
          color: percent >= 0 ? '#3f8600' : '#cf1322',
          fontWeight: 'bold'
        }}>
          {percent >= 0 ? '+' : ''}{percent.toFixed(2)}%
        </span>
      ),
    },
  ]

  const calculatePortfolioStats = () => {
    if (assets.length === 0) return { totalValue: 0, totalChange: 0, changePercent: 0 }

    const totalValue = assets.reduce((sum, asset) => sum + asset.current_price, 0)
    const totalChange = assets.reduce((sum, asset) => sum + asset.change, 0)
    const avgChangePercent = assets.reduce((sum, asset) => sum + asset.change_percent, 0) / assets.length

    return {
      totalValue: totalValue / assets.length,
      totalChange: totalChange / assets.length,
      changePercent: avgChangePercent
    }
  }

  const stats = calculatePortfolioStats()

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529', padding: '0 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', height: '100%' }}>
          <Title level={3} style={{ color: 'white', margin: 0 }}>
            InvestWin - 投资资产分析平台
          </Title>
          {systemStatus && (
            <Space style={{ marginLeft: 'auto' }}>
              <Tag color={systemStatus.status === 'healthy' ? 'green' : 'red'}>
                系统: {systemStatus.status}
              </Tag>
              <Tag color="blue">
                数据库: {systemStatus.database}
              </Tag>
            </Space>
          )}
        </div>
      </Header>
      <Content style={{ padding: '24px' }}>
        <Card title="投资组合概览" style={{ marginBottom: '16px' }}>
          <Space size="large">
            <Statistic
              title="股票数量"
              value={assets.length}
              suffix="只"
            />
            <Statistic
              title="平均价格"
              value={stats.totalValue}
              precision={2}
              prefix="$"
            />
            <Statistic
              title="平均涨跌"
              value={stats.totalChange}
              precision={2}
              prefix="$"
              valueStyle={{
                color: stats.totalChange >= 0 ? '#3f8600' : '#cf1322'
              }}
            />
            <Statistic
              title="平均涨跌幅"
              value={stats.changePercent}
              precision={2}
              suffix="%"
              valueStyle={{
                color: stats.changePercent >= 0 ? '#3f8600' : '#cf1322'
              }}
            />
          </Space>
        </Card>

        <Card title="资产列表" extra={
          <Button type="primary" onClick={fetchAssets} loading={loading}>
            刷新数据
          </Button>
        }>
          <Table
            columns={columns}
            dataSource={assets}
            rowKey="symbol"
            loading={loading}
            pagination={{ pageSize: 10 }}
            scroll={{ x: 800 }}
          />
        </Card>

        <Card title="系统信息" style={{ marginTop: '16px' }}>
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <strong>🔗 API 文档：</strong>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" style={{ marginLeft: 8 }}>
                http://localhost:8000/docs
              </a>
            </div>
            <div>
              <strong>💻 后端服务：</strong>
              <Tag color="blue" style={{ marginLeft: 8 }}>Port 8000</Tag>
            </div>
            <div>
              <strong>🌐 前端服务：</strong>
              <Tag color="green" style={{ marginLeft: 8 }}>Port 5173</Tag>
            </div>
            <div>
              <strong>🗄️ 数据库：</strong>
              <Tag color="orange" style={{ marginLeft: 8 }}>{systemStatus?.database || 'unknown'}</Tag>
            </div>
          </Space>
        </Card>
      </Content>
    </Layout>
  )
}

export default App
