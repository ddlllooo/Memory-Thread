# Memory Thread

一个使用 Vue 3 + FastAPI 构建的个人博客网站。北欧极简暖调配色，玻璃拟态与微拟态视觉风格。

## 技术栈

### 前端
- Vue 3 + TypeScript
- Vite 8
- Tailwind CSS 4
- Tiptap 富文本编辑器
- Lenis 惯性滚动
- Vue Router + Pinia
- Axios

### 后端
- FastAPI
- SQLAlchemy + PyMySQL
- JWT 认证

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/ddlllooo/Memory-Thread.git
cd Memory-Thread
```

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境
python -m venv .venv
.venv\Scripts\activate      # Windows
# source .venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt

# 创建数据库（MySQL）
# CREATE DATABASE memory_thread CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 初始化数据库表和默认管理员
python init_db.py

# 启动后端
uvicorn app.main:app --reload --port 8080
```

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问

- 前端：http://localhost:5173
- 后端 API：http://localhost:8080
- API 文档：http://localhost:8080/docs

## 默认管理员账户

- 用户名：`admin`
- 密码：`admin123`

> 登录态存储在 sessionStorage，关闭浏览器标签页自动退出。

## 项目结构

```
Memory-Thread/
├── frontend/                 # Vue 3 前端
│   └── src/
│       ├── api/              # API 请求
│       ├── components/       # 组件
│       │   ├── layout/       #   布局（Navbar, Footer）
│       │   └── ui/           #   通用（RichEditor）
│       ├── data/             # Mock 数据
│       ├── pages/            # 页面
│       │   ├── Home.vue      #   首页
│       │   ├── Blog.vue      #   博客列表
│       │   ├── Post.vue      #   文章详情
│       │   ├── About.vue     #   关于
│       │   ├── Login.vue     #   登录
│       │   └── Admin.vue     #   管理后台
│       ├── router/           # 路由
│       ├── stores/           # Pinia 状态管理
│       ├── styles/           # 全局样式
│       └── types/            # TypeScript 类型
│
├── backend/                  # FastAPI 后端
│   └── app/
│       ├── routers/          # API 路由
│       ├── models/           # 数据模型
│       ├── services/         # 业务逻辑
│       └── config.py         # 配置
│
└── uploads/                  # 上传文件目录
```

## 功能

- 博客文章发布与管理
- 富文本编辑器（加粗、斜体、标题、对齐、颜色、列表、图片插入等）
- 封面图上传
- 图片管理
- 标签筛选
- 文章阅读进度条
- 惯性滚动与页面过渡动画
- 玻璃拟态 / 微拟态视觉风格
- 北欧极简暖调配色（Noto Serif SC 衬线体标题）
- 响应式布局

## 许可证

MIT License
