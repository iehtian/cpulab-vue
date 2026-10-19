from database.pgsql_config import (
    AREA_TABLE,
    SPACE_TABLE,
    get_connection,
)
from log_config import logger


def create_area():
    with get_connection() as conn, conn.cursor() as cur:
        cur.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {AREA_TABLE} (
                id SERIAL PRIMARY KEY,
                parent_id INTEGER REFERENCES {AREA_TABLE}(id) ON DELETE CASCADE,
                space_id INTEGER REFERENCES {SPACE_TABLE}(id) ON DELETE CASCADE,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.commit()
    logger.info(f"Table '{AREA_TABLE}' ensured.")
