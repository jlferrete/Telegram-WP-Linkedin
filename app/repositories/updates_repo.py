from __future__ import annotations

import sqlite3


class UpdatesRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def exists(self, update_id: int) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM updates WHERE update_id = ?",
            (update_id,),
        ).fetchone()
        return row is not None

    def insert(
        self,
        update_id: int,
        chat_id: int,
        text: str,
        run_id: str,
        source_payload: str,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO updates(update_id, chat_id, text, run_id, source_payload)
            VALUES(?, ?, ?, ?, ?)
            """,
            (update_id, chat_id, text, run_id, source_payload),
        )

    def list_failed_or_partial(self, limit: int = 50) -> list[int]:
        rows = self.conn.execute(
            """
            SELECT u.update_id
            FROM updates u
            JOIN publications p ON p.update_id = u.update_id
            WHERE p.status IN ('failed', 'partial')
            ORDER BY u.received_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [int(row["update_id"]) for row in rows]
