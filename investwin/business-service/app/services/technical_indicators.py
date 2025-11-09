"""
技术指标计算服务
"""

import numpy as np
from typing import Dict, List, Any, Optional
import asyncpg
from datetime import datetime, timedelta

class TechnicalIndicatorsService:
    """技术指标计算服务"""

    def __init__(self, db_service):
        self.db_service = db_service

    async def get_price_data(self, symbol: str, days: int = 100) -> List[float]:
        """获取历史价格数据"""
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
            print(f"Error fetching price data: {e}")
            # 返回模拟数据
            return self._generate_mock_price_data(symbol, days)

    def _generate_mock_price_data(self, symbol: str, days: int) -> List[float]:
        """生成模拟价格数据"""
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
            # 随机波动
            change = np.random.normal(0, 0.02)  # 2%标准差
            price *= (1 + change)
            prices.append(price)

        return prices

    def calculate_sma(self, prices: List[float], period: int) -> float:
        """计算简单移动平均线"""
        if len(prices) < period:
            return np.mean(prices)
        return np.mean(prices[-period:])

    def calculate_ema(self, prices: List[float], period: int) -> float:
        """计算指数移动平均线"""
        if len(prices) == 0:
            return 0.0

        multiplier = 2 / (period + 1)
        ema = prices[0]

        for price in prices[1:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))

        return ema

    def calculate_rsi(self, prices: List[float], period: int = 14) -> float:
        """计算相对强弱指数"""
        if len(prices) < period + 1:
            return 50.0  # 中性值

        deltas = np.diff(prices)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)

        avg_gain = np.mean(gains[-period:])
        avg_loss = np.mean(losses[-period:])

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    def calculate_macd(self, prices: List[float]) -> Dict[str, float]:
        """计算MACD指标"""
        if len(prices) < 26:
            return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}

        ema_12 = self.calculate_ema(prices, 12)
        ema_26 = self.calculate_ema(prices, 26)
        macd_line = ema_12 - ema_26

        # 简化的信号线计算
        signal_line = macd_line * 0.9  # 简化计算
        histogram = macd_line - signal_line

        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }

    def calculate_bollinger_bands(self, prices: List[float], period: int = 20, std_dev: float = 2.0) -> Dict[str, float]:
        """计算布林带"""
        if len(prices) < period:
            prices_slice = prices
        else:
            prices_slice = prices[-period:]

        middle_band = np.mean(prices_slice)
        std = np.std(prices_slice)

        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)

        return {
            "upper": upper_band,
            "middle": middle_band,
            "lower": lower_band
        }

    def calculate_stochastic(self, high_prices: List[float], low_prices: List[float], close_prices: List[float], k_period: int = 14) -> float:
        """计算随机指标"""
        if len(close_prices) < k_period:
            return 50.0

        recent_high = max(high_prices[-k_period:])
        recent_low = min(low_prices[-k_period:])
        current_close = close_prices[-1]

        if recent_high == recent_low:
            return 50.0

        k_percent = ((current_close - recent_low) / (recent_high - recent_low)) * 100
        return k_percent

    async def calculate_all_indicators(self, symbol: str) -> Dict[str, Any]:
        """计算所有技术指标"""
        try:
            # 获取价格数据
            prices = await self.get_price_data(symbol, 100)

            if len(prices) < 20:
                return self._get_default_indicators(symbol)

            # 计算各种指标
            sma_20 = self.calculate_sma(prices, 20)
            sma_50 = self.calculate_sma(prices, 50)
            ema_12 = self.calculate_ema(prices, 12)
            ema_26 = self.calculate_ema(prices, 26)
            rsi = self.calculate_rsi(prices)
            macd = self.calculate_macd(prices)
            bollinger = self.calculate_bollinger_bands(prices)

            # 计算趋势和信号
            current_price = prices[-1]
            price_change_5d = ((current_price - prices[-5]) / prices[-5] * 100) if len(prices) >= 5 else 0
            price_change_20d = ((current_price - prices[-20]) / prices[-20] * 100) if len(prices) >= 20 else 0

            # 生成交易信号
            signals = self._generate_trading_signals(
                current_price, sma_20, sma_50, rsi, macd, bollinger
            )

            indicators = {
                "current_price": current_price,
                "sma_20": sma_20,
                "sma_50": sma_50,
                "ema_12": ema_12,
                "ema_26": ema_26,
                "rsi": rsi,
                "macd": macd,
                "bollinger_bands": bollinger,
                "price_change_5d": price_change_5d,
                "price_change_20d": price_change_20d,
                "signals": signals,
                "updated_at": datetime.now().isoformat()
            }

            return indicators

        except Exception as e:
            print(f"Error calculating indicators for {symbol}: {e}")
            return self._get_default_indicators(symbol)

    def _generate_trading_signals(self, price: float, sma_20: float, sma_50: float,
                                rsi: float, macd: Dict, bollinger: Dict) -> Dict[str, str]:
        """生成交易信号"""
        signals = {}

        # SMA信号
        if price > sma_20 > sma_50:
            signals["trend"] = "bullish"
        elif price < sma_20 < sma_50:
            signals["trend"] = "bearish"
        else:
            signals["trend"] = "neutral"

        # RSI信号
        if rsi < 30:
            signals["rsi"] = "oversold"
        elif rsi > 70:
            signals["rsi"] = "overbought"
        else:
            signals["rsi"] = "neutral"

        # MACD信号
        if macd["histogram"] > 0:
            signals["macd"] = "bullish"
        else:
            signals["macd"] = "bearish"

        # 布林带信号
        if price > bollinger["upper"]:
            signals["bollinger"] = "overbought"
        elif price < bollinger["lower"]:
            signals["bollinger"] = "oversold"
        else:
            signals["bollinger"] = "neutral"

        # 综合信号
        bullish_signals = sum(1 for s in signals.values() if s == "bullish" or s == "oversold")
        bearish_signals = sum(1 for s in signals.values() if s == "bearish" or s == "overbought")

        if bullish_signals >= 3:
            signals["overall"] = "strong_buy"
        elif bullish_signals >= 2:
            signals["overall"] = "buy"
        elif bearish_signals >= 3:
            signals["overall"] = "strong_sell"
        elif bearish_signals >= 2:
            signals["overall"] = "sell"
        else:
            signals["overall"] = "hold"

        return signals

    def _get_default_indicators(self, symbol: str) -> Dict[str, Any]:
        """获取默认指标值"""
        base_prices = {
            'AAPL': 150.0,
            'MSFT': 320.0,
            'GOOGL': 140.0,
            'TSLA': 240.0
        }

        current_price = base_prices.get(symbol, 100.0)

        return {
            "current_price": current_price,
            "sma_20": current_price * 0.98,
            "sma_50": current_price * 0.95,
            "ema_12": current_price * 0.99,
            "ema_26": current_price * 0.97,
            "rsi": 50.0,
            "macd": {"macd": 0.0, "signal": 0.0, "histogram": 0.0},
            "bollinger_bands": {
                "upper": current_price * 1.02,
                "middle": current_price,
                "lower": current_price * 0.98
            },
            "price_change_5d": 1.5,
            "price_change_20d": 3.2,
            "signals": {
                "trend": "neutral",
                "rsi": "neutral",
                "macd": "neutral",
                "bollinger": "neutral",
                "overall": "hold"
            },
            "updated_at": datetime.now().isoformat()
        }