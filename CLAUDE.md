# CLAUDE.md — 项目约束与规范

> Claude Code 在每次会话启动时自动读取此文件，并遵守其中约束。

## 项目概述

全栈在线书店（Monorepo: backend/FastAPI + frontend/React + MySQL + Redis）。
详细架构见 `ARCHITECTURE.md`，开发决策见 `DEVLOG.md`，审计发现见 `AUDIT.md`。

## 绝对不可删除或修改

以下内容在**任何情况下不得删除、重命名或修改其核心结构**：

### 第二期预留表（🔲 标记）
```
models/cart.py          — Cart + CartItem（购物车）
models/address.py       — Address（收货地址）
models/order.py         — Order + OrderItem（订单）
models/payment.py       — Payment（支付）
models/user_favorite.py — UserFavorite（收藏）
```
这些表已经建好 ORM 模型，但**没有 API、没有前端页面**。第二期会用到。
在 `main.py`、`seed_all.py`、`alembic/env.py` 中必须有对应的 import 和 `# 🔲 第二期` 注释标记。

### 学习资料（📚 标记）
**已从当前项目移除**，仅存在于旧仓库 `fast-api_demo` 的历史中。

### 核心文件
- `backend/config/db_conf.py` — ORM 基类，所有模型继承它
- `backend/middleware/timing.py` — 自定义中间件，学习用
- `ARCHITECTURE.md`、`DESIGN.md`、`DEVLOG.md`、`AUDIT.md` — 文档体系

## 重写文件时的检查清单

当需要完整重写一个文件（而非局部修改）时，必须先：

1. **Read 原文件**，确认所有 import、注释标记（🔲📚）、函数签名
2. **对比周边文件**，确认该文件被哪些模块引用
3. **保留所有标记**：`# 🔲 第二期`、`# 📚 [学习资料]`
4. 重写后 `grep` 检查原文件中的关键字符串是否都在新文件中出现

## 编码规范

### Python 后端
- 所有 ORM 模型继承 `config.db_conf.Base`（自动获得 created_at/updated_at）
- 异步全链路：`create_async_engine` → `AsyncSession` → `redis.asyncio`
- JWT 双 Token：Access 30min + Refresh 7天（详见 memory `jwt-dual-token-strategy.md`）
- 密码哈希：`password.encode()[:72]` 截断（bcrypt 5.x 限制）
- API 响应统一包裹：`{ "code": 200, "data": ..., "message": "success" }`
- 索引命名：`uk_`(唯一)、`fk_`(外键)、`idx_`(普通)、`ft_`(全文)
- 前端请求走 Vite 代理 `/api` → `localhost:8000`

### TypeScript 前端
- API 调用统一通过 `api/client.ts`（baseURL `/api/v1`）
- 所有 API 函数放在 `api/` 目录对应文件中
- 每个后端端点必须有对应的前端 API 函数（即使暂未使用）

### 数据库
- 价格字段：`DECIMAL(10,2)` + Python `Decimal` 类型
- JSON 序列化必须用 `jsonable_encoder()` 包裹（Decimal 不兼容标准 json.dumps）

### 种子数据
- 统一入口：`backend/seed_all.py`
- 真实书店场景：书籍覆盖文学小说、人文社科、经济管理、科学技术、生活休闲、艺术设计六大类
- 50 本精选（真实书名）+ 250 本随机生成 = 300 本总计

## 语义化版本

- `v0.x` — 开发阶段，API 不稳定，功能持续迭代
- `v1.0.0` — 第一个稳定版（API 承诺不变，向后兼容）
- `v1.x.0` — 新增功能，不影响旧客户端（如 LIKE→FULLTEXT，API 契约不变）
- `v2.0.0` — 不兼容的 API 变更（如改字段名、删端点、改响应格式）
- 用 `git tag` 打版本：`git tag v0.1.0 && git push --tags`
- 前端 `package.json` 的 `version` 字段与版本控制无关，那是给 npm 发包用的

## Git 提交规范

- 使用约定式提交：`feat:` / `fix:` / `docs:` / `refactor:` / `chore:`
- 提交信息用中文，body 详细列出变更内容

## 后续学习路线

详见 memory `learning-roadmap.md`。简要顺序：
1. 第二期（Celery + 订单/购物车/支付）
2. Elasticsearch（替换 FULLTEXT 搜索）
3. Kafka（替换 Celery broker）
4. Nacos（微服务拆分后）
