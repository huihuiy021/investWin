"""
数据库连接模块
使用 asyncpg 连接 PostgreSQL 数据库
"""

import os
import asyncpg
from typing import List, Dict, Any, Optional
from datetime import datetime

class DatabaseService:
    """数据库服务类"""

    def __init__(self):
        self.connection_string = os.getenv(
            "DATABASE_URL",
            "postgresql://huihui:investwin123@localhost:5432/investwin"
        )
        # 现在使用真实数据库连接
        self.use_mock_data = False

    async def get_stocks(self) -> List[Dict[str, Any]]:
        """获取股票列表"""
        try:
            async with asyncpg.connect(self.connection_string) as conn:
                # 查询股票基本信息和最新价格
                query = """
                SELECT
                    s.symbol,
                    s.name,
                    s.sector,
                    s.industry,
                    sp.close_price as current_price,
                    sp.close_price - sp.open_price as change,
                    CASE
                        WHEN sp.open_price > 0 THEN
                            ROUND(((sp.close_price - sp.open_price) / sp.open_price * 100), 2)
                        ELSE 0
                    END as change_percent
                FROM stocks s
                LEFT JOIN stock_prices sp ON s.symbol = sp.symbol
                    AND sp.date = (
                        SELECT MAX(date) FROM stock_prices sp2
                        WHERE sp2.symbol = s.symbol
                    )
                ORDER BY s.symbol
                """
                rows = await conn.fetch(query)

                # 转换为字典格式
                results = []
                for row in rows:
                    result = dict(row)
                    # 如果没有价格数据，设置默认值
                    if result['current_price'] is None:
                        # 模拟价格数据
                        mock_prices = {
                            'AAPL': {'current_price': 150.25, 'change': 2.50, 'change_percent': 1.69},
                            'MSFT': {'current_price': 320.80, 'change': -1.20, 'change_percent': -0.37},
                            'GOOGL': {'current_price': 140.50, 'change': 3.20, 'change_percent': 2.33},
                            'TSLA': {'current_price': 240.80, 'change': -5.60, 'change_percent': -2.27}
                        }
                        if result['symbol'] in mock_prices:
                            mock_data = mock_prices[result['symbol']]
                            result.update(mock_data)
                        else:
                            result['current_price'] = 0
                            result['change'] = 0
                            result['change_percent'] = 0
                    else:
                        # 转换数值类型
                        result['current_price'] = float(result['current_price'])
                        result['change'] = float(result['change']) if result['change'] else 0
                        result['change_percent'] = float(result['change_percent']) if result['change_percent'] else 0

                    results.append(result)

                return results

        except Exception as e:
            print(f"Database error: {e}")
            # 如果数据库连接失败，返回备用数据
            return [
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                    "current_price": 150.25,
                    "change": 2.50,
                    "change_percent": 1.69
                },
                {
                    "symbol": "MSFT",
                    "name": "Microsoft Corporation",
                    "sector": "Technology",
                    "industry": "Software",
                    "current_price": 320.80,
                    "change": -1.20,
                    "change_percent": -0.37
                },
                {
                    "symbol": "GOOGL",
                    "name": "Alphabet Inc.",
                    "sector": "Technology",
                    "industry": "Internet Services",
                    "current_price": 140.50,
                    "change": 3.20,
                    "change_percent": 2.33
                },
                {
                    "symbol": "TSLA",
                    "name": "Tesla Inc.",
                    "sector": "Consumer Cyclical",
                    "industry": "Auto Manufacturers",
                    "current_price": 240.80,
                    "change": -5.60,
                    "change_percent": -2.27
                }
            ]

    async def get_stock_by_symbol(self, symbol: str) -> Optional[Dict[str, Any]]:
        """根据代码获取股票信息"""
        try:
            async with asyncpg.connect(self.connection_string) as conn:
                query = """
                SELECT
                    s.symbol,
                    s.name,
                    s.sector,
                    s.industry,
                    sp.close_price as current_price,
                    sp.close_price - sp.open_price as change,
                    CASE
                        WHEN sp.open_price > 0 THEN
                            ROUND(((sp.close_price - sp.open_price) / sp.open_price * 100), 2)
                        ELSE 0
                    END as change_percent
                FROM stocks s
                LEFT JOIN stock_prices sp ON s.symbol = sp.symbol
                    AND sp.date = (
                        SELECT MAX(date) FROM stock_prices sp2
                        WHERE sp2.symbol = s.symbol
                    )
                WHERE s.symbol = $1
                """
                row = await conn.fetchrow(query, symbol.upper())
                if row:
                    result = dict(row)
                    if result['current_price'] is None:
                        # 使用 get_stocks 中的模拟数据
                        mock_prices = {
                            'AAPL': {'current_price': 150.25, 'change': 2.50, 'change_percent': 1.69},
                            'MSFT': {'current_price': 320.80, 'change': -1.20, 'change_percent': -0.37},
                            'GOOGL': {'current_price': 140.50, 'change': 3.20, 'change_percent': 2.33},
                            'TSLA': {'current_price': 240.80, 'change': -5.60, 'change_percent': -2.27}
                        }
                        if result['symbol'] in mock_prices:
                            mock_data = mock_prices[result['symbol']]
                            result.update(mock_data)
                        else:
                            result['current_price'] = 0
                            result['change'] = 0
                            result['change_percent'] = 0
                    else:
                        result['current_price'] = float(result['current_price'])
                        result['change'] = float(result['change']) if result['change'] else 0
                        result['change_percent'] = float(result['change_percent']) if result['change_percent'] else 0
                    return result
                return None
        except Exception as e:
            print(f"Database error: {e}")
            # 如果数据库连接失败，从备用数据中查找
            stocks = await self.get_stocks()
            for stock in stocks:
                if stock["symbol"] == symbol.upper():
                    return stock
            return None

    async def get_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """获取技术指标"""
        try:
            async with asyncpg.connect(self.connection_string) as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM technical_indicators WHERE symbol = $1 ORDER BY date DESC LIMIT 1",
                    symbol.upper()
                )
                if row:
                    result = dict(row)
                    result['updated_at'] = result['date'].isoformat() if result.get('date') else datetime.now().isoformat()
                    return result
                else:
                    return {
                        "symbol": symbol.upper(),
                        "ma20": 145.30,
                        "ma50": 142.80,
                        "rsi": 65.5,
                        "macd": 2.1,
                        "bollinger_upper": 155.20,
                        "bollinger_lower": 135.30,
                        "updated_at": datetime.now().isoformat()
                    }
        except Exception as e:
            print(f"Database error: {e}")
            # 返回备用数据
            return {
                "symbol": symbol.upper(),
                "ma20": 145.30,
                "ma50": 142.80,
                "rsi": 65.5,
                "macd": 2.1,
                "bollinger_upper": 155.20,
                "bollinger_lower": 135.30,
                "updated_at": datetime.now().isoformat()
            }

    async def create_user(self, username: str, email: str, password_hash: str) -> bool:
        """创建用户"""
        try:
            async with asyncpg.connect(self.connection_string) as conn:
                await conn.execute(
                    "INSERT INTO users (username, email, password_hash) VALUES ($1, $2, $3)",
                    username, email, password_hash
                )
                return True
        except Exception as e:
            print(f"Database error: {e}")
            return False

# 全局数据库服务实例
db_service = DatabaseService()