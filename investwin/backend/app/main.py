from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
import asyncio
from datetime import datetime
from database import db_service
from service_client import business_client

app = FastAPI(
    title="InvestWin API",
    description="投资资产分析跟踪平台 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React 开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to InvestWin API", "database_status": "connected"}

@app.get("/api/health")
async def health_check():
    """健康检查"""
    try:
        # 测试数据库连接
        await db_service.get_stocks()
        return {
            "status": "healthy",
            "version": "1.0.0",
            "database": "postgresql"
        }
    except Exception as e:
        return {
            "status": "degraded",
            "version": "1.0.0",
            "database": "postgresql",
            "error": str(e)
        }

@app.get("/api/assets")
async def get_assets():
    """获取资产列表"""
    try:
        assets = await db_service.get_stocks()
        return {
            "success": True,
            "data": assets,
            "count": len(assets)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assets/{symbol}")
async def get_asset_detail(symbol: str):
    """获取资产详情"""
    try:
        asset = await db_service.get_stock_by_symbol(symbol.upper())
        if not asset:
            raise HTTPException(status_code=404, detail="Asset not found")

        # 获取技术指标
        indicators = await db_service.get_technical_indicators(symbol.upper())

        return {
            "success": True,
            "data": {
                **asset,
                "technical_indicators": indicators
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/assets/{symbol}/indicators")
async def get_technical_indicators(symbol: str):
    """获取技术指标"""
    try:
        indicators = await db_service.get_technical_indicators(symbol.upper())
        return {
            "success": True,
            "data": indicators,
            "symbol": symbol.upper()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/users")
async def create_user(user_data: Dict[str, Any]):
    """创建用户（示例端点）"""
    try:
        username = user_data.get("username")
        email = user_data.get("email")
        password_hash = user_data.get("password_hash")

        if not all([username, email, password_hash]):
            raise HTTPException(status_code=400, detail="Missing required fields")

        success = await db_service.create_user(username, email, password_hash)

        if success:
            return {
                "success": True,
                "message": f"User {username} created successfully"
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create user")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 业务服务代理端点
@app.get("/api/business/health")
async def business_service_health():
    """业务服务健康检查"""
    try:
        result = await business_client.health_check()
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Business service unavailable: {str(e)}")

@app.post("/api/business/technical-indicators/{symbol}")
async def get_technical_indicators(symbol: str):
    """获取技术指标"""
    try:
        result = await business_client.calculate_technical_indicators(symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Technical indicators service unavailable: {str(e)}")

@app.post("/api/business/opportunities")
async def get_investment_opportunities():
    """获取投资机会"""
    try:
        result = await business_client.find_investment_opportunities()
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Opportunity mining service unavailable: {str(e)}")

@app.post("/api/business/risk-assessment/{symbol}")
async def get_risk_assessment(symbol: str):
    """获取风险评估"""
    try:
        result = await business_client.assess_investment_risk(symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Risk assessment service unavailable: {str(e)}")

@app.post("/api/business/portfolio-analysis")
async def get_portfolio_analysis(symbols: List[str]):
    """获取投资组合分析"""
    try:
        result = await business_client.analyze_portfolio([s.upper() for s in symbols])
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Portfolio analysis service unavailable: {str(e)}")

# 综合分析端点
@app.get("/api/comprehensive-analysis/{symbol}")
async def get_comprehensive_analysis(symbol: str):
    """获取综合分析（包括技术指标、风险评估等）"""
    try:
        # 并行调用多个业务服务
        tasks = [
            business_client.calculate_technical_indicators(symbol.upper()),
            business_client.assess_investment_risk(symbol.upper()),
            db_service.get_stock_by_symbol(symbol.upper())
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        technical_result = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        risk_result = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
        stock_info = results[2] if not isinstance(results[2], Exception) else None

        if "error" in technical_result or "error" in risk_result:
            raise HTTPException(status_code=503, detail="Business services unavailable")

        return {
            "success": True,
            "symbol": symbol.upper(),
            "stock_info": stock_info,
            "technical_indicators": technical_result.get("indicators", {}),
            "risk_assessment": risk_result.get("risk_assessment", {}),
            "analysis_timestamp": datetime.now().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)