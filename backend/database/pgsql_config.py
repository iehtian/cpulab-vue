from collections.abc import Generator
from contextlib import contextmanager
from typing import Any, LiteralString, cast

import psycopg
from psycopg import sql as _sql

DB_CONFIG: dict[str, Any] = {
    "host": "localhost",
    "user": "cpulab_user",
    "password": "cpulab_pass",
    "dbname": "cpulab",
    "port": 5435,
}

USER_TABLE = "users"
BOOKING_TABLE = "bookings"
PLANS_TABLE = "date_plans"
SPACE_TABLE = "spaces"
ZONE_TABLE = "zones"
REAGENT_TABLE = "reagents"
REAGENT_CATEGORY_TABLE = "reagent_categories"
REAGENT_USAGE_TABLE = "reagent_usage"


OAUTH_CLIENT_TABLE = "oauth_clients"


@contextmanager
def get_connection() -> Generator[psycopg.Connection, None, None]:
    """事务作用域连接：正常退出自动提交，异常自动回滚，结束自动关闭。"""
    with psycopg.connect(**DB_CONFIG) as conn:
        yield conn


def dynamic_sql(query: str) -> _sql.SQL:
    """包装动态拼接的 SQL，以满足 psycopg 对 LiteralString 的类型要求。

    安全约定：标识符（表名/列名）只能来自本模块的常量，值一律通过 %s 参数化传入。
    """
    return _sql.SQL(cast("LiteralString", query))
