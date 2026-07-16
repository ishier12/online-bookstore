# 项目审计报告

> 2026-07-16，全面审阅前后端代码，检查 API 对齐、功能完整度、代码质量。

## 发现汇总：25 个问题

| 严重度 | 数量 | 
|:---:|:---:|
| Critical | 2 |
| Major | 9 |
| Minor | 14 |

---

## Critical（影响安全或核心功能缺失）

**#1 — POST/PATCH/DELETE /books 无鉴权**
`backend/routers/book.py:126-191`。任何人可增删改书籍。需加 `Depends(get_current_user)`。

**#2 — 前端无出版社 API**
`GET /api/v1/publishers` 后端有但没有 `frontend/src/api/publishers.ts`，也没有出版社页面。

---

## Major（影响用户体验或功能完整性）

**#3 — 首页无分类浏览入口**

**#4 — 首页无错误处理**（API 失败时永久转圈）

**#5 — 书籍详情的分类标签不可点击**（纯 `<span>`，不是 `<Link>`）

**#6 — 书籍详情的出版社不可点击**（纯文本）

**#7 — 后端缺 `GET /publishers/{id}/books`**（出版社是死胡同）

**#8 — 书评提交后未淘汰书详情缓存**（均分 5 分钟内显示旧值）

**#9 — BookListPage 搜索流程**：`useEffect` 只依赖 `[page]`，改筛选条件不触发查询

**#10 — 分类下拉只显示子分类**，顶级分类不可选

**#11 — Navbar 无分类导航**

---

## Minor

**#12** — `auth.ts` 未导出 `refreshToken()`
**#13** — HomePage 无空状态提示
**#14** — `get_optional_user` 中间件未使用
**#15** — `schemas/common.py` 的 wrapper 类未使用
**#16** — `schemas/user.py` 的 `TokenResponse` 未使用
**#17** — `schemas/book.py` 的 `BookPage` 未使用
**#18** — `routers/book.py` 的 `from decimal import Decimal` 未使用
**#19** — `routers/review.py` 的 `get_optional_user` import 未使用
**#20** — `routers/review.py` 的 `success_response` import 未使用
**#21** — `format.ts` 的 `truncate()` 未被调用
**#22** — 204 DELETE 响应与 axios `response.data.data` 解包可能冲突
**#23** — 出版社/分类列表无分页
**#24** — 部分 Schema 已定义但路由手动构建响应
**#25** — BookCard 未显示评分

---

## 修复状态

| 轮次 | 问题 | 状态 |
|------|------|:--:|
| 第一轮 | #1, #2, #8 (Critical + 缓存) | ⏳ |
| 第二轮 | #3-#11 (Major) | ⏳ |
| 第三轮 | #12-#25 (Minor) | ⏳ |
