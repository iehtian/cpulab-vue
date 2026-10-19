from database.pgsql_config import (
    BOOKING_TABLE,
    PLANS_TABLE,
    USER_TABLE,
    get_connection,
)
from log_config import logger


# -------- 预约相关 --------
def create_booking_index():
    with get_connection() as conn, conn.cursor() as cur:
        # 创建预约表
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {BOOKING_TABLE} (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                instrument_id TEXT NOT NULL,
                booking_date DATE NOT NULL,
                time_slot_id INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_user
                    FOREIGN KEY (user_id)
                    REFERENCES {USER_TABLE}(id)
                    ON DELETE CASCADE,
                CONSTRAINT unique_time_slot
                    UNIQUE (instrument_id, booking_date, time_slot_id)
            )
            """
        )
        # 创建索引优化查询
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{BOOKING_TABLE}_user_id ON {BOOKING_TABLE}(user_id)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{BOOKING_TABLE}_date ON {BOOKING_TABLE}(booking_date)"
        )
        cur.execute(
            f"CREATE INDEX IF NOT EXISTS idx_{BOOKING_TABLE}_instrument_date ON {BOOKING_TABLE}(instrument_id, booking_date)"
        )
        conn.commit()
    logger.info(f"Table '{BOOKING_TABLE}' ensured.")


def upsert_booking(user_name, instrument_id, date, time_slot_id):
    """插入预约，通过 user_name 获取 user_id"""
    # 先根据 user_name 查询 user_id
    get_user_sql = f"SELECT id FROM {USER_TABLE} WHERE user_name = %s"

    insert_sql = f"""
        INSERT INTO {BOOKING_TABLE}
            (user_id, instrument_id, booking_date, time_slot_id)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """
    logger.info(
        f"Creating booking -> "
        f"{{'user_name': {user_name}, 'instrument_id': {instrument_id}, "
        f"'date': {date}, 'time_slot_id': {time_slot_id}}}"
    )
    with get_connection() as conn, conn.cursor() as cur:
        # 获取 user_id
        cur.execute(get_user_sql, (user_name,))
        result = cur.fetchone()

        if result is None:
            raise ValueError(f"用户 '{user_name}' 不存在")

        user_id = result[0]

        # 插入预约
        cur.execute(insert_sql, (user_id, instrument_id, date, time_slot_id))
        booking_id = cur.fetchone()[0]
        conn.commit()

    logger.info(
        f"Created booking id={booking_id} -> "
        f"{{'user_name': {user_name}, 'user_id': {user_id}, "
        f"'instrument_id': {instrument_id}, 'date': {date}, "
        f"'time_slot_id': {time_slot_id}}}"
    )
    return booking_id


def _row_to_booking(row):
    """将数据库行转换为预约字典

    期望行格式: (id, user_id, instrument_id, booking_date, time_slot_id, user_name)
    """

    return {
        "id": row[0],
        "user_id": row[1],
        "instrument_id": row[2],
        "date": row[3].isoformat() if row[3] else None,
        "time_slot_id": row[4] if len(row) > 4 else None,
        "user_name": row[5] if len(row) > 5 else None,
    }


def search_booking_by_date(instrument_id, date):
    """查询某仪器某日期的所有预约（关联用户信息）"""
    sql = f"""
        SELECT b.id, b.user_id, b.instrument_id, b.booking_date, 
               b.time_slot_id,
               u.user_name, u.color
        FROM {BOOKING_TABLE} b
        JOIN {USER_TABLE} u ON b.user_id = u.id
        WHERE b.instrument_id = %s AND b.booking_date = %s
        ORDER BY b.time_slot_id
    """
    with get_connection() as conn, conn.cursor() as cur:
        logger.info(f"Executing SQL: {sql} with params: {(instrument_id, date)}")
        cur.execute(sql, (instrument_id, date))
        rows = cur.fetchall()

    # 包含用户信息的结果
    results = []
    for row in rows:
        booking = _row_to_booking(row[:6])  # 前7个字段包含 user_name
        booking["color"] = row[6]  # 添加颜色信息
        results.append(booking)
    return results


def search_booking_by_user_and_date(user_id, date):
    """查询某人某日期的所有预约"""
    sql = f"""
        SELECT b.id, b.user_id, b.instrument_id, b.booking_date, 
               b.time_slot_id, u.user_name
        FROM {BOOKING_TABLE} b
        JOIN {USER_TABLE} u ON b.user_id = u.id
        WHERE b.user_id = %s AND b.booking_date = %s
        ORDER BY b.time_slot_id
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (user_id, date))
        rows = cur.fetchall()
        logger.info(f"Found bookings for user_id={user_id}, date={date}: {rows}")
    return [_row_to_booking(row) for row in rows]


