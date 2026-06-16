#!/bin/bash

echo "==================================="
echo "Memory Thread - 启动脚本"
echo "==================================="

# 检查 Python 是否安装
if ! command -v python &> /dev/null; then
    echo "错误: 未找到 Python，请先安装 Python"
    exit 1
fi

# 检查 Node.js 是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 Node.js，请先安装 Node.js"
    exit 1
fi

# 启动后端
echo ""
echo "正在启动后端服务..."
cd backend

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "创建 Python 虚拟环境..."
    python -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# 安装依赖
echo "安装后端依赖..."
pip install -r requirements.txt -q

# 初始化数据库
echo "初始化数据库..."
python init_db.py

# 启动后端服务（后台运行）
echo "启动 FastAPI 服务..."
uvicorn app.main:app --reload --port 8080 &
BACKEND_PID=$!

cd ..

# 启动前端
echo ""
echo "正在启动前端服务..."
cd frontend

# 安装依赖
echo "安装前端依赖..."
npm install -q

# 启动前端服务
echo "启动 Vite 开发服务器..."
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "==================================="
echo "服务已启动！"
echo "==================================="
echo ""
echo "前端地址: http://localhost:5173"
echo "后端地址: http://localhost:8080"
echo "API 文档: http://localhost:8080/docs"
echo ""
echo "默认管理员账户:"
echo "用户名: admin"
echo "密码: admin123"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM

# 等待
wait
