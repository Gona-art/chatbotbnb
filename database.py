"""
SQLite database setup and booking utilities.
"""

import sqlite3
from datetime import datetime

DB_NAME = "bookings.db"


def init_db() -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            check_in TEXT NOT NULL,
            check_out TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def is_available(check_in: str, check_out: str) -> bool:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM bookings
        WHERE NOT (
            check_out <= ? OR check_in >= ?
        )
    """, (check_in, check_out))

    conflict = cursor.fetchone()
    conn.close()

    return conflict is None


def calculate_price(check_in: str, check_out: str, price_per_night: float = 120.0) -> float:
    date_format = "%Y-%m-%d"
    start = datetime.strptime(check_in, date_format)
    end = datetime.strptime(check_out, date_format)
    nights = (end - start).days
    return nights * price_per_night


def create_booking(check_in: str, check_out: str) -> None:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO bookings (check_in, check_out)
        VALUES (?, ?)
    """, (check_in, check_out))

    conn.commit()
    conn.close()
