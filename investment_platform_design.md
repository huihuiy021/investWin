# 投资资产分析跟踪平台设计方案

## 项目概述
一个基于 **React + Python + PostgreSQL** 的投资资产分析跟踪平台，采用**微服务架构**，专注于投资机会挖掘和风险控制。

## 架构设计理念

### 🏗️ **微服务分离架构**
采用 **Web 服务 + 业务服务** 分离设计，实现职责清晰、独立扩展、高可维护性的系统架构。

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend       │    │  Web Service     │    │ Business Service │
│   (React)        │───▶│  (FastAPI)       │───▶│  (Python)        │
│                 │    │  Port: 8000      │    │  Port: 8001      │
│ • 用户界面       │    │ • HTTP API       │    │ • 业务逻辑       │
│ • 数据展示       │    │ • 用户认证       │    │ • 投资分析       │
│ • 交互操作       │    │ • 请求路由       │    │ • 风险计算       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL     │    │   Redis Cache    │
                       │   Database       │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 核心功能模块

### ✅ **资产分析跟踪模块**
- 多资产类型支持（股票、期权、期货）
- 实时价格跟踪和历史数据展示
- 技术指标自动计算（MA、RSI、MACD等）
- 资产收益率和趋势分析

### ✅ **投资机会挖掘模块**
- **技术面机会**：突破识别、超买超卖检测、形态识别
- **资金流机会**：成交量异常、大单流入、机构动向分析
- **衍生品机会**：期权波动率交易、套利机会识别
- **智能算法引擎**：多维度机会识别和置信度评分

### ✅ **风险控制模块**
- **个股风险评估**：VaR计算、最大回撤、波动率分析
- **组合风险监控**：相关性分析、集中度风险、分散度评估
- **实时预警系统**：价格下跌、波动率激增、异常交易监控
- **压力测试**：多种情景分析和风险评估

## 技术架构

### **🌐 前端层 (React + TypeScript)**
- **UI框架**：Ant Design（专业组件库）
- **状态管理**：Redux Toolkit（可预测状态管理）
- **数据可视化**：Chart.js/Recharts（交互式图表）
- **HTTP客户端**：Axios（API请求）
- **实时通信**：WebSocket（实时数据更新）

### **🔌 Web 服务层 (FastAPI - Port: 8000)**
- **框架选择**：FastAPI（高性能、自动API文档）
- **核心职责**：
  - HTTP API 接口处理
  - 用户认证和授权（JWT）
  - 请求参数验证
  - 响应格式化
  - 与前端通信
  - 调用业务服务
- **核心库**：SQLAlchemy（ORM）、Pydantic（数据验证）、httpx（服务间通信）

### **⚙️ 业务服务层 (Python - Port: 8001)**
- **框架选择**：FastAPI（轻量级API）
- **核心职责**：
  - 投资机会挖掘算法
  - 技术指标计算（MA、RSI、MACD等）
  - 风险评估模型（VaR、最大回撤、波动率）
  - 投资组合优化
  - 数据分析和处理
- **核心库**：pandas/numpy（数据处理）、yfinance（数据获取）、TA-Lib（技术指标）

### **🗄️ 数据存储层**
#### **PostgreSQL (主数据库)**
- **用户数据**：账户信息、偏好设置
- **投资数据**：资产信息、交易记录、持仓数据
- **分析结果**：风险评估、机会挖掘结果
- **优势利用**：JSONB存储复杂数据、时间序列优化、窗口函数

#### **Redis (缓存层)**
- **实时数据缓存**：股票价格、技术指标
- **计算结果缓存**：分析结果、风险评估
- **会话管理**：用户认证信息
- **任务队列**：异步分析任务

### **📡 服务间通信**
- **同步通信**：HTTP REST API（Web → Business）
- **异步通信**：Redis Pub/Sub（事件驱动）
- **数据格式**：JSON（标准化的数据交换格式）

## 数据库设计

### 1. **核心数据表设计**

#### 用户系统
```sql
-- 用户表
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    risk_profile VARCHAR(20) DEFAULT 'moderate', -- conservative, moderate, aggressive
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 用户投资偏好
CREATE TABLE user_preferences (
    user_id INTEGER REFERENCES users(id),
    preferred_sectors TEXT[], -- 关注的行业板块
    max_portfolio_size INTEGER DEFAULT 50,
    alert_enabled BOOLEAN DEFAULT true,
    risk_tolerance_level NUMERIC(3,2) CHECK (risk_tolerance_level BETWEEN 0 AND 1)
);
```

