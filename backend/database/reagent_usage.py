from database.pgsql_config import (
    REAGENT_TABLE,
    REAGENT_USAGE_TABLE,
    USER_TABLE,
    dynamic_sql,
    get_connection,
)
from log_config import logger

# 使用记录的事件类型
EVENT_USE = 1  # 取用
EVENT_OPEN = 2  # 开瓶贴标设置总量


def create_reagent_usage_table():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            CREATE TABLE IF NOT EXISTS {REAGENT_USAGE_TABLE} (
                id SERIAL PRIMARY KEY,
                reagent_id INTEGER REFERENCES {REAGENT_TABLE}(id) ON DELETE CASCADE,
                user_id INTEGER REFERENCES {USER_TABLE}(id) ON DELETE SET NULL,
                event_type SMALLINT NOT NULL, -- 1=取用, 2=开瓶贴标设置总量
                amount NUMERIC, -- 取用量或修改总量
                remaining_after NUMERIC, -- 余量
                usage_time TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours'),
                UNIQUE (reagent_id, user_id, usage_time)
            )
            """)
        )
        cur.execute(
            dynamic_sql(f"""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_usage_open_once
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
            raise ValueError("该试剂不存在或已被删除")
        capacity = None
        if result[1] is not None and result[2] is not None:
            capacity = result[1] * result[2]

        cur.execute(
            dynamic_sql(f"""
            INSERT INTO {REAGENT_USAGE_TABLE} (reagent_id, user_id, event_type, amount, remaining_after)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (reagent_id) WHERE event_type = 2 DO NOTHING
            """),
            (reagent_id, user_id, EVENT_OPEN, 0, capacity),
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
            raise ValueError("该试剂不存在或已被删除")

        cur.execute(
            dynamic_sql(f"""
            SELECT reagent_id FROM {REAGENT_USAGE_TABLE} WHERE reagent_id = %s AND event_type = 2
            """),
            (reagent_id,),
        )
        if cur.fetchone() is None:
            raise ValueError("该试剂尚未开封，无法记录使用")

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

        if event_type == EVENT_USE:
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
            SELECT COUNT(*) OVER () AS usage_count,
                   u.user_name,
                   r.remaining_after
            FROM {REAGENT_USAGE_TABLE} r
            LEFT JOIN {USER_TABLE} u ON u.id = r.user_id
            WHERE r.reagent_id = %s
            ORDER BY r.usage_time DESC
            LIMIT 1
            """),
            (reagent_id,),
        )
        record = cur.fetchone()

    if record is None:
        return {"usage_count": 0, "user_name": None, "remaining": None}
    #  开瓶贴标不应算作一次使用
    return {
        "usage_count": record[0] - 1,
        "user_name": record[1],
        "remaining": record[2],
    }
