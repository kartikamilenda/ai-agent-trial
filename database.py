import sqlite3
from contextlib import contextmanager
from config import DB_PATH

@contextmanager
def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()

def init_database():
    with get_connection() as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            assignee TEXT NOT NULL,
            deadline TEXT,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )''')
        # Upgrade old database without deleting existing tasks.
        existing = {row['name'] for row in conn.execute('PRAGMA table_info(tasks)')}
        for name, definition in [('deadline', 'TEXT'), ('created_at', 'TEXT'), ('updated_at', 'TEXT')]:
            if name not in existing:
                conn.execute(f'ALTER TABLE tasks ADD COLUMN {name} {definition}')
