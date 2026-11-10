"""
Database operations package.
使用 PostgreSQL 存储用户与预约数据，
按职责拆分为 user / reservation / pgsql_config 模块。

"""

from .oauth import create_client, create_oauth_client_table, get_client
from .pgsql_client import initialize_database
from .pgsql_config import get_connection
from .reagent_usage import (
    add_reagent_usage,
    get_reagent_usage,
    get_reagent_usage_list,
    open_reagent,
)
from .reagents import (
    delete_reagent_by_id,
    get_frequently_used_reagents,
    get_need2restock_reagents,
    get_reagents_by_zone,
    set_needs_restock,
    update_open_date,
    upsert_reagent,
)
from .reservation import (
    delete_booking_by_id,
    delete_bookings_by_dates,
    delete_bookings_by_slots,
    delete_user_daily_plans,
    get_booking_users_by_range,
    get_bookings_by_date,
    get_bookings_by_user_and_date,
    get_daily_plan,
    get_daily_plans_by_date,
    upsert_booking,
    upsert_plan_field,
)
from .space import add_space, delete_space_by_id, get_all_spaces
from .user import search_user_by_name, upsert_user
from .zone import add_zone, get_zones_by_space

__version__ = "2.0.0"

__all__ = [
    "add_reagent_usage",
    "add_space",
    "add_zone",
    "create_client",
    "create_oauth_client_table",
    "delete_booking_by_id",
    "delete_bookings_by_dates",
    "delete_bookings_by_slots",
    "delete_reagent_by_id",
    "delete_space_by_id",
    "delete_user_daily_plans",
    "get_all_spaces",
    "get_booking_users_by_range",
    "get_bookings_by_date",
    "get_bookings_by_user_and_date",
    "get_client",
    "get_connection",
    "get_daily_plan",
    "get_daily_plans_by_date",
    "get_frequently_used_reagents",
    "get_need2restock_reagents",
    "get_reagent_usage",
    "get_reagents_by_zone",
    "get_zones_by_space",
    "initialize_database",
    "open_reagent",
    "search_user_by_name",
    "set_needs_restock",
    "update_open_date",
    "upsert_booking",
    "upsert_plan_field",
    "upsert_reagent",
    "upsert_user",
    "get_reagent_usage_list",
]
