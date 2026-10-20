"""
Database operations package.
使用 PostgreSQL 存储用户与预约数据，
按职责拆分为 user / reservation / pgsql_config 模块。

"""

from .zone import add_zone, get_zones_by_space
from .pgsql_client import initialize_database
from .pgsql_config import get_connection, get_db_connection
from .reservation import (
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
from .space import add_space, delete_space_by_id, get_all_spaces
from .user import search_user_by_name, upsert_user

__version__ = "2.0.0"
__author__ = "Order Management System"

__all__ = [
    "add_zone",
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
    "add_zone",
    "get_zones_by_space",
    "add_space",
    "delete_space_by_id",
    "get_all_spaces",
]
