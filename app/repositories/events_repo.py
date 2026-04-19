from __future__ import annotations

import sqlite3


class EventsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def add(
        self,
        run_id: str,
        stage: str,
        status: str,
        detail: str | None = None,
        update_id: int | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO events(run_id, update_id, stage, status, detail)
            VALUES(?, ?, ?, ?, ?)
            """,
            (run_id, update_id, stage, status, detail),
        )
