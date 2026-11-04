"""OAuth 2.0 客户端（第三方应用）注册与查询。"""

import secrets

from database.pgsql_config import (
    OAUTH_CLIENT_TABLE,
    dynamic_sql,
    get_connection,
)
from log_config import logger
from utils.helpers import hash_password


def create_oauth_client_table():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            CREATE TABLE IF NOT EXISTS {OAUTH_CLIENT_TABLE} (
                client_id TEXT PRIMARY KEY,
                client_secret_hash TEXT NOT NULL,
                client_name TEXT NOT NULL,
                redirect_uris TEXT[] NOT NULL,
                created_at TIMESTAMP DEFAULT
                    (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours')
            )
            """)
        )
    logger.info(f"Table '{OAUTH_CLIENT_TABLE}' ensured.")


def create_client(client_name, redirect_uris):
    """注册第三方应用，返回 (client_id, 明文 client_secret)。

    明文 secret 仅在此次返回值中出现，库里只存 bcrypt 哈希，请妥善保存。
    """
    client_id = secrets.token_urlsafe(16)
    plain_secret = secrets.token_urlsafe(32)
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            INSERT INTO {OAUTH_CLIENT_TABLE}
                (client_id, client_secret_hash, client_name, redirect_uris)
            VALUES (%s, %s, %s, %s)
            """),
            (client_id, hash_password(plain_secret), client_name, list(redirect_uris)),
        )
    logger.info(f"OAuth client '{client_name}' registered: {client_id}")
    return client_id, plain_secret


def get_client(client_id):
    """按 client_id 查询应用，不存在时返回 None。"""
    if not client_id:
        return None
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            dynamic_sql(f"""
            SELECT client_id, client_secret_hash, client_name, redirect_uris
            FROM {OAUTH_CLIENT_TABLE}
            WHERE client_id = %s
            """),
            (client_id,),
        )
        row = cur.fetchone()
    if not row:
        return None
    return {
        "client_id": row[0],
        "client_secret_hash": row[1],
        "client_name": row[2],
        "redirect_uris": list(row[3]),
    }
