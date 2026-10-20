from database.pgsql_config import (
    ZONE_TABLE,
    SPACE_TABLE,
    get_connection,
)
from log_config import logger


def create_zone():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {ZONE_TABLE} (
                id SERIAL PRIMARY KEY,
                parent_id INTEGER REFERENCES {ZONE_TABLE}(id) ON DELETE CASCADE,
                space_id INTEGER REFERENCES {SPACE_TABLE}(id) ON DELETE CASCADE,
                sort_order  INTEGER,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours'),
                UNIQUE (parent_id, space_id, name)

            )
            """
        )
        cur.execute(f"COMMENT ON COLUMN {ZONE_TABLE}.sort_order  IS '区域内排序序号'")
        conn.commit()
    logger.info(f"Table '{ZONE_TABLE}' ensured.")


def add_zone(parent_id, space_id, name):
    """插入或更新区域信息"""

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT sort_order  FROM {ZONE_TABLE} WHERE parent_id IS %s AND space_id = %s
            """,
            (parent_id, space_id),
        )
        existing_sort_order = cur.fetchall()
        sort_order = len(existing_sort_order) + 1 if existing_sort_order else 1
        cur.execute(
            f"""
            INSERT INTO {ZONE_TABLE} (parent_id, space_id, name, sort_order)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (parent_id, space_id, name) DO NOTHING
            """,
            (parent_id, space_id, name, sort_order),
        )
        conn.commit()


def get_zones_by_space(space_id):
    """获取指定空间下的所有区域信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT id, parent_id, space_id, name, created_at
            FROM {ZONE_TABLE}
            WHERE space_id = %s
            """,
            (space_id,),
        )
        rows = cur.fetchall()
        zones = [
            {
                "id": row[0],
                "parent_id": row[1],
                "space_id": row[2],
                "name": row[3],
                "created_at": row[4],
            }
            for row in rows
        ]
        return zones
