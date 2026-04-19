from __future__ import annotations

import sqlite3


class LockRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def acquire(self, owner: str) -> bool:
        result = self.conn.execute(
            """
            UPDATE process_lock
            SET locked = 1,
                owner = ?,
                updated_at = datetime('now')
            WHERE id = 1 AND locked = 0
            """,
            (owner,),
        )
        return result.rowcount == 1

    def release(self, owner: str) -> None:
        self.conn.execute(
            """
            UPDATE process_lock
            SET locked = 0,
                owner = NULL,
                updated_at = datetime('now')
            WHERE id = 1 AND owner = ?
            """,
            (owner,),
        )
