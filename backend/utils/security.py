"""
安全工具模块
- 密码哈希与验证（bcrypt）
- JWT Token 生成与解码（Access Token + Refresh Token）
"""

from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from config.settings import settings

# ====== 密码哈希 ======
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """
    对明文密码进行 bcrypt 哈希
    bcrypt 5.x 限制密码不超过 72 字节，超出部分手动截断
    """
    return pwd_context.hash(password.encode()[:72])


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证明文密码是否与哈希值匹配"""
    return pwd_context.verify(plain_password.encode()[:72], hashed_password)


# ====== JWT ======

def create_access_token(data: dict) -> str:
    """
    创建 Access Token（短期有效，每次请求携带）
    过期时间由 ACCESS_TOKEN_EXPIRE_MINUTES 配置，默认 30 分钟
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    创建 Refresh Token（长期有效，仅用于刷新 Access Token）
    过期时间由 REFRESH_TOKEN_EXPIRE_DAYS 配置，默认 7 天
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    """
    解码并验证 JWT Token
    成功返回 payload 字典，失败（过期/伪造/签名不匹配）返回 None
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
