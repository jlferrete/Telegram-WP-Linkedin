from __future__ import annotations

import sqlite3
from pathlib import Path

PRAGMAS: tuple[str, ...] = (
    "PRAGMA journal_mode = WAL;",
    "PRAGMA synchronous = NORMAL;",
    "PRAGMA foreign_keys = ON;",
    "PRAGMA busy_timeout = 5000;",
)


def connect_db(db_path: Path) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=5.0)
    conn.row_factory = sqlite3.Row
    apply_pragmas(conn)
    return conn


def apply_pragmas(conn: sqlite3.Connection) -> None:
    for pragma in PRAGMAS:
        conn.execute(pragma)


def init_database(db_path: Path, migrations_dir: Path) -> None:
    conn = connect_db(db_path)
    try:
        for migration in sorted(migrations_dir.glob("*.sql")):
            conn.executescript(migration.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()
