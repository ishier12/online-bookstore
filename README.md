# Online Bookstore

全栈在线书店项目 — FastAPI + React + MySQL + Redis

## 技术栈

| 层 | 技术 |
|---|------|
| 后端框架 | FastAPI (async) |
| ORM | SQLAlchemy 2.0 |
| 数据库 | MySQL 8.0 |
| 缓存 | Redis 7 |
| 认证 | JWT 双 Token (python-jose + bcrypt) |
| 前端 | Vite + React 18 + TypeScript + Tailwind CSS |
| 部署 | Docker Compose |

## 项目结构

```
online-bookstore/
├── backend/                  # FastAPI 后端
│   ├── main.py               # 应用入口
│   ├── config/               # 数据库/Redis/配置
│   ├── models/               # ORM 模型 (12 张表)
│   ├── routers/              # RESTful API (/api/v1/*)
│   ├── crud/                 # 数据访问层
│   ├── schemas/              # Pydantic 验证
│   ├── middleware/            # 中间件 (CORS/JWT/Timing/Logging)
│   ├── utils/                # 工具 (缓存/安全/响应)
│   ├── alembic/              # 数据库迁移
│   └── seeds/                # 种子数据
├── frontend/                 # React 前端
│   └── src/
│       ├── components/       # 组件
│       ├── pages/            # 页面
│       ├── api/              # API 调用
│       └── ...
├── docker-compose.yml        # MySQL + Redis + App
└── ARCHITECTURE.md           # 架构文档
```

## 快速启动

```bash
# 1. 启动基础设施
docker-compose up -d mysql redis

# 2. 安装后端依赖
cd backend
pip install -r requirements.txt

# 3. 初始化数据
python seeds/seed_publisher.py
python seeds/seed_category.py

# 4. 启动后端
uvicorn main:app --reload

# 5. 启动前端（另一个终端）
cd frontend
npm install
npm run dev
```

访问 http://localhost:8000/docs 查看 API 文档。
