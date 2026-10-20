"""工具函数：密码散列、随机颜色、Cookie 设置、统一错误响应。"""

import random

import bcrypt
from flask import jsonify

from log_config import logger


def fail(message: str, status: int = 400):
    """统一的错误响应：HTTP 状态码 + {"message": ...}"""
    return jsonify({"message": message}), status


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except ValueError as e:
        logger.error("密码验证异常: {}", e)
        return False


def random_color() -> str:
    colors = [
        "#FFC48A",
        "#79CB9B",
        "#4292C5",
        "#FFAEB0",
        "#F28147",
        "#90BFF9",
        "#8B90CE",
    ]
    return random.choice(colors)


DEFAULT_COOKIE_OPTIONS = {
    "httponly": True,
    "secure": True,
    "samesite": "Lax",
    "max_age": 30 * 24 * 60 * 60,
}


def set_cookie_with_defaults(response, key, value, **overrides):
    options = {**DEFAULT_COOKIE_OPTIONS, **overrides}
    response.set_cookie(key, value, **options)
    return response
