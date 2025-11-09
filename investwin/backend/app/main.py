from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from database import db_service

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
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "mock_data"  # 由于编译限制使用模拟数据
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)