from collections.abc import Iterator
from contextlib import contextmanager

import psycopg

DB_CONFIG = {
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


@contextmanager
def get_connection() -> Iterator[psycopg.Connection]:
    """事务作用域连接：正常退出自动提交，异常自动回滚，结束自动关闭。"""
    with psycopg.connect(**DB_CONFIG) as conn:
        yield conn
