from database.pgsql_config import (
    REAGENT_TABLE,
    REAGENT_USAGE_TABLE,
    USER_TABLE,
    dynamic_sql,
    get_connection,
)
from log_config import logger


def create_reagent_usage():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            CREATE TABLE IF NOT EXISTS {REAGENT_USAGE_TABLE} (
                id SERIAL PRIMARY KEY,
                reagent_id INTEGER REFERENCES {REAGENT_TABLE}(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES {USER_TABLE}(id) ON DELETE SET NULL,
                event_type SMALLINT NOT NULL, -- 1=取用, 2=开屏贴标设置总量
                amount NUMERIC, -- 取用量或修改总量
                remaining_after NUMERIC, -- 余量
                usage_time TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours'),
                UNIQUE (reagent_id, user_id, usage_time)
            )
            """)
        )
        cur.execute(
            dynamic_sql(f"""
            CREATE UNIQUE INDEX idx_usage_open_once
            ON {REAGENT_USAGE_TABLE} (reagent_id)
            WHERE event_type = 2
            """)
        )

    logger.info(f"Table '{REAGENT_USAGE_TABLE}' ensured.")


def open_reagent(reagent_id, user_id):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            SELECT id,capacity,bottle_count FROM {REAGENT_TABLE} WHERE id = %s FOR UPDATE
            """),
            (reagent_id,),
        )
        result = cur.fetchone()
        if result is None:
            raise ValueError(f"Reagent with id {reagent_id} does not exist.")
        capacity = None
        if result[1] is not None and result[2] is not None:
            capacity = result[1] * result[2]

        cur.execute(
            dynamic_sql(f"""
            INSERT INTO {REAGENT_USAGE_TABLE} (reagent_id, user_id, event_type, amount)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (reagent_id) WHERE event_type = 2 DO NOTHING
            """),
            (reagent_id, user_id, 2, capacity),
        )
    logger.info(f"Reagent opened for reagent_id={reagent_id}, user_id={user_id}.")


def add_reagent_usage(reagent_id, user_id, event_type, amount=None):
    """插入试剂使用记录"""

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            SELECT id FROM {REAGENT_TABLE} WHERE id = %s FOR UPDATE
            """),
            (reagent_id,),
        )
        if cur.fetchone() is None:
            raise ValueError(f"Reagent with id {reagent_id} does not exist.")

        cur.execute(
            dynamic_sql(f"""
            SELECT reagent_id FROM {REAGENT_USAGE_TABLE} WHERE reagent_id = %s AND event_type = 2
            """),
            (reagent_id,),
        )
        if cur.fetchone() is None:
            raise ValueError(f"Reagent with id {reagent_id} has not been opened yet")

        cur.execute(
            dynamic_sql(f"""
            SELECT remaining_after FROM {REAGENT_USAGE_TABLE}
            WHERE reagent_id = %s
            ORDER BY usage_time DESC
            LIMIT 1
            """),
            (reagent_id,),
        )
        last_record = cur.fetchone()
        last_remainder = last_record[0] if last_record else None

        if event_type == 1:
            new_remainder = (
                last_remainder - amount if last_remainder is not None else None
            )
        else:
            new_remainder = amount if amount is not None else None

        cur.execute(
            dynamic_sql(f"""
            INSERT INTO {REAGENT_USAGE_TABLE} (reagent_id, user_id, event_type, amount, remaining_after)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (reagent_id, user_id, usage_time) DO NOTHING
            """),
            (
                reagent_id,
                user_id,
                event_type,
                amount,
                new_remainder,
            ),
        )
    logger.info(
        f"Reagent usage record upserted for reagent_id={reagent_id}, user_id={user_id}."
    )


def get_reagent_usage(reagent_id):
    """获取指定试剂的使用记录"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            SELECT user_id, usage_time, remaining_after
            FROM {REAGENT_USAGE_TABLE}
            WHERE reagent_id = %s
            ORDER BY usage_time DESC
            """),
            (reagent_id,),
        )
        records = cur.fetchall()
        lenth = len(records)
        last_record = records[0] if lenth > 0 else None
        remainder = last_record[2] if last_record else None
    return {"length": lenth, "last_record": last_record, "remainder": remainder}