#### 金融工具数据
```sql
-- 股票基础信息
CREATE TABLE stocks (
    symbol VARCHAR(10) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    sector VARCHAR(50),
    industry VARCHAR(100),
    market_cap BIGINT,
    exchange VARCHAR(10),
    country VARCHAR(3),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 期权链数据
CREATE TABLE options_chain (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    expiration DATE NOT NULL,
    strike NUMERIC(10,2) NOT NULL,
    option_type VARCHAR(4) CHECK (option_type IN ('call', 'put')),
    implied_volatility NUMERIC(8,4),
    greeks JSONB, -- {"delta": 0.5, "gamma": 0.1, "theta": -0.05, "vega": 0.2}
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(symbol, expiration, strike, option_type)
);

-- 期货合约
CREATE TABLE futures (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    exchange VARCHAR(20),
    contract_size INTEGER,
    tick_value NUMERIC(10,4),
    margin_requirement NUMERIC(10,2)
);
```

#### 价格数据（时间序列）
```sql
-- 股票价格数据（分区表）
CREATE TABLE stock_prices (
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    date DATE NOT NULL,
    open_price NUMERIC(12,4),
    high_price NUMERIC(12,4),
    low_price NUMERIC(12,4),
    close_price NUMERIC(12,4),
    volume BIGINT,
    adj_close NUMERIC(12,4),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (symbol, date)
) PARTITION BY RANGE (date);

-- 技术指标（使用JSONB存储多个指标）
CREATE TABLE technical_indicators (
    symbol VARCHAR(10) REFERENCES stocks(symbol),
    date DATE NOT NULL,
    indicators JSONB, -- {"ma20": 150.25, "rsi": 65.5, "macd": 2.1}
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    PRIMARY KEY (symbol, date)
);
```

#### 投资组合管理
```sql
-- 投资组合
CREATE TABLE portfolios (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 持仓明细
CREATE TABLE portfolio_positions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    asset_type VARCHAR(10) CHECK (asset_type IN ('stock', 'option', 'future')),
    symbol VARCHAR(20) NOT NULL,
    quantity NUMERIC(15,4),
    avg_cost NUMERIC(12,4),
    current_price NUMERIC(12,4),
    market_value NUMERIC(15,2),
    unrealized_pnl NUMERIC(15,2),
    position_date DATE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 交易记录
CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    portfolio_id INTEGER REFERENCES portfolios(id),
    asset_type VARCHAR(10) CHECK (asset_type IN ('stock', 'option', 'future')),
    symbol VARCHAR(20) NOT NULL,
    action VARCHAR(4) CHECK (action IN ('buy', 'sell')),
    quantity NUMERIC(15,4),
    price NUMERIC(12,4),
    commission NUMERIC(8,2) DEFAULT 0,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    notes TEXT
);
```

#### 策略和回测
```sql
-- 投资策略
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    strategy_config JSONB, -- 策略参数配置
    is_public BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 回测结果
CREATE TABLE backtest_results (
    id SERIAL PRIMARY KEY,
    strategy_id INTEGER REFERENCES strategies(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    initial_capital NUMERIC(15,2),
    final_value NUMERIC(15,2),
    total_return NUMERIC(8,4),
    sharpe_ratio NUMERIC(6,3),
    max_drawdown NUMERIC(6,3),
    win_rate NUMERIC(5,4),
    results_data JSONB, -- 详细回测数据
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 投资机会挖掘算法设计

### 1. **技术面机会识别算法**
```python
# 突破机会识别
def detect_breakout_opportunities(stock_data):
    """
    识别价格突破机会
    - 阻力位突破
    - 支撑位反弹
    - 整理形态突破
    """
    opportunities = []

    # 计算关键价位
    resistance_levels = calculate_resistance_levels(stock_data)
    support_levels = calculate_support_levels(stock_data)

    # 突破检测逻辑
    current_price = stock_data[-1]['close']
    volume = stock_data[-1]['volume']
    avg_volume = calculate_avg_volume(stock_data, 20)

    # 阻力位突破
    for level in resistance_levels:
        if current_price > level and volume > avg_volume * 1.5:
            opportunities.append({
                'type': 'resistance_breakout',
                'price_level': level,
                'confidence': calculate_breakout_confidence(stock_data, level)
            })

    return opportunities

# 超买超卖机会
def detect_oversold_overbought_opportunities(stock_data):
    """
    基于RSI、布林带等指标识别超买超卖机会
    """
    rsi = calculate_rsi(stock_data, 14)
    bollinger_bands = calculate_bollinger_bands(stock_data, 20, 2)

    opportunities = []
    current_price = stock_data[-1]['close']

    # 超卖反弹机会
    if rsi < 30 and current_price <= bollinger_bands['lower_band']:
        opportunities.append({
            'type': 'oversold_bounce',
            'rsi': rsi,
            'price_position': 'below_lower_band',
            'potential_upside': calculate_potential_upside(stock_data)
        })

    return opportunities
