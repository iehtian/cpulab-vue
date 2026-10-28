from database.pgsql_config import (
    REAGENT_TABLE,
    REAGENT_USAGE_TABLE,
    USER_TABLE,
    get_connection,
)
from log_config import logger


def create_reagent_usage():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {REAGENT_USAGE_TABLE} (
                id SERIAL PRIMARY KEY,
                reagent_id INTEGER REFERENCES {REAGENT_TABLE}(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES {USER_TABLE}(id) ON DELETE SET NULL,
                usage_time TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours'),
                UNIQUE (reagent_id, user_id, usage_time)
            )
            """
        )
        conn.commit()
    logger.info(f"Table '{REAGENT_USAGE_TABLE}' ensured.")


def add_reagent_usage(reagent_id, user_id, usage_date=None):
    """插入试剂使用记录"""

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {REAGENT_USAGE_TABLE} (reagent_id, user_id, usage_time)
            VALUES (%s, %s, %s)
            ON CONFLICT (reagent_id, user_id, usage_time) DO NOTHING
            """,
            (
                reagent_id,
                user_id,
                usage_date,
            ),
        )
        conn.commit()
    logger.info(
        f"Reagent usage record upserted for reagent_id={reagent_id}, user_id={user_id}."
    )


def get_reagent_usage(reagent_id):
    """获取指定试剂的使用记录"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT user_id, usage_time
            FROM {REAGENT_USAGE_TABLE}
            WHERE reagent_id = %s
            ORDER BY usage_time DESC
            """,
            (reagent_id,),
        )
        records = cur.fetchall()
        lenth = len(records)
        last_record = records[0] if lenth > 0 else None

    return {"length": lenth, "last_record": last_record}
