# Full-Stack Online Bookstore — 实施计划

## Context

将现有的 FastAPI 学习项目改造为完整的全栈在线书店。当前项目只有单表 CRUD（Book）和索引学习用的演示表，缺少用户体系、多表关系、前端界面。本次改造的目标：

1. 设计完整的数据库，覆盖 1:1、1:N、M:N 三种关系
2. 实现 RESTful API，修复现有 API 不规范之处
3. 搭建 Vite + React + Tailwind CSS 前端
4. 保留所有现有学习资料，加注释说明用途
5. 建立 `ARCHITECTURE.md` 作为项目导航文档
6. 为后续学习 Celery/ES/Kafka 等中间件预留扩展空间

分期：第一期做浏览/搜索/详情/书评/用户注册登录；第二期表结构先建好但 API 和前端暂不做（购物车/订单/支付/收藏）。

---

## 技术决策（已确认）

| 决策 | 选择 |
|------|------|
| 旧表处理 | 保留 `article`、3 张 `review_*` 演示表，加注释说明是学习资料 |
| 认证策略 | JWT 双 Token：Access Token 30min + Refresh Token 7 天 |
| API 响应格式 | 统一包裹：`{ "code": 200, "data": ..., "message": "success" }` |
| API 版本 | 前缀 `/api/v1/`，以后可 `/api/v2/` 共存 |
| 数据库迁移 | 引入 Alembic，替代 `create_all()` 管理 schema 变更 |
| 日志 | 引入结构化日志（`logging` 模块 + request_id），替代 `print()` |
| 前端 | Vite + React + TypeScript + Tailwind CSS + React Router + Axios |
| 中间件 | CORS + GZip + 现有 TimingMiddleware；其余按需扩展 |

---

## 后续技术路线图（本次不实施，设计中预留接口）

### Celery（第二期引入）

**为什么不第一期就加**：第一期没有天然的异步任务场景。注册/搜索/写书评都是毫秒级同步操作，硬塞一个演示任务没有学习价值。

**第二期的真实场景**：
- 下单后异步更新库存统计
- 订单超时未支付自动取消（Celery 定时任务）
- 生成销售报表（耗时的聚合查询从请求线程剥离）

**架构预留**：
- Redis 已经是 Celery 的标准 broker，无需新增基础设施
- `docker-compose.yml` 里加一个 `celery_worker` 服务即可
- 目录结构预留 `tasks/` 目录放 Celery 任务定义

### Elasticsearch（第一期完成后作为独立学习任务引入）

**为什么不第一期就加**：学习路径设计为三段式演进——先用 LIKE 体验全表扫描的痛苦，再用 MySQL FULLTEXT 看到倒排索引的力量，最后引入 ES 理解专用搜索引擎的天花板。一步跳到 ES 等于跳过了理解「为什么需要」的过程。

**三段式学习路径**：`MySQL LIKE` → `MySQL FULLTEXT` → `Elasticsearch (IK 分词 → 拼音搜索 → 聚合搜索)`

每段的代码保留在 `crud/book.py` 中作为对比学习资料。

**架构预留**：
- `GET /api/v1/books?keyword=` 的接口层保持不变，前端零改动
- 只需替换 `crud/book.py` 中的查询实现
- `docker-compose.yml` 后续加 ES 容器即可

### Kafka（第二期后学习）

需先引入异步任务场景或事件驱动模式。最自然路径：Celery → 把 broker 从 Redis 换成 Kafka → 理解 Producer/Consumer/Topic/Partition。

### Nacos（现阶段不推荐）

需先拆微服务（至少 3-4 个独立服务）。单体应用没有服务发现需求。建议学完微服务架构后再碰。

---

## 完整表结构（共 5 张第一期表 + 7 张第二期表壳）

### 第一期 — 建表 + API + 前端

```
✅ user              用户（username, email, hashed_password, nickname, avatar_url, is_active, is_admin）
✅ publisher         出版社（name, description）— 1:N → Book
✅ category          分类（name, parent_id 自引用，最多两级）— M:N → Book
✅ book_category     分类中间表（book_id, category_id 复合主键，纯 Table 对象）
✅ book              书籍（book_name, author, price DECIMAL, isbn, cover_url, description, stock, publisher_id FK）— 改造现有表
✅ review            书评（user_id FK, book_id FK, rating 1-5, content）— UNIQUE(user_id, book_id) 每人每书限一条
```

### 第二期 — 只建表（无 API 无页面）

