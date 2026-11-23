from database.pgsql_config import (
    BOOKING_TABLE,
    DUTY_LOG_TABLE,
    USER_TABLE,
    get_connection,
)

# 候选人计算链：b → s → streaks → pool → cand_base
# get_duty_log / get_duty_roster 共用，保证"选中规则"与"队列排序"永远一致。
# 参数顺序：instrument_id, last_days, week_start（窗口下限基准）,
#           week_start（窗口上限）, instrument_id（关联 duty_log）
_CANDIDATE_CTE = f"""
WITH b AS (
    SELECT user_id, booking_date,
            LAG(booking_date) OVER (PARTITION BY user_id ORDER BY booking_date) AS prev_date
    FROM {BOOKING_TABLE} WHERE instrument_id = %s
    ),
    s AS (
    SELECT user_id, booking_date,
            COUNT(*) FILTER (WHERE prev_date IS NULL
                            OR booking_date - prev_date > %s)   -- 空窗 > 30 天开新段
            OVER (PARTITION BY user_id ORDER BY booking_date) AS streak
    FROM b
    ),
    streaks AS (
    SELECT user_id, streak,
            MIN(booking_date) AS join_date,     -- 当前活跃段首约 = 加入时间
            MAX(booking_date) AS last_booking
    FROM s GROUP BY user_id, streak
    ),
    pool AS (   -- 每个用户取最新一段，且最近预约在窗口内
    SELECT DISTINCT ON (user_id) user_id, join_date
    FROM streaks
    WHERE last_booking >= %s - INTERVAL '30 days'   -- 参数：本周一
        AND last_booking <  %s + INTERVAL '7 days'  -- 窗口含本周：周内新预约即时入队
    ORDER BY user_id, streak DESC
    ),
    cand_base AS (
    SELECT p.user_id, u.user_name, p.join_date,
        (SELECT MAX(week_start) FROM {DUTY_LOG_TABLE} dl
            WHERE dl.user_id = p.user_id AND dl.instrument_id = %s) AS last_served
    FROM pool p JOIN {USER_TABLE} u ON u.id = p.user_id
    )
"""

# 值日优先级排序：① 从未值日的新人优先（新人之间先来的先值日）② 老人按等待最久优先
_ORDER_BY_PRIORITY = """
    ORDER BY (last_served IS NULL) DESC,
             CASE WHEN last_served IS NULL THEN join_date END ASC,
             last_served
"""


def create_duty_log_table():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {DUTY_LOG_TABLE} (
                id SERIAL PRIMARY KEY,
                instrument_id TEXT NOT NULL,
                week_start DATE NOT NULL,
                user_id INTEGER REFERENCES {USER_TABLE}(id) ON DELETE CASCADE,
                user_name TEXT REFERENCES {USER_TABLE}(user_name) ON DELETE CASCADE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (instrument_id, week_start)
            )
        """)


def _select_duty_log(cur, instrument_id, week_start):
    cur.execute(
        f"""
        SELECT  user_name
        FROM {DUTY_LOG_TABLE}
        WHERE instrument_id = %s AND week_start = %s
    """,
        (instrument_id, week_start),
    )
    return cur.fetchone()


def get_duty_log(instrument_id, last_days, week_start):
    with get_connection() as conn, conn.cursor() as cur:
        # 快速路径：本周已有人选
        result = _select_duty_log(cur, instrument_id, week_start)
        if result is not None:
            return result

        # 原子写入：计算候选人并插入，靠唯一约束 (instrument_id, week_start) 仲裁并发。
        # 并发时 ON CONFLICT DO NOTHING 会阻塞等对方事务提交后跳过，
        # RETURNING 为空即表示落选，随后重新读取胜出者写入的记录。
        cur.execute(
            _CANDIDATE_CTE
            + f""",
            candidate AS (
                SELECT * FROM cand_base
                {_ORDER_BY_PRIORITY}
                LIMIT 1
                ),
                ins AS (
                INSERT INTO {DUTY_LOG_TABLE} (instrument_id, week_start, user_id,user_name)
                SELECT %s, %s, user_id, user_name FROM candidate
                ON CONFLICT (instrument_id, week_start) DO NOTHING
                RETURNING user_id
                )
                SELECT  c.user_name
                FROM candidate c
                WHERE c.user_id IN (SELECT user_id FROM ins);
        """,
            (
                instrument_id,
                last_days,
                week_start,
                week_start,
                instrument_id,
                instrument_id,
                week_start,
            ),
        )

        result = cur.fetchone()
        if result is not None:
            return result
        # 并发落选：读取胜出者已提交的记录，保证所有请求返回一致
        return _select_duty_log(cur, instrument_id, week_start)


def get_duty_roster(instrument_id, last_days, week_start):
    """值日生候选队列，按值日优先级排序（队首即下一位值日生）。

    纯查询，不写 duty_log。返回 [(user_name, join_date, last_served), ...]。
    """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            _CANDIDATE_CTE
            + f"""
            SELECT user_name, join_date, last_served
            FROM cand_base
            {_ORDER_BY_PRIORITY}
        """,
            (instrument_id, last_days, week_start, week_start, instrument_id),
        )
        result = cur.fetchall()
        return [
            {"userName": row[0], "joinDate": row[1], "lastServed": row[2]}
            for row in result
        ]
