# 阶段 1：构建前端
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# 阶段 2：运行后端
FROM python:3.11-slim
WORKDIR /app

# 安装依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY backend/ .

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist ./static

# 创建上传目录
RUN mkdir -p uploads

EXPOSE 8080

# 启动时自动初始化数据库并运行
CMD ["sh", "-c", "python init_db.py && python run.py"]
