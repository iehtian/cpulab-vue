from database.pgsql_config import (
    BOOKING_TABLE,
    DUTY_LOG_TABLE,
    USER_TABLE,
    get_connection,
)


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
            f"""
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
                    AND last_booking <  %s
                ORDER BY user_id, streak DESC
                ),
                cand_base AS (
                SELECT p.user_id, u.user_name, p.join_date,
                    (SELECT MAX(week_start) FROM {DUTY_LOG_TABLE} dl
                        WHERE dl.user_id = p.user_id AND dl.instrument_id = %s) AS last_served
                FROM pool p JOIN {USER_TABLE} u ON u.id = p.user_id
                ),
                candidate AS (
                SELECT * FROM cand_base
                ORDER BY (last_served IS NULL) DESC,                          -- ① 从未值日的新人优先
                        CASE WHEN last_served IS NULL THEN join_date END DESC,    --    新人之间按加入先后
                        last_served                                          -- ② 老人按等待最久优先
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
