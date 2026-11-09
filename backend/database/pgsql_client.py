import psycopg

from database.oauth import create_oauth_client_table
from database.reagent_usage import create_reagent_usage_table
from database.reagents import create_reagent_table
from database.reservation import create_booking_table, create_daily_plan_table
from database.space import create_space_table
from database.user import create_user_table
from database.zone import create_zone_table
from log_config import logger


# -------- 初始化 --------
def initialize_database():
    try:
        create_user_table()
        create_booking_table()
        create_daily_plan_table()
        create_space_table()
        create_zone_table()
        create_reagent_table()
        create_reagent_usage_table()
        create_oauth_client_table()
        return True
    except psycopg.Error as e:
        logger.error(f"数据库初始化失败: {e}")
        return False
