from database.pgsql_config import (
    REAGENT_TABLE,
    REAGENT_USAGE_TABLE,
    USER_TABLE,
    ZONE_TABLE,
    dynamic_sql,
    get_connection,
)
from database.reagent_usage import EVENT_SET, EVENT_USE
from log_config import logger


def create_reagent_table():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            CREATE TABLE IF NOT EXISTS {REAGENT_TABLE} (
                id SERIAL PRIMARY KEY,
                zone_id INTEGER REFERENCES {ZONE_TABLE}(id) ON DELETE CASCADE,
                name TEXT NOT NULL,
                CAS_number TEXT,
                -- 试剂类别: 1=普通试剂, 2=危化品, 3=生物试剂, 4=色谱级试剂
                category INTEGER NOT NULL,
                -- 仅色谱级试剂(category=4)使用, 其余类别必须为 NULL
                capacity NUMERIC CHECK (capacity > 0),
                bottle_count INTEGER CHECK (bottle_count > 0),
                -- 规格, 所有类别均可填, 可为空
                specification TEXT,
                need2restock BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours'),
                UNIQUE (zone_id, name),
                -- 容量和瓶数仅允许出现在色谱级试剂上
                CHECK (category = 4 OR (capacity IS NULL AND bottle_count IS NULL))
            )
            """)
        )
    logger.info(f"Table '{REAGENT_TABLE}' ensured.")


_unset = object()


def upsert_reagent(
    zone_id,
    user_id,
    *,
    name=_unset,
    category=_unset,
    cas_number=_unset,
    capacity=_unset,
    bottle_count=_unset,
    specification=_unset,
    needs_restock=_unset,
):
    """插入或更新试剂信息"""
    if zone_id is None:
        raise ValueError("zone_id cannot be None")
    if user_id is None:
        raise ValueError("user_id cannot be None")
    candidate_fields = {
        "name": name,
        "category": category,
        "CAS_number": cas_number,
        "capacity": capacity,
        "bottle_count": bottle_count,
        "specification": specification,
        "need2restock": needs_restock,
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
            dynamic_sql(f"""
            INSERT INTO {REAGENT_TABLE} (zone_id, {columns})
            VALUES (%s, {placeholders})
            ON CONFLICT (zone_id, name) DO UPDATE SET {set_clause}
            RETURNING id, capacity, bottle_count
            """),
            [zone_id] + values,
        )
        result = cur.fetchone()
        if result is None:
            raise RuntimeError("upsert 后未能取回试剂记录")
        reagent_id = result[0]
        total_capacity = None
        if result[1] is not None and result[2] is not None:
            total_capacity = result[1] * result[2]

        # 记录创建者
        cur.execute(
            dynamic_sql(f"""
            INSERT INTO {REAGENT_USAGE_TABLE} (reagent_id, user_id, event_type, amount, remaining_after)
            VALUES (%s, %s, %s, %s, %s)
            """),
            (reagent_id, user_id, EVENT_SET, 0, total_capacity),
        )


def set_needs_restock(reagent_id, needs_restock):
    """更新试剂的补货状态"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            UPDATE {REAGENT_TABLE}
            SET need2restock = %s
            WHERE id = %s
            """),
            (needs_restock, reagent_id),
        )
    logger.info(f"Reagent need2restock updated for reagent_id={reagent_id}.")


def get_reagents_by_zone(zone_id):
    """根据区域 ID 获取试剂信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            SELECT r.id, r.zone_id, r.name, r.CAS_number, r.category, r.capacity,
                r.bottle_count, r.specification,  r.need2restock,
                u.usage_count, u.user_name, u.remaining_after  -- 子查询结果列
            FROM {REAGENT_TABLE} AS r
            LEFT JOIN LATERAL (
                SELECT COUNT(*) OVER () AS usage_count,
                    u.user_name,
                    ru.remaining_after
                FROM {REAGENT_USAGE_TABLE} ru
                LEFT JOIN {USER_TABLE} u ON u.id = ru.user_id
                WHERE ru.reagent_id = r.id
                ORDER BY ru.usage_time DESC
                LIMIT 1
            ) AS u ON TRUE
            WHERE r.zone_id = %s
            """),
            (zone_id,),
        )
        rows = cur.fetchall()
        reagents = [
            {
                "id": row[0],
                "zoneId": row[1],
                "name": row[2],
                "casNumber": row[3],
                "category": row[4],
                "capacity": float(row[5]) if row[5] is not None else None,
                "bottleCount": row[6],
                "specification": row[7],
                "need2restock": row[8],
                "usageLength": row[9],
                "lastUserName": row[10],
                "lastRemainder": row[11],
            }
            for row in rows
        ]
        return reagents


def delete_reagent_by_id(reagent_id):
    """根据试剂 ID 删除试剂信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            DELETE FROM {REAGENT_TABLE}
            WHERE id = %s
            """),
            (reagent_id,),
        )


def get_need2restock_reagents():
    """获取所有需要补货的试剂信息"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            SELECT r.id, r.zone_id, r.name, r.CAS_number, r.category, r.capacity,
                r.bottle_count, r.specification,  r.need2restock,
                u.usage_count, u.user_name, u.remaining_after
            FROM {REAGENT_TABLE} AS r
            LEFT JOIN LATERAL (
                SELECT COUNT(*) OVER () AS usage_count,
                    u.user_name,
                    ru.remaining_after
                FROM {REAGENT_USAGE_TABLE} ru
                LEFT JOIN {USER_TABLE} u ON u.id = ru.user_id
                WHERE ru.reagent_id = r.id
                ORDER BY ru.usage_time DESC
                LIMIT 1
            ) AS u ON TRUE
            WHERE r.need2restock = TRUE
            ORDER BY r.id
            """)
        )
        rows = cur.fetchall()
        reagents = [
            {
                "id": row[0],
                "zoneId": row[1],
                "name": row[2],
                "casNumber": row[3],
                "category": row[4],
                "capacity": float(row[5]) if row[5] is not None else None,
                "bottleCount": row[6],
                "specification": row[7],
                "need2restock": row[8],
                "usageLength": row[9],
                "lastUserName": row[10],
                "lastRemainder": row[11],
            }
            for row in rows
        ]
        return reagents


def get_frequently_used_reagents(user_id):
    """获取指定用户常用的试剂信息（按该用户实际取用次数降序）"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            SELECT r.id, r.zone_id, r.name, r.CAS_number, r.category, r.capacity,
                r.bottle_count, r.specification,  r.need2restock,
                t.use_count,
                u.usage_count, u.user_name, u.remaining_after
            FROM (
                SELECT reagent_id, COUNT(*) AS use_count
                FROM {REAGENT_USAGE_TABLE}
                WHERE user_id = %s AND event_type = {EVENT_USE}
                GROUP BY reagent_id
            ) AS t
            JOIN {REAGENT_TABLE} AS r ON r.id = t.reagent_id
            LEFT JOIN LATERAL (
                SELECT COUNT(*) OVER () AS usage_count,
                    u.user_name,
                    ru.remaining_after
                FROM {REAGENT_USAGE_TABLE} ru
                LEFT JOIN {USER_TABLE} u ON u.id = ru.user_id
                WHERE ru.reagent_id = r.id AND ru.event_type = {EVENT_USE}
                ORDER BY ru.usage_time DESC
                LIMIT 1
            ) AS u ON TRUE
            ORDER BY t.use_count DESC
            """),
            (user_id,),
        )
        rows = cur.fetchall()
        reagents = [
            {
                "id": row[0],
                "zoneId": row[1],
                "name": row[2],
                "casNumber": row[3],
                "category": row[4],
                "capacity": float(row[5]) if row[5] is not None else None,
                "bottleCount": row[6],
                "specification": row[7],
                "need2restock": row[8],
                "times": row[9],
                "usageLength": row[10],
                "lastUserName": row[11],
                "lastRemainder": row[12],
            }
            for row in rows
        ]
        return reagents
