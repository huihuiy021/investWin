"""
业务服务客户端
用于与Business Service通信
"""

import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
import logging

class BusinessServiceClient:
    """业务服务客户端"""

    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url
        self.session = None

    async def _get_session(self):
        """获取HTTP会话"""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def close(self):
        """关闭HTTP会话"""
        if self.session:
            await self.session.close()
            self.session = None

    async def _make_request(self, method: str, endpoint: str, data: Any = None) -> Dict[str, Any]:
        """发送HTTP请求"""
        try:
            session = await self._get_session()
            url = f"{self.base_url}{endpoint}"

            async with session.request(method, url, json=data) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    logging.error(f"Business service error: {response.status} - {error_text}")
                    return {"error": f"Service unavailable: {response.status}"}

        except Exception as e:
            logging.error(f"Error calling business service: {e}")
            return {"error": str(e)}

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return await self._make_request("GET", "/health")

    async def calculate_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """计算技术指标"""
        return await self._make_request("POST", f"/api/technical-indicators/{symbol}")

    async def find_investment_opportunities(self) -> Dict[str, Any]:
        """挖掘投资机会"""
        return await self._make_request("POST", "/api/find-opportunities")

    async def assess_investment_risk(self, symbol: str) -> Dict[str, Any]:
        """评估投资风险"""
        return await self._make_request("POST", f"/api/assess-risk/{symbol}")

    async def analyze_portfolio(self, symbols: List[str]) -> Dict[str, Any]:
        """分析投资组合"""
        return await self._make_request("POST", "/api/portfolio-analysis", data=symbols)

    async def get_assets(self) -> Dict[str, Any]:
        """获取所有资产列表"""
        return await self._make_request("GET", "/api/assets")

    async def get_asset_by_symbol(self, symbol: str) -> Dict[str, Any]:
        """根据代码获取资产信息"""
        return await self._make_request("GET", f"/api/assets/{symbol}")

    async def get_asset_technical_indicators(self, symbol: str) -> Dict[str, Any]:
        """获取资产技术指标"""
        return await self._make_request("GET", f"/api/assets/{symbol}/technical-indicators")

    async def get_asset_price_history(self, symbol: str, days: int = 30) -> Dict[str, Any]:
        """获取资产价格历史"""
        return await self._make_request("GET", f"/api/assets/{symbol}/price-history?days={days}")

# 全局服务客户端实例
business_client = BusinessServiceClient()