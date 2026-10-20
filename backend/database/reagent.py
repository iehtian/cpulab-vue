from database.pgsql_config import (
    ZONE_TABLE,
    REAGENT_TABLE,
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
                name TEXT NOT NULL ,
                created_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'UTC' + INTERVAL '8 hours'),
                UNIQUE (zone_id, name)
            )
            """
        )
        conn.commit()
    logger.info(f"Table '{REAGENT_TABLE}' ensured.")
