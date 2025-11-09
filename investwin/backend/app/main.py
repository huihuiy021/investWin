from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="InvestWin API",
    description="投资资产分析跟踪平台 API",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 开发服务器
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Welcome to InvestWin API"}

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.get("/api/assets")
async def get_assets():
    """获取资产列表"""
    return [
        {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "current_price": 150.25,
            "change": 2.50,
            "change_percent": 1.69
        },
        {
            "symbol": "MSFT",
            "name": "Microsoft Corporation",
            "current_price": 320.80,
            "change": -1.20,
            "change_percent": -0.37
        }
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)