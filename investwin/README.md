# InvestWin - 投资资产分析跟踪平台

## 技术栈
- **后端**: Python + FastAPI + PostgreSQL
- **前端**: React + TypeScript + Ant Design
- **数据库**: PostgreSQL 14

## 开发环境设置

### 1. 后端设置
```bash
cd backend
chmod +x setup.sh
./setup.sh
```

### 2. 数据库设置
```bash
# 启动 PostgreSQL 服务
brew services start postgresql@14

# 创建数据库
createdb investwin

# 连接数据库
psql investwin
```

### 3. 前端设置
```bash
cd frontend
npx create-react-app . --template typescript
npm install @reduxjs/toolkit antd react-chartjs-2 chart.js
```

## 项目结构
```
investwin/
├── backend/           # Python FastAPI 后端
│   ├── app/          # 应用代码
│   ├── venv/         # Python 虚拟环境
│   └── requirements/ # 依赖包
├── frontend/         # React 前端
├── database/         # 数据库脚本
└── docs/            # 项目文档
```

## 快速启动
1. 设置后端环境和依赖
2. 启动 PostgreSQL 数据库
3. 运行数据库迁移
4. 启动后端服务: `uvicorn app.main:app --reload`
5. 启动前端服务: `npm start`