```

### 2. **资金流机会识别算法**
```python
def detect_volume_anomalies(stock_data):
    """
    识别成交量异常机会
    """
    opportunities = []

    # 计算成交量基准
    avg_volume_5d = calculate_avg_volume(stock_data, 5)
    avg_volume_20d = calculate_avg_volume(stock_data, 20)
    current_volume = stock_data[-1]['volume']

    # 放量检测
    volume_ratio = current_volume / avg_volume_20d
    price_change = (stock_data[-1]['close'] - stock_data[-2]['close']) / stock_data[-2]['close']

    if volume_ratio > 3 and price_change > 0.05:  # 放量上涨
        opportunities.append({
            'type': 'volume_surge_up',
            'volume_ratio': volume_ratio,
            'price_change': price_change,
            'strength': 'strong' if volume_ratio > 5 else 'moderate'
        })

    return opportunities

def detect_institutional_flow(trade_data):
    """
    识别机构资金流向
    """
    # 基于大单交易数据分析机构动向
    large_trades = filter_large_trades(trade_data, min_size=1000000)

    if len(large_trades) > 0:
        net_flow = calculate_net_flow(large_trades)
        return {
            'type': 'institutional_flow',
            'net_flow': net_flow,
            'trade_count': len(large_trades),
            'sentiment': 'bullish' if net_flow > 0 else 'bearish'
        }
```

### 3. **期权机会挖掘算法**
```python
def detect_option_volatility_opportunities(option_chain):
    """
    识别期权波动率交易机会
    """
    opportunities = []

    # 计算隐含波动率偏斜
    iv_skew = calculate_iv_skew(option_chain)

    # 波动率低估/高估机会
    historical_vol = calculate_historical_volatility(underlying_stock, 30)
    avg_iv = calculate_average_iv(option_chain)

    if avg_iv < historical_vol * 0.8:  # 隐含波动率低估
        opportunities.append({
            'type': 'iv_undervalued',
            'strategy': 'long_straddle' if iv_skew < 0 else 'long_calendar',
            'iv_ratio': avg_iv / historical_vol
        })

    return opportunities

def detect_option_flow_anomalies(option_trades):
    """
    识别期权异动交易
    """
    # 监控异常大额期权交易
    unusual_trades = detect_unusual_option_activity(option_trades)

    for trade in unusual_trades:
        opportunities.append({
            'type': 'option_flow_anomaly',
            'trade_details': trade,
            'sentiment_implication': analyze_option_sentiment(trade),
            'confidence_score': calculate_flow_confidence(trade)
        })
```

## 风险控制机制设计

### 1. **多层风险监控体系**

```python
# 个股风险评估
class IndividualStockRisk:
    def calculate_var(self, price_data, confidence_level=0.95, holding_period=1):
        """
        计算VaR (Value at Risk) - 在险价值
        """
        returns = calculate_daily_returns(price_data)
        var_percentile = (1 - confidence_level) * 100

        var_value = np.percentile(returns, var_percentile) * holding_period
        return {
            'var_95': var_value,
            'var_99': np.percentile(returns, 1) * holding_period,
            'interpretation': f'未来{holding_period}天有{confidence_level*100}%概率损失不超过{abs(var_value):.2%}'
        }

    def calculate_max_drawdown(self, price_data):
        """
        计算最大回撤
        """
        peak = price_data['close'].expanding().max()
        drawdown = (price_data['close'] - peak) / peak
        max_dd = drawdown.min()

        return {
            'max_drawdown': max_dd,
            'max_dd_duration': calculate_drawdown_duration(drawdown),
            'current_drawdown': drawdown.iloc[-1]
        }

    def calculate_volatility_risk(self, price_data, window=20):
        """
        计算波动率风险
        """
        returns = calculate_daily_returns(price_data)
        rolling_vol = returns.rolling(window=window).std() * np.sqrt(252)

        current_vol = rolling_vol.iloc[-1]
        vol_percentile = rolling_vol.quantile([0.25, 0.5, 0.75])

        return {
            'current_volatility': current_vol,
            'volatility_level': self.classify_volatility_level(current_vol, vol_percentile),
            'volatility_trend': 'increasing' if rolling_vol.iloc[-1] > rolling_vol.iloc[-5] else 'decreasing'
        }
```

### 2. **投资组合风险控制**

```python
# 组合风险分散度分析
class PortfolioRiskManager:
    def calculate_correlation_matrix(self, portfolio_positions):
        """
        计算持仓相关性矩阵
        """
        returns_data = {}
        for position in portfolio_positions:
            returns_data[position['symbol']] = get_historical_returns(position['symbol'])

        correlation_matrix = pd.DataFrame(returns_data).corr()
        return correlation_matrix

    def calculate_concentration_risk(self, portfolio_positions):
        """
        计算集中度风险
        """
        total_value = sum(pos['market_value'] for pos in portfolio_positions)

        # 按股票计算集中度
        stock_concentration = {}
        for pos in portfolio_positions:
            weight = pos['market_value'] / total_value
            stock_concentration[pos['symbol']] = weight

        # 计算Herfindahl指数
        hhi = sum(weight**2 for weight in stock_concentration.values())

        return {
            'concentration_risk': 'high' if hhi > 0.25 else 'medium' if hhi > 0.15 else 'low',
            'herfindahl_index': hhi,
            'top_position_weight': max(stock_concentration.values()),
            'diversification_score': 1 - hhi
        }

    def generate_portfolio_rebalancing_suggestions(self, portfolio_positions):
        """
        生成组合再平衡建议
        """
        current_weights = self.calculate_current_weights(portfolio_positions)
        target_weights = self.get_optimal_weights(portfolio_positions)

        suggestions = []
        for symbol in current_weights:
            current_weight = current_weights[symbol]
            target_weight = target_weights.get(symbol, 0)

            if abs(current_weight - target_weight) > 0.05:  # 5%阈值
                action = 'reduce' if current_weight > target_weight else 'increase'
                suggestions.append({
                    'symbol': symbol,
                    'action': action,
                    'current_weight': current_weight,
                    'target_weight': target_weight,
                    'adjustment_amount': abs(current_weight - target_weight)
                })

        return suggestions
