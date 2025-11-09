#!/bin/bash

# 激活虚拟环境
echo "激活 Python 虚拟环境..."
source venv/bin/activate

# 升级 pip
echo "升级 pip..."
pip install --upgrade pip

# 安装依赖
echo "安装 Python 依赖包..."
pip install -r requirements/requirements.txt

echo "✅ Python 环境设置完成！"
echo ""
echo "使用方法："
echo "1. 激活虚拟环境: source venv/bin/activate"
echo "2. 运行服务器: uvicorn app.main:app --reload --port 8000"