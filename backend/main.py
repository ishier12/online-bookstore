"""
应用入口模块
- 创建 FastAPI 实例
- 注册中间件（洋葱模型：CORS → RequestID → GZip → Timing）
- 注册所有路由
- 配置全局异常处理器
- 定义启动/关闭事件

中间件执行顺序（请求 ↓，响应 ↑）：
    CORS → RequestID → GZip → Timing → 路由处理函数
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

from config.settings import settings
from config.db_conf import engine, Base
from config.redis import init_redis, close_redis
from middleware.timing import TimingMiddleware
from middleware.logging import RequestIDMiddleware
from utils.logging import setup_logging, logger

# ====== 导入所有模型（按导入顺序会在 Base.metadata 中注册，Alembic 和 create_all 都依赖此 metadata）======
import models.book          # 业务表：书籍
import models.user          # 业务表：用户
import models.publisher     # 业务表：出版社
import models.category      # 业务表：分类
import models.review        # 业务表：书评
# 第二期表（只建表，无 API）
import models.cart          # 🔲 购物车
import models.address       # 🔲 收货地址
import models.order         # 🔲 订单
import models.payment       # 🔲 支付
import models.user_favorite # 🔲 收藏

# ====== 路由导入 ======
from routers.book import router as book_router
from routers.auth import router as auth_router
from routers.publisher import router as publisher_router
from routers.category import router as category_router
from routers.review import router as review_router

# ====== 初始化日志 ======
setup_logging()

# ====== 创建 FastAPI 实例 ======
app = FastAPI(
    title="在线书店 API",
    description="全栈学习项目 — FastAPI + SQLAlchemy + Redis + React",
    version="1.0.0",
)

# ====== 注册中间件（洋葱模型：先 add 的在外层） ======

# 1. CORS — 跨域资源共享（前后端分离必须）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request ID — 为每个请求生成唯一追踪 ID
app.add_middleware(RequestIDMiddleware)

# 3. GZip — 大于 1000 字节的响应体自动压缩
app.add_middleware(GZipMiddleware, minimum_size=1000)

# 4. Timing — 记录请求耗时（自定义中间件，最内层最靠近业务）
app.add_middleware(TimingMiddleware)

# 后续可随时插入：TrustedHostMiddleware、SessionMiddleware、自定义限流中间件等


# ====== 全局异常处理器 ======

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Pydantic 请求体校验失败 → 422"""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
        })
    logger.warning(f"请求校验失败: {errors}")
    return JSONResponse(
        status_code=422,
        content={"code": 422, "message": "请求参数校验失败", "data": {"errors": errors}},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """未捕获的异常 → 500"""
    logger.exception(f"未处理的异常: {exc}")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "data": None},
    )


# ====== 注册路由 ======
app.include_router(auth_router)        # /api/v1/auth/*
app.include_router(book_router)        # /api/v1/books/*
app.include_router(review_router)      # /api/v1/books/{book_id}/reviews
app.include_router(publisher_router)   # /api/v1/publishers
app.include_router(category_router)    # /api/v1/categories


# ====== 建表函数 ======
async def create_tables():
    """在数据库中创建所有尚未存在的表（开发阶段用，生产环境应用 Alembic 替代）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ====== 启动事件 ======
@app.on_event("startup")
async def startup_event():
    """FastAPI 启动时：建表 + 连接 Redis"""
    logger.info("应用启动中...")
    # 开发阶段用 create_all 建表，后续用 Alembic 管理变更
    # await create_tables()
    await init_redis()
    logger.info("应用启动完成")


@app.on_event("shutdown")
async def shutdown_event():
    """FastAPI 关闭时释放 Redis 连接"""
    logger.info("应用关闭中...")
    await close_redis()
    logger.info("应用已关闭")


# ====== 根路由 ======
@app.get("/")
async def root():
    return {"message": "在线书店 API", "docs": "/docs", "version": "1.0.0"}
