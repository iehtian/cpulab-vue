"""
Database operations package.
使用 PostgreSQL 存储用户与预约数据，
按职责拆分为 user / reservation / pgsql_config 模块。

"""

from .pgsql_client import initialize_database
from .pgsql_config import get_connection, get_db_connection
from .reservation import (
    create_booking_index,
    create_date_plan_index,
    delete_booking_by_id,
    delete_bookings_by_dates,
    delete_bookings_by_slots,
    delete_user_data,
    get_all_dateinfo_by_date,
    get_dateinfo,
    search_booking_by_date,
    search_booking_by_user_and_date,
    search_booking_users_by_range,
    upsert_booking,
    upsert_plan_field,
)
from .space import get_all_spaces, upsert_space
from .user import create_user_index, search_user_by_name, upsert_user

__version__ = "2.0.0"
__author__ = "Order Management System"

__all__ = [
    "create_booking_index",
    "create_date_plan_index",
    "create_user_index",
    "delete_booking_by_id",
    "delete_bookings_by_dates",
    "delete_bookings_by_slots",
    "delete_user_data",
    "get_all_dateinfo_by_date",
    "get_connection",
    "get_dateinfo",
    "get_db_connection",
    "initialize_database",
    "search_booking_by_date",
    "search_booking_by_user_and_date",
    "search_booking_users_by_range",
    "search_user_by_name",
    "upsert_booking",
    "upsert_plan_field",
    "upsert_user",
    "upsert_space",
    "get_all_spaces",
]