```
🔲 cart             购物车（user_id UNIQUE, 1:1）
🔲 cart_item        购物车明细（cart_id FK, book_id FK, quantity）
🔲 address          收货地址（user_id FK, recipient_name, phone, 省市区, detail, is_default）
🔲 order            订单（user_id FK, address_id FK, status ENUM, total_amount）
🔲 order_item       订单明细（order_id FK, book_id FK, quantity, price 快照）
🔲 payment          支付（order_id UNIQUE 1:1, amount, method ENUM, status ENUM）
🔲 user_favorite    收藏（user_id FK, book_id FK, M:N）
```

### 保留不动（加注释标记为学习资料）

```
📚 article          SQLAlchemy 14 种字段类型演示（models/article.py）
📚 review_no_idx    EXPLAIN 索引学习 — 无索引对照组（models/index_demo.py）
📚 review_idx       EXPLAIN 索引学习 — 单列索引（models/index_demo.py）
📚 review_composite_idx  EXPLAIN 索引学习 — 复合索引（models/index_demo.py）
```

---

## 数据库索引设计（完整方案）

### 索引命名规范

| 前缀 | 含义 | 示例 |
|------|------|------|
| `pk_` | Primary Key | MySQL 默认叫 `PRIMARY` |
| `uk_` | Unique Key | `uk_username` |
| `fk_` | Foreign Key 索引（专为 JOIN 加速） | `fk_publisher_id` |
| `idx_` | 普通索引（查询/排序/复合条件） | `idx_price`, `idx_book_created` |
| `ft_` | Fulltext 索引 | `ft_book` |

### 设计原则

1. **最左前缀原则** — 复合索引中，等值条件列在前，范围条件列在后
2. **高选择性列优先** — 区分度高的列（如 user_id）比低区分度列（如 is_active）更适合建索引
3. **覆盖索引优先** — 如果查询只需索引中的列，避免回表（`Using index`）
4. **避免过度索引** — 每多一个索引，INSERT/UPDATE/DELETE 就多维护一棵 B+ 树
5. **外键必建索引** — JOIN 操作依赖外键列的索引，命名用 `fk_` 前缀

### user 表

```sql
-- 已有：PRIMARY KEY (id)
UNIQUE INDEX uk_username (username)     -- 登录 WHERE username = ?、注册查重
UNIQUE INDEX uk_email (email)           -- 注册查重、可能用 email 登录
```

### publisher 表

```sql
-- 已有：PRIMARY KEY (id)
UNIQUE INDEX uk_name (name)             -- 出版社名唯一约束
-- 轻量表，每次基本都是全表查询，不需要额外索引
```

### category 表

```sql
-- 已有：PRIMARY KEY (id)
INDEX idx_parent_id (parent_id)         -- 查子分类 WHERE parent_id = ?
-- 说明：查顶级分类 WHERE parent_id IS NULL 也会走此索引
```

### book 表 — 查询最频繁，索引最关键

```sql
-- 已有：PRIMARY KEY (id)

-- 外键索引（JOIN publisher 时用到）
INDEX fk_publisher_id (publisher_id)

-- 价格范围索引（最常用的筛选条件）
INDEX idx_price (price)                 -- WHERE price >= ? AND price <= ?

-- 排序索引（默认按上架时间倒序）
INDEX idx_created_at (created_at)       -- ORDER BY created_at DESC

-- 复合索引演示：书名等值 + 价格范围（最左前缀）
-- book_name(等值)在前，price(范围)在后 — 符合最左前缀原则
INDEX idx_book_price (book_name, price) -- WHERE book_name = ? AND price >= ?

-- MySQL 全文索引（ES 之前的过渡方案）
-- 支持自然语言模式和布尔模式，替代 LIKE '%keyword%'
-- 用法：WHERE MATCH(book_name, author, description) AGAINST('Python' IN NATURAL LANGUAGE MODE)
FULLTEXT INDEX ft_book (book_name, author, description)
```

**关于 LIKE 和索引的关键知识点**：
```sql
-- ✅ 走索引（前缀匹配），B+ 树可以利用有序性
WHERE book_name LIKE 'Python%'

-- ❌ 不走索引（左模糊），必须全表扫描
WHERE book_name LIKE '%Python%'

-- ✅ 走 FULLTEXT 索引（自然语言搜索，支持分词）
WHERE MATCH(book_name, author, description) AGAINST('Python' IN NATURAL LANGUAGE MODE)
```

**搜索演进三段式**（循序渐进，每段代码保留以便对比学习）：

