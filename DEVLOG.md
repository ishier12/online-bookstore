# 开发日志

> 记录项目中的重要决策、Bug 修复、学到的可复用知识点。
> 每条记录包含：问题/背景 → 分析 → 解决方案 → 可复用知识点。

---

## 2026-07-16：四个 Bug 修复

### Bug 1：书籍列表/详情返回 500 — Decimal JSON 序列化

**现象**：`GET /api/v1/books` 和 `GET /api/v1/books/{id}` 返回 500。

**根因**：
- 数据库 `price` 字段从 `Float` 改为 `DECIMAL(10,2)`
- Pydantic `model_dump()` 输出的是 Python `Decimal` 对象
- `json.dumps()` 和 `JSONResponse` 内部都不认识 `Decimal`

**修复**：用 FastAPI 内置的 `jsonable_encoder()` 包裹内容后再传给 `JSONResponse` 和 `json.dumps()`。

```python
# ❌ 之前
JSONResponse(content=result)
json.dumps(result)

# ✅ 修复后
serializable = jsonable_encoder(result)
JSONResponse(content=serializable)
json.dumps(serializable)
```

**可复用知识点**：
- **存和传是两码事**：数据库用 `DECIMAL` 保证精度（计算不出错），JSON 传 `float`（协议只支持数字）。精度问题只出现在计算时，展示端 `toFixed(2)` 足够。
- FastAPI 的 `jsonable_encoder` 是专门解决「Python 类型 → JSON 兼容类型」转换的工具，遇到 `Decimal`、`datetime`、`UUID` 等类型时用它。

---

### Bug 2：搜索功能返回 500 — FULLTEXT 语法不兼容

**现象**：`GET /api/v1/books?keyword=Python` 返回 500。

**根因**：`func.match().against()` 在当前 SQLAlchemy 2.0.51 中不被支持。

**修复**：改用 `text()` 直接写 SQL。

```python
# ❌ 之前
func.match(Book.book_name, Book.author, Book.description).against(
    text(f"'{keyword}' IN NATURAL LANGUAGE MODE")
)

# ✅ 修复后
text(
    "MATCH(book.book_name, book.author, book.description) "
    "AGAINST (:kw IN NATURAL LANGUAGE MODE)"
).bindparams(kw=keyword.strip())
```

**可复用知识点**：
- SQLAlchemy ORM 的 FULLTEXT 支持因版本而异，`text()` 是兜底方案
- `text()` + `bindparams()` 可以安全拼接参数（防止 SQL 注入）
- 搜索演进路线：`LIKE '%keyword%'` → `FULLTEXT` → `Elasticsearch`，每阶段代码可保留供对比学习

---

### Bug 3：注册功能导致服务器崩溃 — bcrypt 版本不兼容

**现象**：调用 `POST /api/v1/auth/register` 服务器返回 500，之后直接崩溃无法启动。

**根因**：
- bcrypt 5.x 严格限制密码不超过 72 字节
- `passlib` 的 `bcrypt__truncate_secret=True` 在当前版本中不存在
- 语法错误导致 `utils/security.py` import 失败 → 整个应用无法启动

**修复**：在 `hash_password` 和 `verify_password` 中手动截断。

```python
# ❌ 之前
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto",
                           bcrypt__truncate_secret=True)

# ✅ 修复后
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password.encode()[:72])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password.encode()[:72], hashed_password)
```

**可复用知识点**：
- bcrypt 的 72 字节限制是算法本身的设计，不是 bug
- `passlib` 和 `bcrypt` 是两个独立的库，版本组合可能导致不兼容
- 一个模块 import 失败会导致整个应用无法启动（FastAPI 在启动时加载所有路由依赖链）

---

### Bug 4：书籍详情返回 500 — 异步 Session 懒加载

**现象**：`GET /api/v1/books/{id}` 返回 500。错误日志：`MissingGreenlet: greenlet_spawn has not been called`。

**根因**：
- `Category.children` 关系设为 `lazy="selectin"`
- `get_book_with_relations` 只预加载了 `Book.categories`，没预加载 `Category.children`
- Pydantic `model_validate()` 序列化时访问 `category.children`，触发懒加载
- 此时 async session 已提交/关闭，SQLAlchemy 无法发起新查询

**修复**：查询时链式预加载子分类。

```python
# ❌ 之前
.options(
    joinedload(Book.publisher),
    selectinload(Book.categories),        # 只加载了分类本身
)

# ✅ 修复后
.options(
    joinedload(Book.publisher),
    selectinload(Book.categories).selectinload(Category.children),  # 链式预加载子分类
)
```

**可复用知识点**：
- SQLAlchemy async 模式下，所有数据库访问必须在 async session 生命周期内
- Pydantic `model_validate(orm_obj)` 会遍历 ORM 对象的所有字段，触发未加载的 relationship
- **黄金法则**：序列化之前，确保所有需要的关联数据已通过 `joinedload` / `selectinload` 预加载
- `selectinload` 可以链式调用：`.selectinload(A.bs).selectinload(B.cs)` 一次加载三层

---

## 2026-07-16：API 版本管理与前端部署

### 决策：API 使用 `/api/v1/` 前缀

**为什么**：
- API 版本号管理的是「契约变更」（改了请求/响应格式），不是「实现变更」（换了内部引擎）
- LIKE → FULLTEXT → Elasticsearch 是内部实现变更，不需要 `/v2`；但如果把 `keyword` 改名为 `q`，就需要 `/v2`

**可复用知识点**：
- **API 版本号 ≠ 功能迭代号**。只有当旧客户端调不通时才需要新版本
- 前端只需在一处配置 `baseURL`，切换版本只改一行
- Git tag 用于版本控制（`v1.0.0` → `v1.1.0` → `v2.0.0`），与前端 `package.json` 的 `version` 字段无关

### 决策：Monorepo 平级结构

**为什么**：
- `backend/` 和 `frontend/` 平级是 GitHub 上全栈项目的标准布局
- 一个 `docker-compose.yml` 编排所有服务
- 比「后端在根目录」更清晰，比「多仓库」更简单

---

## 2026-07-16：数据库设计

### 索引命名规范

```
uk_  → UNIQUE KEY     (uk_username)
fk_  → FOREIGN KEY    (fk_publisher_id)
idx_ → 普通索引        (idx_price)
ft_  → FULLTEXT       (ft_book)
```

### 复合索引的最左前缀原则

`INDEX idx_book_price (book_name, price)` — 等值列在前，范围列在后。
- `WHERE book_name = ? AND price >= ?` → 走索引 ✅
- `WHERE price >= ?` → 不走索引 ❌（跳过了第一列）

### 搜索演进三段式

`LIKE '%keyword%'`（全表扫描）→ `FULLTEXT`（倒排索引）→ `Elasticsearch`（专用搜索引擎）
每段代码保留在 `crud/book.py` 供对比学习。

---

## 2026-07-16：Docker 与数据持久化

**可复用知识点**：
- 容器名 ≠ 项目名。Docker Compose 项目名来自文件夹名
- `docker compose down` 删容器，Volume 保留；加 `-v` 才删 Volume（即删数据）
- 日常开发用 `docker compose stop/up`，Volume 一直在，数据不会丢
- 容器间通信用 `服务名:容器端口`（如 `mysql:3306`），宿主机访问用 `localhost:映射端口`（如 `localhost:3307`）

---

## 待续

后续决策和知识点将持续补充到此文件。
