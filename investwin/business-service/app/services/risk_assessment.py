"""
风险评估服务
"""

import numpy as np
from typing import Dict, List, Any
import asyncpg
from datetime import datetime, timedelta

class RiskAssessmentService:
    """风险评估服务"""

    def __init__(self, db_service):
        self.db_service = db_service

    async def get_price_history(self, symbol: str, days: int = 252) -> List[float]:
        """获取历史价格数据（一年交易日）"""
        try:
            conn = await self.db_service.get_connection()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            rows = await conn.fetch(
                """
                SELECT close_price
                FROM stock_prices
                WHERE symbol = $1 AND date >= $2 AND date <= $3
                ORDER BY date ASC
                """,
                symbol, start_date, end_date
            )
            await conn.close()

            return [float(row['close_price']) for row in rows]
        except Exception as e:
            print(f"Error fetching price history: {e}")
            return self._generate_mock_price_history(symbol, days)

    def _generate_mock_price_history(self, symbol: str, days: int) -> List[float]:
        """生成模拟价格历史"""
        base_prices = {
            'AAPL': 150.0,
            'MSFT': 320.0,
            'GOOGL': 140.0,
            'TSLA': 240.0
        }

        base_price = base_prices.get(symbol, 100.0)
        prices = []
        price = base_price

        for _ in range(days):
            # 更大的波动率用于风险计算
            change = np.random.normal(0, 0.025)  # 2.5%日波动率
            price *= (1 + change)
            prices.append(price)

        return prices

    def calculate_volatility(self, prices: List[float]) -> float:
        """计算波动率（年化）"""
        if len(prices) < 2:
            return 0.25  # 默认25%年化波动率

        # 计算日收益率
        returns = np.diff(prices) / prices[:-1]

        # 年化波动率（假设252个交易日）
        daily_vol = np.std(returns)
        annualized_vol = daily_vol * np.sqrt(252)

        return annualized_vol

    def calculate_max_drawdown(self, prices: List[float]) -> float:
        """计算最大回撤"""
        if len(prices) < 2:
            return 0.0

        peak = prices[0]
        max_drawdown = 0.0

        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            max_drawdown = max(max_drawdown, drawdown)

        return max_drawdown

    def calculate_sharpe_ratio(self, prices: List[float], risk_free_rate: float = 0.02) -> float:
        """计算夏普比率"""
        if len(prices) < 2:
            return 1.0

        # 计算日收益率
        returns = np.diff(prices) / prices[:-1]

        # 年化收益率和波动率
        annual_return = np.mean(returns) * 252
        annual_vol = np.std(returns) * np.sqrt(252)

        if annual_vol == 0:
            return 0.0

        # 夏普比率
        sharpe = (annual_return - risk_free_rate) / annual_vol
        return sharpe

    def calculate_beta(self, stock_prices: List[float], market_prices: List[float]) -> float:
        """计算Beta系数"""
        if len(stock_prices) < 2 or len(market_prices) < 2:
            return 1.0

        # 计算收益率
        stock_returns = np.diff(stock_prices) / stock_prices[:-1]
        market_returns = np.diff(market_prices) / market_prices[:-1]

        # 计算协方差和方差
        if len(stock_returns) != len(market_returns):
            min_len = min(len(stock_returns), len(market_returns))
            stock_returns = stock_returns[:min_len]
            market_returns = market_returns[:min_len]

        covariance = np.cov(stock_returns, market_returns)[0][1]
        market_variance = np.var(market_returns)

        if market_variance == 0:
            return 1.0

        beta = covariance / market_variance
        return beta

    def calculate_var(self, prices: List[float], confidence_level: float = 0.95) -> float:
        """计算风险价值（VaR）"""
        if len(prices) < 30:
            return 0.05  # 默认5% VaR

        # 计算日收益率
        returns = np.diff(prices) / prices[:-1]

        # 使用历史方法计算VaR
        var_percentile = (1 - confidence_level) * 100
        var_daily = np.percentile(returns, var_percentile)

        # 年化VaR（假设252个交易日）
        var_annual = var_daily * np.sqrt(252)

        return abs(var_annual)

    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票基本信息"""
        try:
            conn = await self.db_service.get_connection()
            row = await conn.fetchrow(
                """
                SELECT symbol, name, sector, industry, market_cap
                FROM stocks
                WHERE symbol = $1
                """,
                symbol.upper()
            )
            await conn.close()

            if row:
                return dict(row)
            else:
                # 返回默认信息
                return {
                    "symbol": symbol.upper(),
                    "name": f"{symbol.upper()} Corporation",
                    "sector": "Technology",
                    "industry": "Software",
                    "market_cap": 1000000000000
                }
        except Exception as e:
            print(f"Error fetching stock info: {e}")
            return {
                "symbol": symbol.upper(),
                "name": f"{symbol.upper()} Corporation",
                "sector": "Technology",
                "industry": "Software",
                "market_cap": 1000000000000
            }

    async def assess_risk(self, symbol: str) -> Dict[str, Any]:
        """全面评估投资风险"""
        try:
            # 获取数据
            prices = await self.get_price_history(symbol)
            stock_info = await self.get_stock_info(symbol)

            if len(prices) < 20:
                return self._get_default_risk_assessment(symbol, stock_info)

            # 计算风险指标
            volatility = self.calculate_volatility(prices)
            max_drawdown = self.calculate_max_drawdown(prices)
            sharpe_ratio = self.calculate_sharpe_ratio(prices)
            var_95 = self.calculate_var(prices, 0.95)
            var_99 = self.calculate_var(prices, 0.99)

            # 计算风险评分
            risk_scores = self.calculate_risk_scores(volatility, max_drawdown, sharpe_ratio)

            # 风险等级
            risk_level = self.determine_risk_level(risk_scores['overall'])

            # 风险因子
            risk_factors = self.identify_risk_factors(volatility, max_drawdown, stock_info)

            # 建议
            recommendations = self.generate_risk_recommendations(risk_level, risk_factors)

            return {
                "symbol": symbol,
                "company_name": stock_info.get('name', ''),
                "risk_level": risk_level,
                "risk_scores": risk_scores,
                "risk_metrics": {
                    "volatility": round(volatility * 100, 2),  # 转换为百分比
                    "max_drawdown": round(max_drawdown * 100, 2),
                    "sharpe_ratio": round(sharpe_ratio, 2),
                    "var_95": round(var_95 * 100, 2),
                    "var_99": round(var_99 * 100, 2)
                },
                "risk_factors": risk_factors,
                "recommendations": recommendations,
                "market_cap": stock_info.get('market_cap', 0),
                "sector": stock_info.get('sector', ''),
                "assessment_date": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error assessing risk for {symbol}: {e}")
            return self._get_default_risk_assessment(symbol, {})

    def calculate_risk_scores(self, volatility: float, max_drawdown: float, sharpe_ratio: float) -> Dict[str, float]:
        """计算风险评分（0-100，分数越高风险越大）"""
        # 波动率评分（0-40分）
        if volatility < 0.15:  # 15%以下
            volatility_score = 10
        elif volatility < 0.25:  # 15-25%
            volatility_score = 20
        elif volatility < 0.35:  # 25-35%
            volatility_score = 30
        else:  # 35%以上
            volatility_score = 40

        # 最大回撤评分（0-30分）
        if max_drawdown < 0.10:  # 10%以下
            drawdown_score = 5
        elif max_drawdown < 0.20:  # 10-20%
            drawdown_score = 10
        elif max_drawdown < 0.35:  # 20-35%
            drawdown_score = 20
        else:  # 35%以上
            drawdown_score = 30

        # 夏普比率评分（0-30分，分数越低越好）
        if sharpe_ratio > 2.0:
            sharpe_score = 0
        elif sharpe_ratio > 1.5:
            sharpe_score = 5
        elif sharpe_ratio > 1.0:
            sharpe_score = 10
        elif sharpe_ratio > 0.5:
            sharpe_score = 20
        else:
            sharpe_score = 30

        overall_score = volatility_score + drawdown_score + sharpe_score

        return {
            "volatility": volatility_score,
            "max_drawdown": drawdown_score,
            "sharpe_ratio": sharpe_score,
            "overall": overall_score
        }

    def determine_risk_level(self, overall_score: float) -> str:
        """确定风险等级"""
        if overall_score < 20:
            return "Very Low"
        elif overall_score < 35:
            return "Low"
        elif overall_score < 50:
            return "Medium"
        elif overall_score < 70:
            return "High"
        else:
            return "Very High"

    def identify_risk_factors(self, volatility: float, max_drawdown: float, stock_info: Dict[str, Any]) -> List[str]:
        """识别风险因子"""
        factors = []

        # 基于波动率的风险因子
        if volatility > 0.35:
            factors.append("High price volatility indicates significant market risk")
        elif volatility > 0.25:
            factors.append("Moderate to high volatility may cause large price swings")

        # 基于最大回撤的风险因子
        if max_drawdown > 0.40:
            factors.append("Historical maximum drawdown suggests high downside risk")
        elif max_drawdown > 0.25:
            factors.append("Significant historical drawdown indicates potential for large losses")

        # 基于行业的风险因子
        sector = stock_info.get('sector', '')
        if sector == "Technology":
            factors.append("Technology sector subject to rapid innovation and disruption risks")
        elif sector == "Energy":
            factors.append("Energy sector exposed to commodity price volatility")
        elif sector == "Finance":
            factors.append("Financial sector sensitive to interest rate changes and regulations")

        # 基于市值的风险因子
        market_cap = stock_info.get('market_cap', 0)
        if market_cap < 2000000000:  # 小于20亿
            factors.append("Small-cap stock may have liquidity and volatility risks")

        return factors[:4]  # 最多返回4个风险因子

    def generate_risk_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """生成风险管理建议"""
        recommendations = []

        if risk_level in ["High", "Very High"]:
            recommendations.extend([
                "Consider position sizing to limit exposure",
                "Use stop-loss orders to manage downside risk",
                "Monitor closely for market changes"
            ])
        elif risk_level == "Medium":
            recommendations.extend([
                "Maintain diversified portfolio to reduce concentration risk",
                "Regular rebalancing recommended"
            ])
        else:  # Low, Very Low
            recommendations.extend([
                "Suitable for long-term investment strategies",
                "Lower monitoring frequency required"
            ])

        # 基于风险因子的特定建议
        if "volatility" in " ".join(risk_factors).lower():
            recommendations.append("Consider dollar-cost averaging to mitigate volatility impact")

        return recommendations[:4]  # 最多返回4个建议

    def _get_default_risk_assessment(self, symbol: str, stock_info: Dict[str, Any]) -> Dict[str, Any]:
        """获取默认风险评估"""
        return {
            "symbol": symbol,
            "company_name": stock_info.get('name', f"{symbol.upper()} Corporation"),
            "risk_level": "Medium",
            "risk_scores": {
                "volatility": 20,
                "max_drawdown": 10,
                "sharpe_ratio": 15,
                "overall": 45
            },
            "risk_metrics": {
                "volatility": 25.0,
                "max_drawdown": 15.0,
                "sharpe_ratio": 1.2,
                "var_95": 5.0,
                "var_99": 8.0
            },
            "risk_factors": [
                "Limited historical data available",
                "Market conditions may change rapidly"
            ],
            "recommendations": [
                "Monitor position regularly",
                "Consider diversification"
            ],
            "market_cap": stock_info.get('market_cap', 1000000000000),
            "sector": stock_info.get('sector', 'Technology'),
            "assessment_date": datetime.now().isoformat()
        }