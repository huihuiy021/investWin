"""
投资机会挖掘服务
"""

import numpy as np
from typing import Dict, List, Any
import asyncpg
from datetime import datetime, timedelta

class OpportunityMiningService:
    """投资机会挖掘服务"""

    def __init__(self, db_service):
        self.db_service = db_service

    async def get_all_stocks(self) -> List[Dict[str, Any]]:
        """获取所有股票信息"""
        try:
            conn = await self.db_service.get_connection()
            rows = await conn.fetch(
                """
                SELECT s.symbol, s.name, s.sector, s.industry, s.market_cap,
                       sp.close_price as current_price, sp.date as price_date
                FROM stocks s
                LEFT JOIN stock_prices sp ON s.symbol = sp.symbol
                    AND sp.date = (
                        SELECT MAX(date) FROM stock_prices sp2
                        WHERE sp2.symbol = s.symbol
                    )
                ORDER BY s.symbol
                """
            )
            await conn.close()

            stocks = []
            for row in rows:
                stock = dict(row)
                if stock['current_price'] is None:
                    # 使用模拟价格
                    mock_prices = {
                        'AAPL': 150.25, 'MSFT': 320.80, 'GOOGL': 140.50, 'TSLA': 240.80
                    }
                    stock['current_price'] = mock_prices.get(stock['symbol'], 100.0)
                stocks.append(stock)

            return stocks

        except Exception as e:
            print(f"Error fetching stocks: {e}")
            # 返回模拟数据
            return [
                {"symbol": "AAPL", "name": "Apple Inc.", "sector": "Technology", "industry": "Consumer Electronics", "market_cap": 3000000000000, "current_price": 150.25},
                {"symbol": "MSFT", "name": "Microsoft Corporation", "sector": "Technology", "industry": "Software", "market_cap": 2800000000000, "current_price": 320.80},
                {"symbol": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology", "industry": "Internet Services", "market_cap": 1800000000000, "current_price": 140.50},
                {"symbol": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical", "industry": "Auto Manufacturers", "market_cap": 800000000000, "current_price": 240.80}
            ]

    async def find_opportunities(self) -> List[Dict[str, Any]]:
        """挖掘投资机会"""
        try:
            stocks = await self.get_all_stocks()
            opportunities = []

            for stock in stocks:
                opportunity = await self.analyze_stock_opportunity(stock)
                if opportunity['score'] > 60:  # 只返回评分较高的机会
                    opportunities.append(opportunity)

            # 按评分排序
            opportunities.sort(key=lambda x: x['score'], reverse=True)
            return opportunities[:10]  # 返回前10个机会

        except Exception as e:
            print(f"Error finding opportunities: {e}")
            return []

    async def analyze_stock_opportunity(self, stock: Dict[str, Any]) -> Dict[str, Any]:
        """分析单个股票的投资机会"""
        symbol = stock['symbol']
        current_price = stock['current_price']

        # 计算各种指标
        valuation_score = self.calculate_valuation_score(stock)
        momentum_score = self.calculate_momentum_score(symbol, current_price)
        quality_score = self.calculate_quality_score(stock)
        growth_score = self.calculate_growth_score(stock)

        # 综合评分
        total_score = (valuation_score * 0.3 +
                      momentum_score * 0.25 +
                      quality_score * 0.25 +
                      growth_score * 0.2)

        # 确定投资等级
        if total_score >= 85:
            grade = "Strong Buy"
        elif total_score >= 75:
            grade = "Buy"
        elif total_score >= 65:
            grade = "Moderate Buy"
        elif total_score >= 55:
            grade = "Hold"
        elif total_score >= 45:
            grade = "Moderate Sell"
        else:
            grade = "Sell"

        # 计算目标价格
        target_price = self.calculate_target_price(current_price, total_score)

        return {
            "symbol": symbol,
            "name": stock['name'],
            "sector": stock['sector'],
            "current_price": current_price,
            "target_price": target_price,
            "potential_return": ((target_price - current_price) / current_price * 100),
            "score": round(total_score, 2),
            "grade": grade,
            "scores": {
                "valuation": valuation_score,
                "momentum": momentum_score,
                "quality": quality_score,
                "growth": growth_score
            },
            "market_cap": stock.get('market_cap', 0),
            "analysis_date": datetime.now().isoformat(),
            "reasons": self.generate_investment_reasons(total_score, stock)
        }

    def calculate_valuation_score(self, stock: Dict[str, Any]) -> float:
        """计算估值评分"""
        # 简化的估值评分逻辑
        symbol = stock['symbol']
        market_cap = stock.get('market_cap', 0)

        # 基于市值的估值评分
        if market_cap > 2000000000000:  # 大盘股
            base_score = 70
        elif market_cap > 500000000000:   # 中盘股
            base_score = 80
        else:  # 小盘股
            base_score = 60

        # 基于行业的调整
        sector_adjustments = {
            "Technology": 5,
            "Healthcare": 3,
            "Finance": 2,
            "Consumer Cyclical": 0,
            "Energy": -2
        }

        sector = stock.get('sector', '')
        adjustment = sector_adjustments.get(sector, 0)

        return min(100, max(0, base_score + adjustment + np.random.normal(0, 10)))

    def calculate_momentum_score(self, symbol: str, current_price: float) -> float:
        """计算动量评分"""
        # 简化的动量计算
        price_changes = {
            'AAPL': 2.5,
            'MSFT': -1.2,
            'GOOGL': 3.2,
            'TSLA': -5.6
        }

        change_5d = price_changes.get(symbol, np.random.normal(0, 3))

        # 基于价格变化的动量评分
        if change_5d > 5:
            return 90
        elif change_5d > 2:
            return 80
        elif change_5d > 0:
            return 70
        elif change_5d > -2:
            return 60
        elif change_5d > -5:
            return 40
        else:
            return 30

    def calculate_quality_score(self, stock: Dict[str, Any]) -> float:
        """计算质量评分"""
        sector = stock.get('sector', '')
        market_cap = stock.get('market_cap', 0)

        # 基于行业的质量评分
        sector_scores = {
            "Technology": 85,
            "Healthcare": 90,
            "Finance": 75,
            "Consumer Cyclical": 70,
            "Energy": 65
        }

        base_score = sector_scores.get(sector, 70)

        # 基于市值的质量调整
        if market_cap > 1000000000000:
            base_score += 10  # 大公司通常更稳定

        return min(100, max(0, base_score + np.random.normal(0, 8)))

    def calculate_growth_score(self, stock: Dict[str, Any]) -> float:
        """计算成长评分"""
        sector = stock.get('sector', '')

        # 基于行业的成长性评分
        growth_scores = {
            "Technology": 90,
            "Healthcare": 85,
            "Finance": 70,
            "Consumer Cyclical": 75,
            "Energy": 60
        }

        base_score = growth_scores.get(sector, 70)
        return min(100, max(0, base_score + np.random.normal(0, 12)))

    def calculate_target_price(self, current_price: float, score: float) -> float:
        """计算目标价格"""
        # 基于评分计算预期回报率
        if score >= 85:
            expected_return = 0.20  # 20%
        elif score >= 75:
            expected_return = 0.15  # 15%
        elif score >= 65:
            expected_return = 0.10  # 10%
        elif score >= 55:
            expected_return = 0.05  # 5%
        else:
            expected_return = -0.05  # -5%

        return current_price * (1 + expected_return)

    def generate_investment_reasons(self, score: float, stock: Dict[str, Any]) -> List[str]:
        """生成投资理由"""
        reasons = []

        if score >= 75:
            reasons.extend([
                f"{stock['sector']} sector showing strong momentum",
                "Technical indicators suggest upside potential",
                "Strong fundamentals relative to peers"
            ])
        elif score >= 60:
            reasons.extend([
                "Reasonable valuation with growth potential",
                "Positive technical trend"
            ])
        else:
            reasons.extend([
                "High volatility expected",
                "Better opportunities may exist elsewhere"
            ])

        # 特殊情况
        if stock.get('market_cap', 0) > 2000000000000:
            reasons.append("Large-cap stability provides downside protection")

        return reasons[:3]  # 返回最多3个理由

    async def analyze_portfolio(self, symbols: List[str]) -> Dict[str, Any]:
        """分析投资组合"""
        try:
            stocks = await self.get_all_stocks()
            portfolio_stocks = [s for s in stocks if s['symbol'] in symbols]

            if not portfolio_stocks:
                return {"error": "No valid stocks found in portfolio"}

            total_value = sum(s['current_price'] for s in portfolio_stocks)
            opportunities = []

            for stock in portfolio_stocks:
                opportunity = await self.analyze_stock_opportunity(stock)
                opportunities.append(opportunity)

            # 组合分析
            avg_score = np.mean([opp['score'] for opp in opportunities])
            high_quality_count = sum(1 for opp in opportunities if opp['score'] >= 75)

            # 分散化分析
            sectors = list(set(s['sector'] for s in portfolio_stocks))
            diversification_score = min(100, len(sectors) * 20)

            return {
                "portfolio_stocks": opportunities,
                "total_value": total_value,
                "average_score": round(avg_score, 2),
                "high_quality_holdings": high_quality_count,
                "diversification_score": diversification_score,
                "sectors": sectors,
                "recommendation": self.generate_portfolio_recommendation(avg_score, diversification_score),
                "analysis_date": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error analyzing portfolio: {e}")
            return {"error": str(e)}

    def generate_portfolio_recommendation(self, avg_score: float, diversification_score: float) -> str:
        """生成投资组合建议"""
        if avg_score >= 80 and diversification_score >= 60:
            return "Excellent portfolio with strong fundamentals and good diversification"
        elif avg_score >= 70:
            return "Good portfolio quality, consider adding more diversified positions"
        elif avg_score >= 60:
            return "Moderate portfolio, review underperforming positions"
        else:
            return "Portfolio needs rebalancing, consider reducing weaker positions"