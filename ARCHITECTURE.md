# 在线书店 — 项目架构文档

## 概述

全栈在线书店项目，前后端分离架构。后端：FastAPI + SQLAlchemy (async) + MySQL + Redis。前端：Vite + React + TypeScript + Tailwind CSS。

**分期路线**：
- **第一期**（已完成）：书籍浏览/搜索/详情、用户注册/登录（JWT 双 Token）、书评
- **第二期**（表已建，API/前端待做）：购物车、订单、支付、收藏

---

## 技术栈

| 层 | 技术 |
|---|------|
| Web 框架 | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0+ (async) |
| 数据库 | MySQL 8.0 (aiomysql 驱动) |
| 缓存 | Redis 7 (redis-py async) |
| 认证 | JWT 双 Token (python-jose + passlib/bcrypt) |
| 数据库迁移 | Alembic |
| 前端 | Vite + React 18 + TypeScript + Tailwind CSS + React Router + Axios |
| 部署 | Docker Compose (MySQL + Redis + App) |

---

## 目录结构

```
online-bookstore/
├── README.md
├── ARCHITECTURE.md            # 本文件
├── docker-compose.yml         # 三容器编排（MySQL + Redis + App）
├── .gitignore
│
├── backend/                   # FastAPI 后端
│   ├── main.py                # 应用入口：创建 FastAPI、注册中间件/路由/异常处理器
├── requirements.txt           # Python 依赖
├── .env / .env.example        # 环境变量
├── docker-compose.yml         # 三容器编排
├── Dockerfile                 # Python 3.13-slim 镜像
├── ARCHITECTURE.md            # 本文件
│
├── config/
│   ├── settings.py            # 集中配置（从 .env 加载）
│   ├── db_conf.py             # 异步引擎 + Session 工厂 + ORM 基类
│   ├── db.py                  # FastAPI 依赖注入 get_database()
│   └── redis.py               # Redis 客户端管理
│
├── middleware/
│   ├── timing.py              # 📐 请求耗时中间件
│   ├── logging.py             # Request ID 中间件
│   └── auth.py                # JWT 认证依赖 (get_current_user / get_optional_user)
│
├── models/                    # ORM 模型（每文件一张表）
│   ├── book.py                # Book + book_category 中间表（M:N）
│   ├── user.py                # User
│   ├── publisher.py           # Publisher
│   ├── category.py            # Category（自引用两级层级）
│   ├── review.py              # Review（书评）
│   ├── cart.py                # 🔲 Cart + CartItem（第二期）
│   ├── address.py             # 🔲 Address（第二期）
│   ├── order.py               # 🔲 Order + OrderItem（第二期）
│   ├── payment.py             # 🔲 Payment（第二期）
│   └── user_favorite.py       # 🔲 UserFavorite（第二期）
│
├── schemas/                   # Pydantic 请求/响应模型
│   ├── common.py              # 通用包装类型
│   ├── book.py                # BookCreate/Update/Response/Detail
│   ├── user.py                # UserRegister/Login/Response/Token
│   ├── publisher.py           # PublisherResponse
│   ├── category.py            # CategoryResponse（含 children）
│   └── review.py              # ReviewCreate/Response
│
├── crud/                      # 数据访问层
│   ├── book.py                # 多条件搜索 + FULLTEXT + 分页
│   ├── user.py                # User CRUD
│   ├── publisher.py           # Publisher 查询
│   ├── category.py            # 分类树查询
│   └── review.py              # 书评 CRUD + 均分统计
│
├── routers/                   # API 路由（RESTful, /api/v1/）
│   ├── book.py                # /api/v1/books/*
│   ├── auth.py                # /api/v1/auth/*
│   ├── publisher.py           # /api/v1/publishers
│   ├── category.py            # /api/v1/categories
│   └── review.py              # /api/v1/books/{id}/reviews
│
├── utils/
│   ├── cache.py               # Redis 缓存工具
│   ├── logging.py             # 结构化日志配置
│   ├── response.py            # 统一响应格式
│   └── security.py            # JWT + bcrypt 工具
│
├── seeds/                     # 数据初始化脚本
│   ├── seed_publisher.py      # 初始化出版社
│   └── seed_category.py       # 初始化分类树
├── seed_book.py               # 初始化 10 本书（含关联）
├── seed_book_batch.py         # 批量生成 500 本书
│
├── alembic/                   # 数据库迁移
│   ├── env.py                 # 迁移环境配置（async）
│   └── versions/              # 迁移脚本
├── alembic.ini                # Alembic 配置
│
├── index_benchmark.py         # 📚 [学习资料] 索引基准测试
├── explain_learning.sql       # 📚 [学习资料] EXPLAIN 笔记
└── frontend/                  # 前端工程（见下方）
```

---

## 数据模型

### 关系总览

