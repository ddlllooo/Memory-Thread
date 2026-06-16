@echo off
chcp 65001 >nul

echo ===================================
echo Memory Thread - 启动脚本
echo ===================================

:: 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python，请先安装 Python
    pause
    exit /b 1
)

:: 检查 Node.js 是否安装
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Node.js，请先安装 Node.js
    pause
    exit /b 1
)

:: 启动后端
echo.
echo 正在启动后端服务...
cd backend

:: 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 创建 Python 虚拟环境...
    python -m venv venv
)

:: 激活虚拟环境
call venv\Scripts\activate.bat

:: 安装依赖
echo 安装后端依赖...
pip install -r requirements.txt -q

:: 初始化数据库
echo 初始化数据库...
python init_db.py

:: 启动后端服务
echo 启动 FastAPI 服务...
start "Backend" cmd /c "uvicorn app.main:app --reload --port 8080"

cd ..

:: 启动前端
echo.
echo 正在启动前端服务...
cd frontend

:: 安装依赖
echo 安装前端依赖...
npm install -q

:: 启动前端服务
echo 启动 Vite 开发服务器...
start "Frontend" cmd /c "npm run dev"

cd ..

echo.
echo ===================================
echo 服务已启动！
echo ===================================
echo.
echo 前端地址: http://localhost:5173
echo 后端地址: http://localhost:8080
echo API 文档: http://localhost:8080/docs
echo.
echo 默认管理员账户:
echo 用户名: admin
echo 密码: admin123
echo.
echo 关闭此窗口不会停止服务
echo 请手动关闭 Backend 和 Frontend 窗口
pause
