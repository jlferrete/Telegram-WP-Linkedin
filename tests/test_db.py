from __future__ import annotations

import sqlite3
from pathlib import Path

from app.infra.db import init_database


def test_init_database_creates_core_tables(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"

    init_database(db_path=db_path, migrations_dir=migrations_dir)

    conn = sqlite3.connect(str(db_path))
    try:
        tables = {
            row[0]
            for row in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        }
        assert "state" in tables
        assert "runs" in tables
        assert "updates" in tables
        assert "publications" in tables
        assert "events" in tables
        assert "process_lock" in tables
    finally:
        conn.close()