```
阶段一：LIKE '%keyword%'
  → 体验：模糊搜索不走 B+ 树，全表扫描，几百条无所谓，几万条开始卡
  → 学到：B+ 树为什么对左模糊无效

阶段二：MySQL FULLTEXT 索引
  → 体验：倒排索引 + 自然语言分词，比 LIKE 快两个数量级
  → 学到：倒排索引原理、ngram 分词、布尔模式 vs 自然语言模式
  → 局限：无中文分词器（只能 ngram）、不支持分布式、不能高亮、不能纠错

阶段三：Elasticsearch（后续学习任务）
  → 体验：IK 分词、拼音搜索、聚合 facet、高亮、分布式
  → 学到：专用搜索引擎和数据库内置全文索引的天花板差异
```

搜索实现策略：`crud/book.py` 中 keyword 搜时优先用 FULLTEXT（MATCH...AGAINST），keyword 为空时走普通 LIKE 兜底。

### book_category 中间表

```sql
-- 已有：PRIMARY KEY (book_id, category_id) — 覆盖「书属于哪些分类」
INDEX idx_category_book (category_id, book_id)  -- 反向查「某分类下有哪些书」
-- 说明：复合主键只优化了第一个方向，反向查询需另建索引
```

### review 表

```sql
-- 已有：PRIMARY KEY (id)

-- 业务约束 + 覆盖「某人是否评过某书」查询
UNIQUE INDEX uk_user_book (user_id, book_id)

-- 书籍详情页最频繁查询：某书书评按时间倒序
-- book_id(等值)在前，created_at DESC(排序)在后 → 避免 filesort
INDEX idx_book_created (book_id, created_at)

-- 「我的书评」页面
INDEX fk_user_id (user_id)
-- 说明：外键索引加速 JOIN user 表
```

### 第二期表索引（建表时一并创建）

```sql
-- cart_item：同一本书不能加两次购物车
UNIQUE INDEX uk_cart_book (cart_id, book_id)

-- address：查某用户的默认地址
INDEX idx_user_default (user_id, is_default)

-- order：我的订单按时间倒序
INDEX idx_user_created (user_id, created_at)
-- 管理后台按状态筛选
INDEX idx_status (status)

-- order_item：订单详情
INDEX fk_order_id (order_id)

-- user_favorite：不能重复收藏 + 我的收藏按时间倒序
UNIQUE INDEX uk_user_book (user_id, book_id)
INDEX idx_user_created (user_id, created_at)
```

---

## SQL 优化、视图、锁 — 本期学习规划

| 技术 | 本期是否引入 | 说明 |
|------|------------|------|
| **复合索引 + 最左前缀** | ✅ 已设计 | `idx_book_price(book_name, price)` 和 `idx_book_created(book_id, created_at)` 都是复合索引实践 |
| **FULLTEXT 索引** | ✅ 已设计 | `ft_book`，作为 ES 过渡方案，演示 MySQL 内置全文检索 |
| **覆盖索引** | ✅ 观察 EXPLAIN | `uk_user_book(user_id, book_id)` 查 `COUNT(*)` 时走覆盖索引（Using index），配合 `EXPLAIN` 观察 |
| **EXPLAIN 分析** | ✅ 沿用现有 | `explain_learning.sql` 保留，新查询也可用 EXPLAIN 验证是否走索引 |
| **VIEW（视图）** | ❌ 不引入 | SQLAlchemy ORM 的 JOIN 查询已足够清晰；MySQL 视图不物化，无性能提升。`ARCHITECTURE.md` 中提一句作为扩展方向 |
| **行级锁（FOR UPDATE）** | ❌ 第二期 | 订单场景需要：`SELECT stock FROM book WHERE id=? FOR UPDATE` 防超卖 |
| **表级锁** | ❌ 不需要 | InnoDB 默认行锁，显式表锁在 OLTP 场景几乎不需要 |

---

## RESTful API 端点设计

所有端点前缀 `/api/v1`，统一包裹格式 `{ "code": 200, "data": ..., "message": "success" }`。
分页端点额外包含 `total/page/page_size`。

### 认证（`/api/v1/auth`）

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| POST | `/api/v1/auth/register` | 否 | 注册 |
| POST | `/api/v1/auth/login` | 否 | 登录，返回 access_token + refresh_token |
| POST | `/api/v1/auth/refresh` | 否 | 用 refresh_token 换新 access_token |
| GET | `/api/v1/auth/me` | 是 | 当前用户信息 |

### 书籍（`/api/v1/books`）

