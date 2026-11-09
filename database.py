
import sqlite3
from contextlib import contextmanager

from config import DB_PATH


@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

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
                deadline TEXT,
                status TEXT NOT NULL DEFAULT 'pending',
                source_item_id TEXT,
                created_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT NOT NULL
                    DEFAULT CURRENT_TIMESTAMP
            )
        """)

        existing = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(tasks)"
            )
        }

        migrations = [
            ("deadline", "TEXT"),
            ("created_at", "TEXT"),
            ("updated_at", "TEXT"),
            ("source_item_id", "TEXT")
        ]

        for name, definition in migrations:
            if name not in existing:
                conn.execute(
                    f"ALTER TABLE tasks "
                    f"ADD COLUMN {name} {definition}"
                )

        conn.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS
                idx_tasks_source_item_id
            ON tasks(source_item_id)
        """)

        conn.execute("""
            UPDATE tasks
            SET created_at = COALESCE(
                    created_at,
                    CURRENT_TIMESTAMP
                ),
                updated_at = COALESCE(
                    updated_at,
                    CURRENT_TIMESTAMP
                )
            WHERE created_at IS NULL
               OR updated_at IS NULL
        """)


if __name__ == "__main__":
    init_database()
    print("Database initialized.")
