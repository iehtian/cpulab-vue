from database.pgsql_config import (
    REAGENT_TABLE,
    ZONE_TABLE,
    get_connection,
)
from log_config import logger


def create_reagent():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {REAGENT_TABLE} (
                id SERIAL PRIMARY KEY,
                zone_id INTEGER REFERENCES {ZONE_TABLE}(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                CAS_number TEXT,
                expiry_date DATE,
                -- 试剂类别: 1=普通试剂, 2=危化品, 3=生物试剂, 4=色谱级试剂
                category INTEGER NOT NULL,
                -- 仅色谱级试剂(category=4)使用, 其余类别必须为 NULL
                capacity NUMERIC CHECK (capacity > 0),
                bottle_count INTEGER CHECK (bottle_count > 0),
                -- 规格, 所有类别均可填, 可为空
                specification TEXT,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours'),
                UNIQUE (zone_id, name),
                -- 容量和瓶数仅允许出现在色谱级试剂上
                CHECK (category = 4 OR (capacity IS NULL AND bottle_count IS NULL))
            )
            """
        )
        conn.commit()
    logger.info(f"Table '{REAGENT_TABLE}' ensured.")


def upsert_reagent(
    zone_id,
    name,
    category,
    CAS_number=None,
    capacity=None,
    bottle_count=None,
    specification=None,
    expiry_date=None,
):
    """插入或更新试剂信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            INSERT INTO {REAGENT_TABLE} (zone_id, name, CAS_number, category, capacity, bottle_count, specification, expiry_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (zone_id, name) DO UPDATE SET
                category = EXCLUDED.category,
                capacity = EXCLUDED.capacity,
                bottle_count = EXCLUDED.bottle_count,
                specification = EXCLUDED.specification
            """,
            (
                zone_id,
                name,
                CAS_number,
                category,
                capacity,
                bottle_count,
                specification,
                expiry_date,
            ),
        )
        conn.commit()


def get_reagents_by_zone(zone_id):
    """根据区域 ID 获取试剂信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT id, zone_id, name, category, capacity, bottle_count, specification
            FROM {REAGENT_TABLE}
            WHERE zone_id = %s
            """,
            (zone_id,),
        )
        rows = cur.fetchall()
        reagents = [
            {
                "id": row[0],
                "zone_id": row[1],
                "name": row[2],
                "category": row[3],
                "capacity": float(row[4]) if row[4] is not None else None,
                "bottle_count": row[5],
                "specification": row[6],
            }
            for row in rows
        ]
        return reagents
