"""
SQLite setup for the Task API.

Stage 0 of A2: creates tasks.db and the `tasks` table if they don't exist,
and seeds three example tasks only the first time (when the table is empty).
"""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "tasks.db"

SEED_TASKS = [
    ("Buy milk", 0),
    ("Finish FL-01 assignment", 1),
    ("Walk the dog", 0),
]


def get_connection() -> sqlite3.Connection:
    """Open a connection with sensible defaults for a small API server."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create the tasks table if missing, and seed it if empty."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id    INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT    NOT NULL,
                done  INTEGER NOT NULL DEFAULT 0
            )
            """
        )
        conn.commit()

        (count,) = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()
        if count == 0:
            conn.executemany(
                "INSERT INTO tasks (title, done) VALUES (?, ?)", SEED_TASKS
            )
            conn.commit()
    finally:
        conn.close()
