from database.pgsql_config import (
    SPACE_TABLE,
    get_connection,
)
from log_config import logger


def _row_to_dict(row):
    """将数据库行转换为字典"""
    if row is None:
        return None
    return {
        "id": row[0],
        "name": row[1],
    }


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


def add_space(name):
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


def delete_space_by_id(space_id):
    """根据空间 ID 删除空间信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            DELETE FROM {SPACE_TABLE} WHERE id = %s
            """,
            (space_id,),
        )
        conn.commit()


def get_all_spaces():
    """获取所有空间信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT id, name FROM {SPACE_TABLE} ORDER BY created_at DESC
            """
        )
        spaces = cur.fetchall()
        results = []
        for space in spaces:
            results.append(_row_to_dict(space))
    return results
