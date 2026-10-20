import psycopg2

from database.zone import create_zone
from database.reagent import create_reagent
from database.reservation import create_booking_index, create_date_plan_index
from database.space import create_space
from database.user import create_user_index
from log_config import logger


# -------- 初始化 --------
def initialize_database():
    try:
        create_user_index()
        create_booking_index()
        create_date_plan_index()
        create_space()
        create_zone()
        create_reagent()
        return True
    except psycopg2.Error as e:
        logger.error(f"数据库初始化失败: {e}")
        return False
