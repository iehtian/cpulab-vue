from database.pgsql_config import (
    USER_TABLE,
    get_connection,
)
from log_config import logger


# -------- 用户相关 --------
def user_index_exists(index_name=USER_TABLE):
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute("SELECT to_regclass(%s)", (f"public.{index_name}",))
        exists = cur.fetchone()[0] is not None
    return exists


def create_user_index():
    with get_connection() as conn:
        with conn.cursor() as cur:
            # 创建用户表，使用 SERIAL 作为主键
            # fmt: off
            cur.execute(
                rf"""
                CREATE TABLE IF NOT EXISTS {USER_TABLE} (
                    id SERIAL PRIMARY KEY,
                    password TEXT NOT NULL,
                    user_name TEXT UNIQUE NOT NULL,
                    color TEXT NOT NULL,
                    email TEXT CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{{2,}}$'),
                    phone TEXT CHECK (phone ~* '^1[3-9]\d{{9}}$'),
                    created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours')
                )
                """
            )
            # fmt: on

            # 为常用查询字段创建索引
            cur.execute(
                f"CREATE INDEX IF NOT EXISTS idx_{USER_TABLE}_user_name ON {USER_TABLE}(user_name)"
            )
            conn.commit()
        logger.info(f"Table '{USER_TABLE}' ensured.")


def upsert_user(user_name, password=None, color=None, email=None, phone=None):
    """插入或更新用户信息"""
    # 构建字段列表
    insert_fields = ["user_name"]
    insert_values = [user_name]
    update_clauses = []

    # 动态添加字段
    if password:
        insert_fields.append("password")
        insert_values.append(password)
        update_clauses.append("password = EXCLUDED.password")

    if color:
        insert_fields.append("color")
        insert_values.append(color)
        update_clauses.append("color = EXCLUDED.color")

    if email:
        insert_fields.append("email")
        insert_values.append(email)
        update_clauses.append("email = EXCLUDED.email")

    if phone:
        insert_fields.append("phone")
        insert_values.append(phone)
        update_clauses.append("phone = EXCLUDED.phone")

    if not update_clauses:
        raise ValueError("没有提供要更新的字段")

    # 构建 SQL
    placeholders = ", ".join(["%s"] * len(insert_fields))
    sql = f"""
        INSERT INTO {USER_TABLE} ({", ".join(insert_fields)})
        VALUES ({placeholders})
        ON CONFLICT (user_name) DO UPDATE
        SET {", ".join(update_clauses)}
        RETURNING id
    """

    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, tuple(insert_values))
        user_id = cur.fetchone()[0]
        conn.commit()

    logger.info(f"Upserted user '{user_name}' (id={user_id})")
    return user_id


def _row_to_user(row):
    """将数据库行转换为用户字典，字段顺序与 SELECT 对齐"""
    return {
        "id": row[0],
        "user_name": row[1],
        "password": row[2],
        "color": row[3],
        "email": row[4],
        "phone": row[5],
        "created_at": row[6].isoformat() if row[6] else None,
    }


def search_user_by_name(user_name):
    """根据用户名查询用户"""
    sql = f"""
            SELECT id, user_name, password, color, email, phone, created_at
            FROM {USER_TABLE}
            WHERE user_name = %s
        """
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(sql, (user_name,))
        row = cur.fetchone()
        logger.debug(
            f"search_user_by_name('{user_name}') returned {'1 row' if row else '0 rows'}"
        )
    return _row_to_user(row) if row else None
