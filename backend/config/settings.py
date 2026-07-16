"""
集中配置模块
从环境变量 / .env 文件加载所有配置项，其他模块统一从这里读取配置
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """应用配置"""
    # 数据库
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "mysql+aiomysql://root:demo000@localhost:3307/bookstore"
    )
    DB_ECHO: bool = os.getenv("DB_ECHO", "false").lower() == "true"

    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-secret-change-me")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(
        os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7")
    )

    # CORS
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")


settings = Settings()