def search_booking_users_by_range(instrument_id, start_date, end_date):
    """查询某仪器在 [start_date, end_date]（含端点）内预约过的去重用户名与颜色，按用户名排序。"""
    sql = f"""
        SELECT DISTINCT u.user_name, u.color
        FROM {BOOKING_TABLE} b
        JOIN {USER_TABLE} u ON b.user_id = u.id
        WHERE b.instrument_id = %s
          AND b.booking_date BETWEEN %s AND %s
        ORDER BY u.user_name
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (instrument_id, start_date, end_date))
        rows = cur.fetchall()

    logger.info(
        f"Found bookers for instrument_id={instrument_id}, range={start_date}~{end_date}: {rows}"
    )
    return [{"user_name": row[0], "color": row[1]} for row in rows]


def delete_booking_by_id(booking_id):
    """删除预约"""
    sql = f"DELETE FROM {BOOKING_TABLE} WHERE id = %s"
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (booking_id,))
        conn.commit()
    logger.info(f"Deleted booking id={booking_id}")


def delete_bookings_by_dates(instrument_id, date_list):
    """删除某仪器在指定日期列表的所有预约"""
    sql = f"DELETE FROM {BOOKING_TABLE} WHERE instrument_id = %s AND booking_date = ANY(%s)"
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (instrument_id, date_list))
        conn.commit()
    logger.info(
        f"Deleted bookings for instrument_id={instrument_id} on dates={date_list}"
    )


def delete_bookings_by_slots(instrument_id, date, slots):
    """删除某仪器在指定日期的指定时间段预约"""
    if not slots:
        return 0

    sql = f"""
        DELETE FROM {BOOKING_TABLE}
        WHERE instrument_id = %s
          AND booking_date = %s
          AND time_slot_id = ANY(%s)
    """

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (instrument_id, date, slots))
        deleted = cur.rowcount
        conn.commit()

    logger.info(
        f"Deleted {deleted} bookings for instrument_id={instrument_id} on date={date} slots={slots}"
    )
    return deleted


# -------- 每日计划相关 --------
def create_date_plan_index():
    """创建每日计划表与索引"""
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {PLANS_TABLE} (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                date DATE NOT NULL,
                plan TEXT,
                status INTEGER DEFAULT 0,
                remark TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT fk_user
                    FOREIGN KEY (user_id)
                    REFERENCES {USER_TABLE}(id)
                    ON DELETE CASCADE
            )
            """
        )

        # 优化按用户+日期查询，并保证同一用户同一天只有一条记录
        cur.execute(
            f"CREATE UNIQUE INDEX IF NOT EXISTS idx_{PLANS_TABLE}_user_date ON {PLANS_TABLE}(user_id, date)"
        )
        conn.commit()
    logger.info(f"Table '{PLANS_TABLE}' ensured.")


def get_dateinfo(user_name: str, date: str) -> list[tuple]:
    """根据 user_name 和 date 查询 plan / status / remark"""
    sql = f"""
        SELECT dp.plan, dp.status, dp.remark
        FROM {PLANS_TABLE} dp
        JOIN {USER_TABLE} u ON dp.user_id = u.id
        WHERE u.user_name = %s AND dp.date = %s
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (user_name, date))
        results = cur.fetchall()

    logger.debug(
        "查询每日计划 | user_name=%s, date=%s, count=%d", user_name, date, len(results)
    )
    return results


def get_all_dateinfo_by_date(date: str, skip_names=None) -> list[dict]:
    """按日期查询所有用户每日计划，返回结构与接口层一致。"""
    sql = f"""
        SELECT u.user_name, dp.plan, dp.status, dp.remark
        FROM {USER_TABLE} u
        LEFT JOIN {PLANS_TABLE} dp
          ON dp.user_id = u.id
         AND dp.date = %s
        ORDER BY u.user_name
    """

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (date,))
        rows = cur.fetchall()

    skip_set = set(skip_names or [])
    grouped = {}
    for user_name, plan, status, remark in rows:
        if user_name in skip_set:
            continue

        if user_name not in grouped:
            grouped[user_name] = {"user": user_name, "info": []}

        if plan is not None or status is not None or remark is not None:
            grouped[user_name]["info"].append((plan, status, remark))

    results = list(grouped.values())
    logger.debug("查询所有用户每日计划 | date={}, users={}", date, len(results))
    return results


def upsert_plan_field(user_name: str, date: str, field: str, value) -> None:
    """根据是否已有记录插入或更新指定字段。"""
    allowed_fields = {"plan", "status", "remark"}
    if field not in allowed_fields:
        raise ValueError(f"不支持的字段: {field}")

    if field == "status":
        if isinstance(value, bool):
            value = 1 if value else 0
        if isinstance(value, str):
            value = value.strip()
        if value not in {0, 1, 2, "0", "1", "2"}:
            raise ValueError(f"status 只能是 0、1 或 2，收到: {value}")
        value = int(value)

    get_user_sql = f"SELECT id FROM {USER_TABLE} WHERE user_name = %s"

    check_sql = f"""
        SELECT dp.id FROM {PLANS_TABLE} dp
        JOIN {USER_TABLE} u ON dp.user_id = u.id
        WHERE u.user_name = %s AND dp.date = %s
    """

    update_sql = f"""
        UPDATE {PLANS_TABLE}
        SET {field} = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """

    insert_sql = f"""
        INSERT INTO {PLANS_TABLE} (user_id, date, {field})
        VALUES (%s, %s, %s)
    """

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(get_user_sql, (user_name,))
        row = cur.fetchone()
        if row is None:
            raise ValueError(f"用户 '{user_name}' 不存在")
        user_id = row[0]

        cur.execute(check_sql, (user_name, date))
        existing = cur.fetchone()

        if existing:
            cur.execute(update_sql, (value, existing[0]))
        else:
            cur.execute(insert_sql, (user_id, date, value))

        conn.commit()

    logger.info(
        "每日计划更新成功 | user_name=%s, date=%s, field=%s", user_name, date, field
    )


def delete_user_data(user_name: str) -> None:
    """删除某用户的全部 date_plans 记录"""
    sql = f"""
        DELETE FROM {PLANS_TABLE}
        WHERE user_id = (SELECT id FROM {USER_TABLE} WHERE user_name = %s)
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (user_name,))
        conn.commit()
    logger.info("user_name={} 的每日计划数据已删除", user_name)
