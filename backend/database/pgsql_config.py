from contextlib import contextmanager

import psycopg2

DB_CONFIG = {
    "host": "localhost",
    "user": "cpulab_user",
    "password": "cpulab_pass",
    "database": "cpulab",
    "port": 5435,
}

USER_TABLE = "users"
BOOKING_TABLE = "bookings"
PLANS_TABLE = "date_plans"
SPACE_TABLE = "spaces"
ZONE_TABLE = "zones"
REAGENT_TABLE = "reagents"


def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)


@contextmanager
def get_connection():
    conn = get_db_connection()
    try:
        yield conn
    finally:
        conn.close()