```
User ────1:N──→ Review ────N:1──→ Book
                │                       │
                │                       │ N:1
                │                  Publisher
                │
                │                       │ M:N
                └────────────────→ Category

User ────1:1──→ Cart ──1:N──→ CartItem ──N:1──→ Book
User ────1:N──→ Order ──1:N──→ OrderItem ──N:1──→ Book
Order ──1:1──→ Payment
User ────1:N──→ Address
User ────M:N──→ Book (user_favorite)
```

### 关系类型分布

| 类型 | 具体关系 |
|------|---------|
| **1:N** | Publisher→Book, User→Review, Book→Review, User→Order, Order→OrderItem, User→Address |
| **1:1** | User→Cart, Order→Payment |
| **M:N** | Book↔Category, User↔Book（收藏）|
| **自引用** | Category.parent_id → Category.id（两级分类）|

---

## API 端点一览

所有端点前缀 `/api/v1`，统一响应格式 `{ "code": 200, "data": ..., "message": "success" }`。

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/books` | 否 | 书籍列表（keyword/category_id/价格范围/排序/分页）|
| GET | `/books/{id}` | 否 | 书籍详情（出版社/分类/均分/评论数）|
| POST | `/books` | 是 | 新增书籍 |
| PATCH | `/books/{id}` | 是 | 部分更新 |
| DELETE | `/books/{id}` | 是 | 删除（204）|
| GET | `/books/{id}/reviews` | 否 | 书评列表 |
| POST | `/books/{id}/reviews` | 是 | 写书评 |
| GET | `/publishers` | 否 | 出版社列表 |
| GET | `/categories` | 否 | 分类树 |
| POST | `/auth/register` | 否 | 注册 |
| POST | `/auth/login` | 否 | 登录 |
| POST | `/auth/refresh` | 否 | 刷新 Token |
| GET | `/auth/me` | 是 | 当前用户 |

---

## 中间件洋葱模型

```
请求 → CORS → RequestID → GZip → Timing → 路由处理
响应 ← CORS ← RequestID ← GZip ← Timing ← 路由处理
```

后续可扩展：TrustedHostMiddleware、SessionMiddleware、自定义限流中间件。

---

## 缓存策略

| 端点 | Key 模式 | TTL | 淘汰时机 |
|------|---------|-----|---------|
| GET /books | `books:list:<hash>` | 300s | 新增/修改/删除书籍时 |
| GET /books/{id} | `book:<id>` | 300s | 该书修改/删除时 |
| GET /publishers | 未缓存（表小） | — | — |
| GET /categories | 未缓存（表小） | — | — |

---

## 索引设计

索引命名规范：`fk_`（外键）、`uk_`（唯一）、`idx_`（普通）、`ft_`（全文）。

关键索引：
- `book.ft_book` — FULLTEXT(book_name, author, description)，搜索演进阶段二
- `book.idx_book_price` — 复合索引 (book_name, price)，最左前缀演示
- `review.idx_book_created` — 复合索引 (book_id, created_at)，避免 filesort
- 每张表的外键列均建有 `fk_` 前缀索引

---

## 搜索演进路径

```
阶段一：LIKE '%keyword%'       → 全表扫描，理解 B+ 树的局限
阶段二：MySQL FULLTEXT 索引     → 倒排索引，比 LIKE 快 100 倍
阶段三：Elasticsearch（后续）   → IK 分词/拼音/聚合/高亮
```

每段代码保留在 `crud/book.py` 中供对比学习。

---

## 后续扩展

| 方向 | 时机 | 说明 |
|------|------|------|
| **Elasticsearch** | 第一期完成后 | 搜索从 FULLTEXT 升级到 ES |
| **Celery** | 第二期 | 订单超时取消、异步通知、报表生成 |
| **Kafka** | Celery 学完后 | 把 broker 从 Redis 换成 Kafka |
| **Nacos** | 微服务拆分后 | 服务发现和配置中心 |
| **Alembic 正式启用** | 首次上线 | 代替 create_all() 管理 schema 版本 |
| **VIEW（视图）** | 报表需求 | 复杂聚合查询可抽为 MySQL 视图 |
| **行级锁** | 第二期订单 | `SELECT ... FOR UPDATE` 防超卖 |
| **管理后台** | 第三期 | 书籍管理、订单管理、用户管理 |

---

## 如何新增一个功能

1. 创建/修改 ORM 模型（`models/xxx.py`）
2. 生成迁移脚本：`alembic revision --autogenerate -m "描述"`
3. 执行迁移：`alembic upgrade head`
4. 创建 Schema（`schemas/xxx.py`）
5. 创建 CRUD（`crud/xxx.py`）
6. 创建 Router（`routers/xxx.py`）
7. 在 `main.py` 中导入模型 + 注册路由
8. 更新 `ARCHITECTURE.md`
