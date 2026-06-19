# MemoryThread 部署指南

## 域名：moondrift.cloud

## 前置要求

- 云服务器（推荐 2GB+ 内存）
- Docker 和 Docker Compose 已安装
- 域名已解析到服务器 IP

## 部署步骤

### 1. 克隆代码

```bash
git clone <your-repo-url> memory-thread
cd memory-thread
```

### 2. 配置环境变量

```bash
# 复制配置模板
cp .env.production .env.production.bak

# 编辑配置（必须修改所有 CHANGE_ME）
vim .env.production
```

**必须修改的配置：**

| 配置项 | 说明 |
|--------|------|
| `DB_ROOT_PASSWORD` | MySQL root 密码 |
| `SECRET_KEY` | JWT 密钥（32位随机字符串） |
| `ADMIN_PASSWORD` | 管理员登录密码 |

**生成随机密钥：**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. 配置 SSL 证书

**方式一：使用 Let's Encrypt（推荐）**

```bash
# 安装 certbot
apt update && apt install -y certbot

# 停止占用 80 端口的服务
docker compose down

# 获取证书
certbot certonly --standalone -d moondrift.cloud -d www.moondrift.cloud

# 复制证书到项目目录
mkdir -p nginx/ssl
cp /etc/letsencrypt/live/moondrift.cloud/fullchain.pem nginx/ssl/
cp /etc/letsencrypt/live/moondrift.cloud/privkey.pem nginx/ssl/

# 设置证书自动续期
echo "0 0 1 * * certbot renew && docker compose restart nginx" | crontab -
```

**方式二：使用其他证书**

将你的 SSL 证书文件放到 `nginx/ssl/` 目录：
- `fullchain.pem` - 证书链
- `privkey.pem` - 私钥

### 4. 部署

```bash
# 添加执行权限
chmod +x deploy.sh

# 运行部署脚本
./deploy.sh
```

或手动部署：

```bash
# 构建并启动
docker compose build
docker compose up -d

# 查看日志
docker compose logs -f
```

### 5. 验证部署

```bash
# 检查服务状态
docker compose ps

# 测试 API
curl https://moondrift.cloud/api/v1/health

# 测试网站
curl -I https://moondrift.cloud
```

## 常用命令

```bash
# 查看所有容器状态
docker compose ps

# 查看实时日志
docker compose logs -f

# 重启所有服务
docker compose restart

# 重启单个服务
docker compose restart app

# 停止所有服务
docker compose down

# 进入容器
docker compose exec app bash
docker compose exec db mysql -u root -p

# 备份数据库
docker compose exec db mysqldump -u root -p memory_thread > backup.sql

# 恢复数据库
docker compose exec -T db mysql -u root -p memory_thread < backup.sql
```

## 更新部署

```bash
# 拉取最新代码
git pull

# 重新构建并部署
docker compose build --no-cache
docker compose up -d

# 如果数据库有变更
docker compose exec app python init_db.py
```

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker compose logs app
docker compose logs db
docker compose logs nginx

# 检查端口占用
netstat -tlnp | grep -E '80|443|3306'
```

### 数据库连接失败

```bash
# 检查数据库状态
docker compose exec db mysqladmin ping -u root -p

# 查看数据库日志
docker compose logs db
```

### SSL 证书问题

```bash
# 检查证书有效期
openssl x509 -in nginx/ssl/fullchain.pem -noout -dates

# 测试 SSL 配置
curl -vI https://moondrift.cloud
```

## 目录结构

```
memory-thread/
├── backend/           # FastAPI 后端
├── frontend/          # Vue 前端
├── nginx/
│   ├── nginx.conf     # Nginx 配置
│   └── ssl/           # SSL 证书
├── Dockerfile         # Docker 构建文件
├── docker-compose.yml # 服务编排
├── .env.production    # 生产环境配置
└── deploy.sh          # 部署脚本
```

## 安全建议

1. **定期更新密码** - 每 3-6 个月更换一次
2. **启用防火墙** - 只开放 80、443、22 端口
3. **定期备份** - 数据库和上传文件
4. **监控日志** - 关注异常访问
5. **保持更新** - 定期更新 Docker 镜像
