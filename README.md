# Memory Thread - 个人博客网站

一个使用 Vue 3 + FastAPI 构建的个人博客网站，具有 3D 立体风格和炫酷动画效果。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite 6
- shadcn/ui-vue
- Tailwind CSS
- GSAP + ScrollTrigger（动画）
- Lenis（惯性滚动）
- Vue Router
- Pinia（状态管理）
- Axios

### 后端
- FastAPI
- SQLAlchemy + PyMySQL
- JWT 认证
- Pillow（图片处理）

## 快速开始

### 1. 克隆项目
```bash
git clone <repository-url>
cd memory-thread
```

### 2. 设置后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接等信息

# 初始化数据库
python init_db.py

# 启动后端服务
uvicorn app.main:app --reload --port 8080
```

### 3. 设置前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端：http://localhost:5173
- 后端 API：http://localhost:8080
- API 文档：http://localhost:8080/docs

## 默认管理员账户

- 用户名：admin
- 密码：admin123

**注意：请在生产环境中修改默认密码！**

## 项目结构

```
memory-thread/
├── frontend/              # Vue 前端
│   ├── src/
│   │   ├── api/          # API 请求
│   │   ├── components/   # 组件
│   │   ├── composables/  # 组合式函数
│   │   ├── pages/        # 页面
│   │   ├── router/       # 路由
│   │   ├── stores/       # 状态管理
│   │   └── styles/       # 样式
│   └── package.json
│
├── backend/               # FastAPI 后端
│   ├── app/
│   │   ├── routers/      # API 路由
│   │   ├── models/       # 数据模型
│   │   ├── services/     # 业务逻辑
│   │   └── config.py     # 配置
│   └── requirements.txt
│
├── uploads/               # 上传文件目录
└── README.md
```

## 功能特性

- ✅ 3D 立体风格界面
- ✅ 炫酷动画效果（GSAP）
- ✅ 惯性滚动（Lenis）
- ✅ 图片画廊（瀑布流布局）
- ✅ 灯箱预览
- ✅ 管理员登录
- ✅ 内容管理（CRUD）
- ✅ 图片上传和管理
- ✅ 响应式设计

## 部署

### 前端构建
```bash
cd frontend
npm run build
```

### 后端部署
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8080
```

## 许可证

MIT License
