"""
请求耗时中间件
功能：
  - 记录每次请求的处理时间
  - 输出到终端（对所有路由生效）
"""

import time
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        elapsed = (time.perf_counter() - start) * 1000  # 转毫秒

        print(f"⏱️ {request.method} {request.url.path} - {response.status_code} - {elapsed:.1f}ms")
        response.headers["X-Process-Time"] = f"{elapsed:.1f}ms"
        return response
