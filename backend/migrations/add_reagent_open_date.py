"""一次性迁移脚本: 给试剂表补 open_date(开瓶贴标日期) 字段, 并移除误加的 manufacturer 列"""

from database.pgsql_config import REAGENT_TABLE, get_connection
from log_config import logger


def migrate():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            ALTER TABLE {REAGENT_TABLE}
            ADD COLUMN IF NOT EXISTS open_date DATE
            """
        )
        cur.execute(
            f"""
            ALTER TABLE {REAGENT_TABLE}
            DROP COLUMN IF EXISTS manufacturer
            """
        )
    logger.info(f"Column 'open_date' ensured, 'manufacturer' dropped on table '{REAGENT_TABLE}'.")


if __name__ == "__main__":
    migrate()