| 方法 | 路径 | 认证 | 说明 | 缓存 |
|------|------|------|------|------|
| GET | `/api/v1/books` | 否 | 列表（keyword/category_id/min_price/max_price/sort/page/page_size）| 300s |
| GET | `/api/v1/books/{id}` | 否 | 详情（含出版社/分类/均分/评论数）| 300s |
| POST | `/api/v1/books` | 是 | 新增 | 淘汰列表 |
| PATCH | `/api/v1/books/{id}` | 是 | 部分更新（修复原 PUT→PATCH）| 淘汰该书+列表 |
| DELETE | `/api/v1/books/{id}` | 是 | 删除，204 No Content（修复原 response_model 冲突）| 淘汰该书+列表 |

### 书评（嵌套在书籍下）

| 方法 | 路径 | 认证 | 说明 |
|------|------|------|------|
| GET | `/api/v1/books/{id}/reviews` | 否 | 该书评列表（分页）|
| POST | `/api/v1/books/{id}/reviews` | 是 | 写书评（每人每书限一条，重复 409）|

### 出版社 & 分类（只读）

| 方法 | 路径 | 认证 | 说明 | 缓存 |
|------|------|------|------|------|
| GET | `/api/v1/publishers` | 否 | 出版社列表 | 600s |
| GET | `/api/v1/categories` | 否 | 分类树（两级，含 children）| 600s |

---

## 关键文件变更

### 修改的现有文件

| 文件 | 改动 |
|------|------|
| `main.py` | 加 CORS + GZip + 结构化日志 + 验证异常处理器；注册所有新路由；导入所有模型 |
| `requirements.txt` | 加 `python-jose`, `passlib[bcrypt]`, `python-multipart`, `python-dotenv`, `alembic` |
| `docker-compose.yml` | 加 JWT/CORS 环境变量 |
| `.gitignore` | 加 `frontend/node_modules/`, `frontend/dist/`, `.env` |
| `config/db_conf.py` | `echo` 改为环境变量控制；引入 settings；适配 Alembic |
| `models/book.py` | 加 6 个新字段 + publisher_id FK + category M:N 关系；删 `publisher` 字符串字段；价格改为 DECIMAL；按索引方案加 Index 定义 |
| `schemas/book.py` | 新字段 + BookDetail 含 publisher/categories/avg_rating；BookUpdate 适配 PATCH |
| `crud/book.py` | 多条件搜索（FULLTEXT 优先，LIKE 兜底）+ joinedload 联表查询 |
| `routers/book.py` | PUT→PATCH；DELETE 去 response_model 用 204；统一包裹响应；路径加 `/api/v1` |
| `seed_book.py` | 适配新字段和 publisher_id |
| `seed_book_batch.py` | 同上 |
| `test_main.http` | 更新为新的 API 示例 |

### 新建的后端文件（~25 个）

```
.env + .env.example                    环境变量
config/settings.py                     集中配置
utils/security.py                      JWT 生成/验证 + 密码哈希
utils/response.py                      统一响应工具函数
utils/logging.py                       request_id 生成 + 结构化日志配置
middleware/auth.py                     get_current_user / get_optional_user 依赖
middleware/logging.py                  RequestIDMiddleware（注入 X-Request-ID）
models/user.py, publisher.py, category.py, review.py
models/cart.py, address.py, order.py, payment.py, user_favorite.py  (第二期壳)
schemas/common.py, user.py, publisher.py, category.py, review.py
crud/user.py, publisher.py, category.py, review.py
routers/auth.py, publisher.py, category.py, review.py
seeds/seed_publisher.py, seed_category.py
alembic.ini + alembic/env.py          Alembic 迁移配置
ARCHITECTURE.md                       项目架构文档
```

### 新建的前端工程（~30 个文件）

```
frontend/
  package.json, vite.config.ts, tsconfig*.json
  tailwind.config.js, postcss.config.js, index.html
  src/
    main.tsx, App.tsx, index.css
    types/index.ts
    api/client.ts, auth.ts, books.ts, reviews.ts, categories.ts
    context/AuthContext.tsx
    hooks/useBooks.ts, useBookDetail.ts, useReviews.ts
    utils/format.ts, constants.ts
    components/
      layout/Navbar.tsx, Footer.tsx, Layout.tsx
      common/Loading.tsx, ErrorMessage.tsx, Pagination.tsx,
             StarRating.tsx, ProtectedRoute.tsx, EmptyState.tsx
      books/BookCard.tsx, BookGrid.tsx, BookSearch.tsx
      reviews/ReviewList.tsx, ReviewItem.tsx, ReviewForm.tsx
    pages/
      HomePage.tsx, BookListPage.tsx, BookDetailPage.tsx,
      LoginPage.tsx, RegisterPage.tsx, UserProfilePage.tsx, NotFoundPage.tsx
```

---

## 中间件配置

