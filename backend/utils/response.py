"""
统一响应工具函数
所有 API 端点返回的 JSON 都通过这两个函数构建，保证前端对接时有统一的格式约定

成功响应：
    { "code": 200, "message": "success", "data": {...} }
分页响应：
    { "code": 200, "message": "success", "data": { "items": [...], "total": N, "page": N, "page_size": N } }
错误响应：
    由 FastAPI 异常处理器统一处理，格式为 { "code": status_code, "message": "...", "data": null }
"""

from typing import Any, Optional


def success_response(data: Any = None, message: str = "success") -> dict:
    """构建成功响应"""
    return {
        "code": 200,
        "message": message,
        "data": data,
    }


def created_response(data: Any = None, message: str = "created") -> dict:
    """构建 201 创建成功响应"""
    return {
        "code": 201,
        "message": message,
        "data": data,
    }


def paginated_response(
    items: list,
    total: int,
    page: int,
    page_size: int,
    message: str = "success",
) -> dict:
    """构建分页响应"""
    return {
        "code": 200,
        "message": message,
        "data": {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
        },
    }


def error_response(code: int, message: str, detail: Any = None) -> dict:
    """构建错误响应（通常由异常处理器调用，路由中一般不需要手动调用）"""
    return {
        "code": code,
        "message": message,
        "data": detail,
    }