```

### 3. **实时风险预警系统**

```python
class RiskAlertSystem:
    def __init__(self):
        self.alert_rules = self.load_default_rules()

    def load_default_rules(self):
        return {
            'price_drop_alert': {
                'threshold': -0.15,  # 15%下跌
                'timeframe': 'daily',
                'priority': 'high'
            },
            'volatility_spike': {
                'threshold': 3.0,  # 波动率超过3倍
                'baseline_window': 20,
                'priority': 'medium'
            },
            'volume_anomaly': {
                'threshold': 5.0,  # 成交量异常5倍
                'priority': 'medium'
            },
            'correlation_increase': {
                'threshold': 0.8,  # 相关性超过80%
                'priority': 'low'
            }
        }

    def check_risk_alerts(self, asset_data, portfolio_data):
        """
        检查风险预警条件
        """
        alerts = []

        # 价格下跌预警
        price_change = self.calculate_price_change(asset_data)
        if price_change <= self.alert_rules['price_drop_alert']['threshold']:
            alerts.append({
                'type': 'price_drop',
                'severity': 'high',
                'message': f'资产价格下跌 {abs(price_change):.2%}',
                'suggestion': '考虑减仓或设置止损'
            })

        # 波动率激增预警
        current_vol = self.calculate_current_volatility(asset_data)
        avg_vol = self.calculate_average_volatility(asset_data, 20)
        if current_vol > avg_vol * self.alert_rules['volatility_spike']['threshold']:
            alerts.append({
                'type': 'volatility_spike',
                'severity': 'medium',
                'message': f'波动率激增至正常水平的 {current_vol/avg_vol:.1f} 倍',
                'suggestion': '注意仓位控制，考虑对冲策略'
            })

        return alerts

    def generate_risk_report(self, portfolio_data):
        """
        生成风险评估报告
        """
        report = {
            'overall_risk_score': self.calculate_overall_risk_score(portfolio_data),
            'key_risks': self.identify_key_risks(portfolio_data),
            'recommendations': self.generate_risk_recommendations(portfolio_data),
            'stress_test_results': self.run_stress_tests(portfolio_data)
        }

        return report
```

### 4. **压力测试系统**

```python
def run_stress_scenarios(portfolio_positions):
    """
    运行压力测试情景
    """
    scenarios = {
        'market_crash': {'market_decline': -0.30, 'volatility_spike': 2.5},
        'sector_rotation': {'tech_decline': -0.20, 'financial_gain': 0.10},
        'interest_rate_shock': {'rate_increase': 0.02, 'bond_impact': -0.15},
        'liquidity_crisis': {'volume_decline': -0.50, 'spread_widening': 0.02}
    }

    results = {}
    for scenario_name, parameters in scenarios.items():
        scenario_loss = calculate_scenario_impact(portfolio_positions, parameters)
        results[scenario_name] = {
            'potential_loss': scenario_loss,
            'loss_percentage': scenario_loss / calculate_portfolio_value(portfolio_positions),
            'worst_affected_positions': identify_worst_positions(portfolio_positions, parameters)
        }

    return results
```

## 系统架构和API接口设计

### 1. **后端API接口设计 (FastAPI)**

```python
# app/api/assets.py - 资产管理API
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

router = APIRouter(prefix="/api/assets", tags=["assets"])

