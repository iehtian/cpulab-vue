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
                -- 开瓶贴标日期
                open_date DATE,
                -- 试剂类别: 1=普通试剂, 2=危化品, 3=生物试剂, 4=色谱级试剂
                category INTEGER NOT NULL,
                -- 仅色谱级试剂(category=4)使用, 其余类别必须为 NULL
                capacity NUMERIC CHECK (capacity > 0),
                -- 规格, 所有类别均可填, 可为空
                specification TEXT,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours'),
                UNIQUE (zone_id, name),
                -- 容量和瓶数仅允许出现在色谱级试剂上
                CHECK (category = 4 OR (capacity  IS NULL))
            )
            """
        )
    logger.info(f"Table '{REAGENT_TABLE}' ensured.")


_unset = object()


def upsert_reagent(
    zone_id,
    *,
    name=_unset,
    category=_unset,
    CAS_number=_unset,
    capacity=_unset,
    specification=_unset,
    expiry_date=_unset,
    open_date=_unset,
):
    """插入或更新试剂信息"""
    if zone_id is None:
        raise ValueError("zone_id cannot be None")
    candidate_fields = {
        "name": name,
        "category": category,
        "CAS_number": CAS_number,
        "capacity": capacity,
        "specification": specification,
        "expiry_date": expiry_date,
        "open_date": open_date,
    }
    update_fields = {k: v for k, v in candidate_fields.items() if v is not _unset}
    if not update_fields:
        logger.info("No fields to update for reagent.")
        return
    with get_connection() as conn, conn.cursor() as cur:
        columns = ", ".join(update_fields.keys())
        placeholders = ", ".join(["%s"] * len(update_fields))
        set_clause = ", ".join(f"{k} = EXCLUDED.{k}" for k in update_fields.keys())
        values = list(update_fields.values())
        cur.execute(
            f"""
            INSERT INTO {REAGENT_TABLE} (zone_id, {columns})
            VALUES (%s, {placeholders})
            ON CONFLICT (zone_id, name) DO UPDATE SET {set_clause}
            """,
            [zone_id] + values,
        )


def update_open_date(reagent_id, open_date):
    """更新试剂的开瓶贴标日期"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            UPDATE {REAGENT_TABLE}
            SET open_date = %s
            WHERE id = %s
            """,
            (open_date, reagent_id),
        )

def get_reagents_by_zone(zone_id):
    """根据区域 ID 获取试剂信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            SELECT id, zone_id, name, CAS_number, category, capacity,
                   specification, open_date, expiry_date
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
                "CAS_number": row[3],
                "category": row[4],
                "capacity": float(row[5]) if row[5] is not None else None,
                "specification": row[6],
                "open_date": row[7].isoformat() if row[7] is not None else None,
                "expiry_date": row[8].isoformat() if row[8] is not None else None,
            }
            for row in rows
        ]
        return reagents


def delete_reagent_by_id(reagent_id):
    """根据试剂 ID 删除试剂信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            DELETE FROM {REAGENT_TABLE}
            WHERE id = %s
            """,
            (reagent_id,),
        )
