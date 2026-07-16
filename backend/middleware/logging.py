"""
Request ID 中间件
为每个 HTTP 请求生成唯一的 X-Request-ID，注入到：
1. 响应头 X-Request-ID（前端可以拿到）
2. 日志的 request_id 字段（方便 grep 追踪单次请求的所有日志）

配合 utils/logging.py 使用
"""

import logging
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class RequestIDMiddleware(BaseHTTPMiddleware):
    """每个请求生成唯一 ID，贯穿整个请求生命周期"""

    async def dispatch(self, request: Request, call_next):
        # 优先使用客户端传过来的 X-Request-ID（如 Nginx / 前端设置），否则自己生成
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        # 将 request_id 注入到 logging 全局变量中
        logging._request_id = request_id

        response = await call_next(request)

        # 响应头也带上，前端可以拿到用于问题排查
        response.headers["X-Request-ID"] = request_id
        return response