`main.py` 中添加顺序（洋葱模型，先 add 的在外层）：

```python
# 1. 安全/网络层
app.add_middleware(CORSMiddleware, allow_origins=settings.CORS_ORIGINS, ...)
# 2. 请求追踪
app.add_middleware(RequestIDMiddleware)          # 每个请求生成唯一 X-Request-ID
# 3. 压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)
# 4. 自定义监控
app.add_middleware(TimingMiddleware)
# 后续可随时插入：TrustedHostMiddleware、SessionMiddleware、自定义限流等
```

---

## 项目结构调整

保留的学习资料保持原位置，在文件头部加注释标记：

```python
# models/article.py → 顶部加：
# 📚 [学习资料] 展示 SQLAlchemy 14 种 MySQL 字段类型，非业务表，不影响正常业务

# models/index_demo.py → 顶部加：
# 📚 [学习资料] 索引性能对比的 3 张演示表（无索引/单列索引/复合索引）
# 配合 index_benchmark.py 和 explain_learning.sql 使用，不影响正常业务

# index_benchmark.py → 顶部加：
# 📚 [学习资料] 索引性能基准测试脚本

# explain_learning.sql → 顶部加：
# 📚 [学习资料] EXPLAIN 执行计划笔记，配合 review_* 三张表使用
```

---

## 开发顺序（12 步）

### 后端基础设施
1. **环境配置 + Alembic 初始化** → `.env` + `config/settings.py` + `requirements.txt` + `docker-compose.yml` 更新 + `alembic init`
2. **结构化日志 + 统一响应 + 安全工具** → `utils/logging.py` + `utils/response.py` + `utils/security.py` + `middleware/auth.py` + `middleware/logging.py`
3. **改造 main.py** → CORS + GZip + RequestID + 异常处理器 + 模型导入 + 路由注册

### 数据模型
4. **所有 ORM 模型（12 张表）** → 第一期 5 张业务表 + 第二期 7 张表壳，含外键、relationship、索引定义
5. **改造 Book 模型** → 加字段、加外键、加 M:N 关系、加索引；`db_conf.py` echo 改环境变量；生成 Alembic 迁移脚本

### API
6. **认证系统** → `routers/auth.py`（register/login/refresh/me）
7. **出版社 + 分类 API** → 两个只读接口
8. **改造 Book API** → 修复 RESTful 问题 + FULLTEXT 搜索 + 联表查询 + `/api/v1` 前缀
9. **书评 API** → 嵌套路由，含每人每书限一条校验（UNIQUE 约束 + IntegrityError 处理）

### 数据初始化
10. **Seed 脚本** → 更新 book seed + 新建 publisher/category seed

### 文档
11. **ARCHITECTURE.md** → 完整项目架构文档（包含后续扩展路线图）

### 前端
12. **Vite + React + Tailwind 工程** → 脚手架 → 布局 → 认证页 → 书籍页 → 书评 → 个人中心

---

## RESTful 规范修复总结

| 问题 | 修复前 | 修复后 |
|------|--------|--------|
| 部分更新用了 PUT | `@router.put("/{book_id}")` | `@router.patch("/{book_id}")` |
| DELETE 声明了 response_model 但返回 204 | `response_model=BookResponse` + `return Response(204)` | 去掉 `response_model`，装饰器设 `status_code=204` |
| 路径无版本前缀 | `/books` | `/api/v1/books` |
| 出版社存为字符串 | `publisher: str` 字段 | `publisher_id` FK → `publisher` 表 |
| 响应格式不统一 | 直接返回对象或手动组装 dict | 统一通过 `utils/response.py` 包裹 |
| 日志用 print() | `print(f"⏱️ ...")` | 用 `logging` 模块 + `X-Request-ID` 链路追踪 |
| 数据库变更无迁移 | `Base.metadata.create_all()` | Alembic 管理 schema 版本 |

---

## 验证方式

1. `docker-compose up -d` 启动 MySQL + Redis + App
2. `alembic upgrade head` 执行数据库迁移
3. 运行 seed 脚本初始化数据
4. `curl localhost:8000/api/v1/books?keyword=Python` 验证搜索和统一响应格式
5. `curl -X POST localhost:8000/api/v1/auth/register` 验证注册
6. `curl -X POST localhost:8000/api/v1/auth/login` 验证登录和 JWT Token
7. 带 Token `curl -X POST localhost:8000/api/v1/books/1/reviews` 验证书评 + 重复提交 409
8. 用 EXPLAIN 检查关键查询是否走了设计的索引
9. `cd frontend && npm run dev` 启动前端，浏览器操作全流程
