"""
InvestWin Business Service
投资分析业务逻辑服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
from datetime import datetime
from database import db_service

app = FastAPI(
    title="InvestWin Business Service",
    description="投资分析业务逻辑服务",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接已从 database.py 模块导入

# 导入业务逻辑模块
from services.technical_indicators import TechnicalIndicatorsService
from services.opportunity_mining import OpportunityMiningService
from services.risk_assessment import RiskAssessmentService

# 服务实例
technical_service = TechnicalIndicatorsService(db_service)
opportunity_service = OpportunityMiningService(db_service)
risk_service = RiskAssessmentService(db_service)

@app.get("/")
async def root():
    return {
        "service": "InvestWin Business Service",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        conn = await db_service.get_connection()
        await conn.execute("SELECT 1")
        await conn.close()
        return {
            "status": "healthy",
            "service": "business",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "business",
            "database": "disconnected",
            "error": str(e)
        }

@app.post("/api/technical-indicators/{symbol}")
async def calculate_technical_indicators(symbol: str):
    """计算技术指标"""
    try:
        indicators = await technical_service.calculate_all_indicators(symbol.upper())
        return {
            "success": True,
            "symbol": symbol.upper(),
            "indicators": indicators,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/find-opportunities")
async def find_investment_opportunities():
    """挖掘投资机会"""
    try:
        opportunities = await opportunity_service.find_opportunities()
        return {
            "success": True,
            "opportunities": opportunities,
            "count": len(opportunities),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/assess-risk/{symbol}")
async def assess_investment_risk(symbol: str):
    """评估投资风险"""
    try:
        risk_assessment = await risk_service.assess_risk(symbol.upper())
        return {
            "success": True,
            "symbol": symbol.upper(),
            "risk_assessment": risk_assessment,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/portfolio-analysis")
async def analyze_portfolio(symbols: List[str]):
    """投资组合分析"""
    try:
        analysis = await opportunity_service.analyze_portfolio(symbols)
        return {
            "success": True,
            "portfolio": symbols,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ========== 基础数据查询接口 ==========
@app.get("/api/assets")
async def get_assets():
    """获取所有资产列表"""
    try:
        assets = await db_service.get_stocks()
        return {
            "success": True,
            "assets": assets,
            "count": len(assets),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assets/{symbol}")
async def get_asset_by_symbol(symbol: str):
    """根据代码获取资产信息"""
    try:
        asset = await db_service.get_stock_by_symbol(symbol.upper())
        if not asset:
            raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")

        return {
            "success": True,
            "asset": asset,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assets/{symbol}/technical-indicators")
async def get_asset_technical_indicators(symbol: str):
    """获取资产技术指标"""
    try:
        indicators = await db_service.get_technical_indicators(symbol.upper())
        return {
            "success": True,
            "symbol": symbol.upper(),
            "technical_indicators": indicators,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assets/{symbol}/price-history")
async def get_asset_price_history(symbol: str, days: int = 30):
    """获取资产价格历史"""
    try:
        price_history = await db_service.get_price_history(symbol.upper(), days)
        return {
            "success": True,
            "symbol": symbol.upper(),
            "price_history": price_history,
            "count": len(price_history),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)