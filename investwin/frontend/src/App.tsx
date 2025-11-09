import React, { useState, useEffect } from 'react'
import { Layout, Card, Table, Button, Space, message, Typography } from 'antd'
import './App.css'

const { Header, Content } = Layout
const { Title } = Typography

interface Asset {
  symbol: string
  name: string
  current_price: number
  change: number
  change_percent: number
}

function App() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(false)

  const fetchAssets = async () => {
    setLoading(true)
    try {
      const response = await fetch('http://localhost:8000/api/assets')
      const data = await response.json()
      setAssets(data)
      message.success('数据加载成功！')
    } catch (error) {
      message.error('加载数据失败，请检查后端服务是否启动')
      console.error('Error fetching assets:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAssets()
  }, [])

  const columns = [
    {
      title: '股票代码',
      dataIndex: 'symbol',
      key: 'symbol',
    },
    {
      title: '公司名称',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: '当前价格',
      dataIndex: 'current_price',
      key: 'current_price',
      render: (price: number) => `$${price.toFixed(2)}`,
    },
    {
      title: '涨跌额',
      dataIndex: 'change',
      key: 'change',
      render: (change: number) => (
        <span style={{ color: change >= 0 ? '#3f8600' : '#cf1322' }}>
          {change >= 0 ? '+' : ''}{change.toFixed(2)}
        </span>
      ),
    },
    {
      title: '涨跌幅',
      dataIndex: 'change_percent',
      key: 'change_percent',
      render: (percent: number) => (
        <span style={{ color: percent >= 0 ? '#3f8600' : '#cf1322' }}>
          {percent >= 0 ? '+' : ''}{percent.toFixed(2)}%
        </span>
      ),
    },
  ]

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ background: '#001529' }}>
        <Title level={3} style={{ color: 'white', margin: '16px 0' }}>
          InvestWin - 投资资产分析平台
        </Title>
      </Header>
      <Content style={{ padding: '24px' }}>
        <Card title="资产概览" extra={
          <Button type="primary" onClick={fetchAssets} loading={loading}>
            刷新数据
          </Button>
        }>
          <Table
            columns={columns}
            dataSource={assets}
            rowKey="symbol"
            loading={loading}
            pagination={false}
          />
        </Card>

        <Card title="系统状态" style={{ marginTop: '24px' }}>
          <Space direction="vertical">
            <div>
              <strong>后端服务：</strong>
              <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
                http://localhost:8000/docs
              </a>
            </div>
            <div>
              <strong>前端服务：</strong>
              <a href="http://localhost:5173" target="_blank" rel="noopener noreferrer">
                http://localhost:5173
              </a>
            </div>
          </Space>
        </Card>
      </Content>
    </Layout>
  )
}

export default App
