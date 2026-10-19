from database.pgsql_config import (
    SPACE_TABLE,
    get_connection,
)
from log_config import logger


def create_space():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {SPACE_TABLE} (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours')
            )
            """
        )
        conn.commit()
    logger.info(f"Table '{SPACE_TABLE}' ensured.")


def upsert_space(name):
    """插入或更新空间信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {SPACE_TABLE} (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            """,
            (name,),
        )
        conn.commit()


def get_space_by_name(name):
    """根据名称获取空间信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT * FROM {SPACE_TABLE} WHERE name = %s
            """,
            (name,),
        )
        space = cur.fetchone()
    return space


def get_all_spaces():
    """获取所有空间信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT * FROM {SPACE_TABLE}
            """
        )
        spaces = cur.fetchall()
    return spaces
