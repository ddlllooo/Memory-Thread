#!/bin/bash

# ======================
# MemoryThread 部署脚本
# ======================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== MemoryThread 部署脚本 ===${NC}"
echo ""

# 1. 检查 .env.production
if [ ! -f .env.production ]; then
    if [ -f .env.production.example ]; then
        echo -e "${YELLOW}.env.production 不存在，从模板创建...${NC}"
        cp .env.production.example .env.production
        echo -e "${RED}请先编辑 .env.production 修改所有 CHANGE_ME 配置：${NC}"
        echo "  vim .env.production"
        exit 1
    else
        echo -e "${RED}错误：.env.production 和 .env.production.example 都不存在${NC}"
        exit 1
    fi
fi

# 2. 检查 SSL 证书
if [ ! -f nginx/ssl/fullchain.pem ] || [ ! -f nginx/ssl/privkey.pem ]; then
    echo -e "${YELLOW}警告：SSL 证书文件不存在${NC}"
    echo "请将 SSL 证书放到 nginx/ssl/ 目录："
    echo "  - nginx/ssl/fullchain.pem"
    echo "  - nginx/ssl/privkey.pem"
    echo ""
    echo "可以使用 Let's Encrypt 获取免费证书："
    echo "  apt install certbot"
    echo "  certbot certonly --standalone -d moondrift.cloud"
    echo ""
    read -p "是否继续部署？(y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 3. 停止旧容器
echo -e "${GREEN}停止旧容器...${NC}"
docker compose down

# 4. 构建镜像
echo -e "${GREEN}构建镜像...${NC}"
docker compose build --no-cache

# 5. 启动服务
echo -e "${GREEN}启动服务...${NC}"
docker compose up -d

# 6. 等待数据库就绪
echo -e "${GREEN}等待数据库就绪...${NC}"
sleep 10

# 7. 检查服务状态
echo -e "${GREEN}检查服务状态...${NC}"
docker compose ps

echo ""
echo -e "${GREEN}=== 部署完成 ===${NC}"
echo ""
echo "访问地址："
echo "  - https://moondrift.cloud"
echo "  - 管理后台：https://moondrift.cloud/admin"
echo ""
echo "常用命令："
echo "  - 查看日志：docker compose logs -f"
echo "  - 重启服务：docker compose restart"
echo "  - 停止服务：docker compose down"
echo ""
