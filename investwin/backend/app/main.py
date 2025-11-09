from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime
from service_client import business_client

app = FastAPI(
    title="InvestWin Web API",
    description="投资资产分析跟踪平台 Web API Gateway",
    version="2.0.0"
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
    return {
        "service": "InvestWin Web API Gateway",
        "version": "2.0.0",
        "description": "API Gateway for InvestWin Platform",
        "business_service": "http://localhost:8001"
    }

@app.get("/api/health")
async def health_check():
    """健康检查 - 检查Web服务和业务服务状态"""
    try:
        # 检查业务服务健康状态
        business_health = await business_client.health_check()

        return {
            "status": "healthy",
            "version": "2.0.0",
            "service": "web_api_gateway",
            "business_service": business_health,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "degraded",
            "version": "2.0.0",
            "service": "web_api_gateway",
            "business_service": {"status": "unreachable", "error": str(e)},
            "timestamp": datetime.now().isoformat()
        }

# ========== 资产管理端点 ==========
@app.get("/api/assets")
async def get_assets():
    """获取所有资产列表"""
    try:
        result = await business_client.get_assets()
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch assets: {str(e)}")

@app.get("/api/assets/{symbol}")
async def get_asset_detail(symbol: str):
    """获取资产详情"""
    try:
        result = await business_client.get_asset_by_symbol(symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch asset details: {str(e)}")

@app.get("/api/assets/{symbol}/technical-indicators")
async def get_asset_technical_indicators(symbol: str):
    """获取资产技术指标"""
    try:
        result = await business_client.get_asset_technical_indicators(symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch technical indicators: {str(e)}")

@app.get("/api/assets/{symbol}/price-history")
async def get_asset_price_history(symbol: str, days: Optional[int] = Query(30, description="历史数据天数")):
    """获取资产价格历史"""
    try:
        result = await business_client.get_asset_price_history(symbol.upper(), days)
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch price history: {str(e)}")

# ========== 业务服务代理端点 ==========
@app.get("/api/business/health")
async def business_service_health():
    """业务服务健康检查"""
    try:
        result = await business_client.health_check()
        return result
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Business service unavailable: {str(e)}")

@app.post("/api/business/technical-indicators/{symbol}")
async def calculate_technical_indicators(symbol: str):
    """计算技术指标"""
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
async def find_investment_opportunities():
    """挖掘投资机会"""
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
async def assess_investment_risk(symbol: str):
    """评估投资风险"""
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
async def analyze_portfolio(symbols: List[str]):
    """投资组合分析"""
    try:
        result = await business_client.analyze_portfolio([s.upper() for s in symbols])
        if "error" in result:
            raise HTTPException(status_code=503, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Portfolio analysis service unavailable: {str(e)}")

# ========== 综合分析端点 ==========
@app.get("/api/comprehensive-analysis/{symbol}")
async def get_comprehensive_analysis(symbol: str):
    """获取综合分析（包括基础信息、技术指标、风险评估等）"""
    try:
        # 并行调用多个业务服务
        tasks = [
            business_client.get_asset_by_symbol(symbol.upper()),
            business_client.calculate_technical_indicators(symbol.upper()),
            business_client.assess_investment_risk(symbol.upper())
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        asset_result = results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])}
        technical_result = results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])}
        risk_result = results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])}

        # 检查是否有错误
        errors = []
        if "error" in asset_result:
            errors.append(f"Asset data: {asset_result['error']}")
        if "error" in technical_result:
            errors.append(f"Technical analysis: {technical_result['error']}")
        if "error" in risk_result:
            errors.append(f"Risk assessment: {risk_result['error']}")

        if errors:
            raise HTTPException(status_code=503, detail=f"Business services unavailable: {'; '.join(errors)}")

        return {
            "success": True,
            "symbol": symbol.upper(),
            "asset_info": asset_result.get("asset", {}),
            "technical_indicators": technical_result.get("indicators", {}),
            "risk_assessment": risk_result.get("risk_assessment", {}),
            "analysis_timestamp": datetime.now().isoformat(),
            "data_sources": ["business_service"]
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Comprehensive analysis failed: {str(e)}")

# ========== 用户管理端点（示例） ==========
@app.post("/api/users")
async def create_user(user_data: Dict[str, Any]):
    """创建用户（示例端点 - 通过业务服务处理）"""
    try:
        # 注意：这里需要在业务服务中实现用户管理功能
        # 目前返回一个占位响应
        return {
            "success": False,
            "message": "User management not implemented in business service yet",
            "requested_data": user_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)