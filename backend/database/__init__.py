"""
Database operations package for order management system.
This package now uses PostgreSQL for users and bookings to replace Redis.
"""

import psycopg2

from .pgsql_client import (
    create_booking_index,
    create_date_plan_index,
    create_user_index,
    delete_bookings_by_dates,
    delete_bookings_by_slots,
    get_all_dateinfo_by_date,
    get_dateinfo,
    get_db_connection,
    search_booking_by_date,
    search_booking_by_user_and_date,
    search_booking_users_by_range,
    search_user_by_name,
    upsert_booking,
    upsert_plan_field,
    upsert_user,
)

# 包版本信息
__version__ = "1.0.0"
__author__ = "Order Management System"


# 包级别的初始化函数
def initialize_database():
    """初始化数据库索引"""
    try:
        create_user_index()
        create_booking_index()
        create_date_plan_index()
        conn = get_db_connection()
        conn.close()
        print("📊 Database indexes initialized successfully!")
        return True
    except psycopg2.Error as e:
        print(f"❌ Database initialization failed: {e}")
        return False


# 导出所有公共接口
__all__ = [
    "create_date_plan_index",
    "delete_bookings_by_dates",
    "delete_bookings_by_slots",
    "get_all_dateinfo_by_date",
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
]
