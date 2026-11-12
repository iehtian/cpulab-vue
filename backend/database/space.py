from database.pgsql_config import (
    SPACE_TABLE,
    dynamic_sql,
    get_connection,
)
from log_config import logger


def _row_to_space(row):
    """将数据库行转换为字典"""
    if row is None:
        return None
    return {
        "id": row[0],
        "name": row[1],
    }


def create_space_table():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            CREATE TABLE IF NOT EXISTS {SPACE_TABLE} (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours')
            )
            """)
        )
    logger.info(f"Table '{SPACE_TABLE}' ensured.")


def add_space(name):
    """插入空间信息（同名已存在则忽略）"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            INSERT INTO {SPACE_TABLE} (name)
            VALUES (%s)
            ON CONFLICT (name) DO NOTHING
            """),
            (name,),
        )


def update_space_name(space_id, new_name):
    """更新空间名称"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            UPDATE {SPACE_TABLE}
            SET name = %s
            WHERE id = %s
            """),
            (new_name, space_id),
        )


def delete_space_by_id(space_id):
    """根据空间 ID 删除空间信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            DELETE FROM {SPACE_TABLE} WHERE id = %s
            """),
            (space_id,),
        )


def get_all_spaces():
    """获取所有空间信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            SELECT id, name FROM {SPACE_TABLE} ORDER BY created_at ASC
            """)
        )
        spaces = cur.fetchall()
        results = []
        for space in spaces:
            results.append(_row_to_space(space))
    return results