@router.get("/", response_model=List[AssetResponse])
async def get_assets(
    skip: int = 0,
    limit: int = 50,
    asset_type: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """获取用户资产列表"""
    pass

@router.post("/", response_model=AssetResponse)
async def add_asset(
    asset: AssetCreate,
    current_user: User = Depends(get_current_user)
):
    """添加新资产到跟踪列表"""
    pass

@router.get("/{symbol}/analysis")
async def get_asset_analysis(
    symbol: str,
    timeframe: str = "daily",
    current_user: User = Depends(get_current_user)
):
    """获取资产分析结果"""
    pass

@router.get("/{symbol}/realtime")
async def get_realtime_data(symbol: str):
    """获取实时价格数据"""
    pass
```

```python
# app/api/opportunities.py - 机会挖掘API
@router.get("/api/opportunities", response_model=List[OpportunityResponse])
async def get_investment_opportunities(
    opportunity_type: Optional[str] = None,
    min_confidence: float = 0.6,
    current_user: User = Depends(get_current_user)
):
    """获取投资机会列表"""
    pass

@router.get("/api/opportunities/scan")
async def scan_market_opportunities():
    """扫描市场机会（定时任务触发）"""
    pass

@router.post("/api/opportunities/{id}/track")
async def track_opportunity(
    id: int,
    track_data: OpportunityTrack,
    current_user: User = Depends(get_current_user)
):
    """跟踪特定投资机会"""
    pass
```

```python
# app/api/risk.py - 风险控制API
@router.get("/api/risk/portfolio")
async def get_portfolio_risk(
    current_user: User = Depends(get_current_user)
):
    """获取投资组合风险评估"""
    pass

@router.get("/api/risk/alerts")
async def get_risk_alerts(
    current_user: User = Depends(get_current_user)
):
    """获取风险预警信息"""
    pass

@router.post("/api/risk/stress-test")
async def run_stress_test(
    test_config: StressTestConfig,
    current_user: User = Depends(get_current_user)
):
    """运行压力测试"""
    pass
```

### 2. **WebSocket 实时数据接口**

```python
# app/websocket/realtime_data.py
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_subscriptions: dict = {}

manager = ConnectionManager()

@router.websocket("/ws/realtime/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # 处理订阅请求
            subscription_data = json.loads(data)
            await handle_subscription(websocket, subscription_data)

            # 发送实时数据
            realtime_data = await get_realtime_data(subscription_data.get('symbols'))
            await websocket.send_text(json.dumps(realtime_data))

    except WebSocketDisconnect:
        manager.disconnect(websocket)
```

### 3. **数据服务层设计**

```python
# app/services/data_service.py
class MarketDataService:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.data_sources = {
            'yahoo_finance': YahooFinanceClient(),
            'alpha_vantage': AlphaVantageClient(),
            'polygon': PolygonClient()
        }

    async def get_real_time_price(self, symbol: str) -> RealTimePrice:
        """获取实时价格"""
        # 先检查缓存
        cached_data = self.redis_client.get(f"price:{symbol}")
        if cached_data:
            return json.loads(cached_data)

        # 从数据源获取
        for source_name, source_client in self.data_sources.items():
            try:
                data = await source_client.get_quote(symbol)
                # 缓存30秒
                self.redis_client.setex(f"price:{symbol}", 30, json.dumps(data))
                return data
            except Exception as e:
                continue

        raise HTTPException(status_code=404, detail=f"Data not found for {symbol}")

class AnalysisService:
    def __init__(self):
        self.indicator_calculator = TechnicalIndicators()
        self.opportunity_detector = OpportunityDetector()

    async def analyze_asset(self, symbol: str, timeframe: str) -> AssetAnalysis:
        """综合分析资产"""
        price_data = await self.get_historical_data(symbol, timeframe)

        # 计算技术指标
        indicators = self.indicator_calculator.calculate_all(price_data)

        # 挖掘投资机会
        opportunities = self.opportunity_detector.detect_opportunities(price_data, indicators)

        # 风险评估
        risk_metrics = self.calculate_risk_metrics(price_data)

        return AssetAnalysis(
            symbol=symbol,
            current_price=price_data.iloc[-1]['close'],
            indicators=indicators,
            opportunities=opportunities,
            risk_metrics=risk_metrics,
            updated_at=datetime.now()
        )
```

### 4. **前端状态管理设计**

```typescript
// src/store/store.ts
import { configureStore } from '@reduxjs/toolkit'
import assetsReducer from './slices/assetsSlice'
import opportunitiesReducer from './slices/opportunitiesSlice'
import riskReducer from './slices/riskSlice'

export const store = configureStore({
  reducer: {
    assets: assetsReducer,
    opportunities: opportunitiesReducer,
    risk: riskReducer,
  },
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

```typescript
// src/store/slices/assetsSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit'

interface Asset {
  symbol: string
  name: string
  currentPrice: number
  change: number
  changePercent: number
  indicators: TechnicalIndicators
  lastUpdate: string
}

export const fetchAssets = createAsyncThunk(
  'assets/fetchAssets',
  async (_, { rejectWithValue }) => {
    try {
      const response = await api.get('/assets/')
      return response.data
    } catch (error) {
      return rejectWithValue(error.response.data)
    }
  }
)

const assetsSlice = createSlice({
  name: 'assets',
  initialState,
  reducers: {
    updateRealTimePrice: (state, action) => {
      const { symbol, price, change } = action.payload
      const asset = state.assets.find(a => a.symbol === symbol)
      if (asset) {
        asset.currentPrice = price
        asset.change = change
        asset.changePercent = (change / (price - change)) * 100
        asset.lastUpdate = new Date().toISOString()
      }
    },
  },
  extraReducers: (builder) => {
    builder.addCase(fetchAssets.fulfilled, (state, action) => {
      state.assets = action.payload
      state.loading = false
    })
  },
})
```

## 前端页面结构设计

### 1. **整体页面架构**

```
src/pages/
├── Dashboard/
│   ├── index.tsx           # 总览仪表板
│   ├── components/
│   │   ├── PortfolioSummary.tsx
│   │   ├── MarketOverview.tsx
│   │   ├── RecentOpportunities.tsx
│   │   └── RiskAlerts.tsx
├── Assets/
│   ├── index.tsx           # 资产管理页面
│   ├── AssetDetail.tsx     # 资产详情页面
│   └── components/
│       ├── AssetCard.tsx
│       ├── AssetTable.tsx
│       ├── AddAssetModal.tsx
│       └── PriceChart.tsx
├── Opportunities/
│   ├── index.tsx           # 投资机会页面
│   ├── OpportunityDetail.tsx # 机会详情页面
│   └── components/
│       ├── OpportunityCard.tsx
│       ├── OpportunityFilters.tsx
│       └── TechnicalScanner.tsx
└── RiskAnalysis/
    ├── index.tsx           # 风险分析页面
    └── components/
        ├── RiskDashboard.tsx
        ├── StressTest.tsx
        └── RiskAlerts.tsx
```

### 2. **核心页面组件设计**

```typescript
// src/pages/Dashboard/index.tsx
import React from 'react'
import { Grid, Card, Row, Col } from 'antd'
import PortfolioSummary from './components/PortfolioSummary'
import MarketOverview from './components/MarketOverview'
import RecentOpportunities from './components/RecentOpportunities'
import RiskAlerts from './components/RiskAlerts'

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard">
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <PortfolioSummary />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={16}>
          <MarketOverview />
        </Col>
        <Col span={8}>
          <RecentOpportunities />
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={24}>
          <RiskAlerts />
        </Col>
      </Row>
    </div>
  )
}
```

```typescript
// src/pages/Assets/AssetDetail.tsx
import React, { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Card, Tabs, Row, Col, Statistic } from 'antd'
import PriceChart from '../components/PriceChart'
import TechnicalIndicators from '../components/TechnicalIndicators'
import RiskMetrics from '../components/RiskMetrics'
import RelatedOpportunities from '../components/RelatedOpportunities'

const { TabPane } = Tabs

const AssetDetail: React.FC = () => {
  const { symbol } = useParams<{ symbol: string }>()
  const [assetData, setAssetData] = useState<any>(null)

  useEffect(() => {
    // 获取资产详细数据
    fetchAssetDetails(symbol)
  }, [symbol])

  return (
    <div className="asset-detail">
      <Row gutter={[16, 16]}>
        <Col span={24}>
          <Card>
            <Row gutter={16}>
              <Col span={6}>
                <Statistic title="当前价格" value={assetData?.currentPrice} />
              </Col>
              <Col span={6}>
                <Statistic
                  title="日涨跌"
                  value={assetData?.change}
                  valueStyle={{ color: assetData?.change > 0 ? '#3f8600' : '#cf1322' }}
                />
              </Col>
              <Col span={6}>
                <Statistic title="成交量" value={assetData?.volume} />
              </Col>
              <Col span={6}>
                <Statistic title="市值" value={assetData?.marketCap} />
              </Col>
            </Row>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={16}>
          <Card title="价格走势">
            <PriceChart symbol={symbol} />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="技术指标">
            <TechnicalIndicators symbol={symbol} />
          </Card>
        </Col>
      </Row>

      <Row style={{ marginTop: 16 }}>
        <Col span={24}>
          <Card title="风险分析">
            <RiskMetrics symbol={symbol} />
          </Card>
        </Col>
      </Row>
    </div>
  )
}
```

### 3. **关键通用组件设计**

```typescript
// src/components/PriceChart.tsx
import React, { useEffect, useRef } from 'react'
import { Line } from 'react-chartjs-2'
import { useWebSocket } from '../hooks/useWebSocket'

interface PriceChartProps {
  symbol: string
  timeframe?: string
  height?: number
}

const PriceChart: React.FC<PriceChartProps> = ({
  symbol,
  timeframe = '1D',
  height = 300
}) => {
  const chartRef = useRef<any>(null)
  const { data: realtimeData } = useWebSocket(`/ws/realtime/${symbol}`)

  const chartData = {
    labels: [], // 时间标签
    datasets: [
      {
        label: '价格',
        data: [], // 价格数据
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.1
      }
    ]
  }

  useEffect(() => {
    if (realtimeData) {
      updateChartWithRealTimeData(realtimeData)
    }
  }, [realtimeData])

  return (
    <div className="price-chart">
      <Line ref={chartRef} data={chartData} height={height} />
    </div>
  )
}
```

```typescript
// src/components/OpportunityCard.tsx
import React from 'react'
import { Card, Tag, Button, Space } from 'antd'
import { Opportunity } from '../types/opportunity'

interface OpportunityCardProps {
  opportunity: Opportunity
  onTrack?: (opportunity: Opportunity) => void
  onIgnore?: (opportunity: Opportunity) => void
}

const OpportunityCard: React.FC<OpportunityCardProps> = ({
  opportunity,
  onTrack,
  onIgnore
}) => {
  const getOpportunityTypeColor = (type: string) => {
    const colors = {
      'breakout': 'green',
      'oversold': 'blue',
      'volume_surge': 'orange',
      'volatility': 'purple'
    }
    return colors[type] || 'default'
  }

  return (
    <Card
      size="small"
      title={
        <Space>
          <Tag color={getOpportunityTypeColor(opportunity.type)}>
            {opportunity.type}
          </Tag>
          {opportunity.symbol}
        </Space>
      }
      extra={
        <Space>
          <Button size="small" onClick={() => onTrack?.(opportunity)}>
            跟踪
          </Button>
          <Button size="small" type="text" onClick={() => onIgnore?.(opportunity)}>
            忽略
          </Button>
        </Space>
      }
    >
      <p>{opportunity.description}</p>
      <div className="opportunity-metrics">
        <span>置信度: {(opportunity.confidence * 100).toFixed(1)}%</span>
        <span>预期收益: {opportunity.expectedReturn?.toFixed(2)}%</span>
        <span>风险等级: {opportunity.riskLevel}</span>
      </div>
    </Card>
  )
}
```

### 4. **路由配置**

```typescript
// src/App.tsx
import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import Dashboard from './pages/Dashboard'
import Assets from './pages/Assets'
import AssetDetail from './pages/Assets/AssetDetail'
import Opportunities from './pages/Opportunities'
import RiskAnalysis from './pages/RiskAnalysis'

const { Content } = Layout

const App: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Content>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/assets" element={<Assets />} />
            <Route path="/assets/:symbol" element={<AssetDetail />} />
            <Route path="/opportunities" element={<Opportunities />} />
            <Route path="/risk" element={<RiskAnalysis />} />
          </Routes>
        </Content>
      </Layout>
    </Router>
  )
}
```

## PostgreSQL 优势利用

### 窗口函数示例
```sql
-- 计算移动平均和收益率
CREATE VIEW stock_analysis AS
SELECT
    symbol,
    date,
    close_price,
    AVG(close_price) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) as ma20,
    AVG(close_price) OVER (PARTITION BY symbol ORDER BY date ROWS BETWEEN 49 PRECEDING AND CURRENT ROW) as ma50,
    (close_price - LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date)) / LAG(close_price, 1) OVER (PARTITION BY symbol ORDER BY date) as daily_return
FROM stock_prices;
```

### JSONB 查询示例
```sql
-- 查询特定技术指标
SELECT * FROM technical_indicators
WHERE indicators->>'rsi' > '70'
  AND date = CURRENT_DATE;

-- 更新期权希腊字母
UPDATE options_chain
SET greeks = jsonb_set(greeks, '{delta}', '0.65'::jsonb)
WHERE symbol = 'AAPL' AND expiration = '2024-12-20';
```

### 索引策略
```sql
-- 复合索引
CREATE INDEX idx_stock_prices_symbol_date ON stock_prices(symbol, date DESC);
CREATE INDEX idx_portfolios_user_active ON portfolios(user_id, is_active);

-- JSONB 索引
CREATE INDEX idx_technical_indicators_rsi ON technical_indicators USING GIN ((indicators->'rsi'));
```

## 📁 项目结构

### **微服务目录结构**
```
investwin/
├── frontend/                 # React 前端应用
│   ├── src/
│   │   ├── components/     # UI组件
│   │   ├── pages/          # 页面组件
│   │   ├── services/       # API服务
│   │   └── store/          # 状态管理
│   └── package.json
├── web-service/             # Web API服务 (Port: 8000)
│   ├── app/
│   │   ├── api/            # API路由层
│   │   │   ├── auth/       # 认证相关
│   │   │   ├── assets/     # 资产管理
│   │   │   └── portfolios/ # 投资组合
│   │   ├── auth/           # 认证模块
│   │   ├── models/         # 数据模型
│   │   ├── client.py       # 业务服务客户端
│   │   └── main.py         # Web服务入口
│   └── requirements.txt
├── business-service/        # 业务逻辑服务 (Port: 8001)
│   ├── app/
│   │   ├── services/       # 业务服务层
│   │   │   ├── analysis/   # 分析服务
│   │   │   │   ├── technical/  # 技术分析
│   │   │   │   ├── fundamental/ # 基本面分析
│   │   │   │   └── sentiment/   # 情绪分析
│   │   │   ├── risk/        # 风险评估
│   │   │   └── opportunity/ # 机会挖掘
│   │   ├── algorithms/     # 算法模块
│   │   │   ├── indicators/  # 技术指标
│   │   │   ├── patterns/    # 形态识别
│   │   │   └── optimization/ # 组合优化
│   │   ├── models/         # 业务模型
│   │   └── main.py         # 业务服务入口
│   └── requirements.txt
├── shared/                   # 共享代码
│   ├── models/              # 共享数据模型
│   ├── utils/               # 共享工具函数
│   └── config/              # 配置文件
└── docker-compose.yml       # 容器编排配置
```

## 📡 服务间通信

### **通信架构**
```mermaid
sequenceDiagram
    participant Frontend
    participant WebService
    participant BusinessService
    participant Database
    participant Cache

    Frontend->>WebService: HTTP请求 (API调用)
    WebService->>WebService: 用户认证/参数验证
    WebService->>BusinessService: HTTP调用 (业务逻辑)
    BusinessService->>Cache: 检查缓存数据
    alt 缓存命中
        Cache-->>BusinessService: 返回缓存数据
    else 缓存未命中
        BusinessService->>Database: 查询/计算数据
        Database-->>BusinessService: 返回原始数据
        BusinessService->>BusinessService: 业务逻辑处理
        BusinessService->>Cache: 存储计算结果
    end
    BusinessService-->>WebService: 返回业务结果
    WebService-->>Frontend: JSON响应
```

### **API 设计示例**

#### **Web Service API (面向前端)**
```python
# web-service/api/opportunities.py
@router.get("/assets/{symbol}/opportunities")
async def get_asset_opportunities(symbol: str, current_user: User = Depends(get_current_user)):
    """获取资产投资机会"""
    # 调用业务服务
    opportunities = await business_client.get_opportunities(symbol)

    return {
        "symbol": symbol,
        "opportunities": opportunities,
        "user_id": current_user.id,
        "timestamp": datetime.now()
    }
```

#### **Business Service API (内部服务)**
```python
# business-service/services/opportunity.py
@router.get("/opportunities/{symbol}")
async def analyze_opportunities(symbol: str):
    """分析投资机会（内部API）"""
    # 检查缓存
    cache_key = f"opportunities:{symbol}"
    cached_result = await cache.get(cache_key)
    if cached_result:
        return cached_result

    # 执行分析
    opportunities = await opportunity_service.find_all_opportunities(symbol)

    # 缓存结果
    await cache.set(cache_key, opportunities, expire=300)  # 5分钟缓存

    return opportunities
```

## 🐳 部署配置

### **Docker Compose 配置**
```yaml
version: '3.8'
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - web-service
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  web-service:
    build: ./web-service
    ports:
      - "8000:8000"
    depends_on:
      - business-service
      - postgres
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/investwin
      - BUSINESS_SERVICE_URL=http://business-service:8001

  business-service:
    build: ./business-service
    ports:
      - "8001:8001"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://user:password@postgres:5432/investwin
      - REDIS_URL=redis://redis:6379

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: investwin
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 🔧 开发环境

### **本地开发启动顺序**
1. **启动基础服务**：
   ```bash
   docker-compose up postgres redis -d
   ```

2. **启动业务服务**：
   ```bash
   cd business-service
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app/main.py  # Port: 8001
   ```

3. **启动Web服务**：
   ```bash
   cd web-service
   source venv/bin/activate
   pip install -r requirements.txt
   python app/main.py   # Port: 8000
   ```

4. **启动前端**：
   ```bash
   cd frontend
   npm start           # Port: 3000
   ```

## 🚀 开发优势

### **微服务架构优势**
1. **服务独立**：Web和业务服务独立开发、测试、部署
2. **技术灵活**：不同服务可以使用不同的技术栈
3. **可扩展性**：可以根据负载独立扩展特定服务
4. **容错性好**：单个服务故障不影响整个系统
5. **团队协作**：不同团队可以并行开发不同服务

### **投资平台优势**
6. **前后端分离**：React前端与Python后端完全分离
7. **实时数据**：WebSocket支持毫秒级数据更新
8. **智能分析**：基于算法的机会自动识别
9. **风险可控**：多层次风险监控和预警
10. **专业分析**：技术面、资金面、衍生品全覆盖

## 📚 API接口设计

### **Web Service API (面向前端)**
- `POST /api/auth/login` - 用户登录
- `GET /api/assets/` - 资产列表管理
- `GET /api/assets/{symbol}/analysis` - 资产分析结果
- `GET /api/opportunities/` - 投资机会列表
- `GET /api/risk/portfolio` - 组合风险评估
- `WebSocket /ws/realtime/` - 实时数据推送

### **Business Service API (内部服务)**
- `GET /analysis/technical/{symbol}` - 技术分析
- `GET /analysis/fundamental/{symbol}` - 基本面分析
- `GET /risk/assessment/{symbol}` - 风险评估
- `GET /opportunities/scan/{symbol}` - 机会扫描
- `POST /portfolio/optimize` - 组合优化

### **功能特点**
- RESTful API设计，统一响应格式
- JWT认证，权限控制
- 服务间通信，异步处理
- 缓存策略，性能优化
- 自动生成API文档
- 完整的错误处理机制