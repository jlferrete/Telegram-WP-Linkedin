from __future__ import annotations

import sqlite3


class RunsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def create_started(self, run_id: str) -> None:
        self.conn.execute(
            "INSERT INTO runs(run_id, status) VALUES(?, 'started')",
            (run_id,),
        )

    def finish(self, run_id: str, status: str, error: str | None = None) -> None:
        self.conn.execute(
            """
            UPDATE runs
            SET status = ?,
                error = ?,
                finished_at = datetime('now')
            WHERE run_id = ?
            """,
            (status, error, run_id),
        )
