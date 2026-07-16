"""
结构化日志配置模块
- 替代项目中的 print() 调用，统一使用 logging
- 每个请求自动携带唯一的 request_id，方便追踪整条请求链路
- 生产环境可切换为 JSON 格式输出，对接 ELK / Loki 等日志平台

使用方式：
    from utils.logging import logger
    logger.info("用户登录成功", extra={"username": "zhangsan"})
"""

import logging
import sys

# 日志格式：时间 | 级别 | request_id | 模块:行号 | 消息
LOG_FORMAT = (
    "%(asctime)s | %(levelname)-7s | %(request_id)-36s | "
    "%(name)s:%(lineno)d | %(message)s"
)


class RequestIDFilter(logging.Filter):
    """
    从当前请求上下文中获取 request_id 注入到日志记录中
    如果没有（如启动时的日志），显示 ----------
    """

    def filter(self, record):
        # 尝试从 logging 的全局变量获取 request_id（由 RequestIDMiddleware 设置）
        record.request_id = getattr(logging, "_request_id", "----------")
        return True


def setup_logging():
    """初始化全局日志配置，在应用启动时调用一次"""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    handler.addFilter(RequestIDFilter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # 避免重复添加 handler（uvicorn reload 时可能多次调用）
    if not root.handlers:
        root.addHandler(handler)

    # 降低 uvicorn 的日志级别，避免重复打印请求信息
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    return logging.getLogger("bookstore")


# 模块级 logger，其他地方直接 import 使用
logger = logging.getLogger("bookstore")
