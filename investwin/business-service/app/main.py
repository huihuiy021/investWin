"""
InvestWin Business Service
投资分析业务逻辑服务
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import os
import asyncpg
from datetime import datetime

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

# 数据库连接
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://huihui:investwin123@localhost:5432/investwin"
)

class DatabaseService:
    def __init__(self):
        self.connection_string = DATABASE_URL

    async def get_connection(self):
        return await asyncpg.connect(self.connection_string)

db_service = DatabaseService()

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)