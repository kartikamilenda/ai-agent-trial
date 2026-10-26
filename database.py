
import sqlite3
from contextlib import contextmanager

DB_PATH = "tasks.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH)

    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                assignee TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'pending'
            )
        """)


if __name__ == "__main__":
    init_database()
    print("Database initialized.")
