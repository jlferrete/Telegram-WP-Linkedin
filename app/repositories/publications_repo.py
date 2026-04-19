from __future__ import annotations

import sqlite3


class PublicationsRepository:
    def __init__(self, conn: sqlite3.Connection) -> None:
        self.conn = conn

    def upsert_status(
        self,
        update_id: int,
        status: str,
        last_error: str | None = None,
    ) -> None:
        self.conn.execute(
            """
            INSERT INTO publications(update_id, status, last_error, updated_at)
            VALUES(?, ?, ?, datetime('now'))
            ON CONFLICT(update_id) DO UPDATE SET
              status=excluded.status,
              last_error=excluded.last_error,
              updated_at=datetime('now')
            """,
            (update_id, status, last_error),
        )

    def mark_wordpress_success(self, update_id: int, wp_post_id: str) -> None:
        self.conn.execute(
            """
            INSERT INTO publications(update_id, wp_post_id, status, updated_at)
            VALUES(?, ?, 'partial', datetime('now'))
            ON CONFLICT(update_id) DO UPDATE SET
              wp_post_id=excluded.wp_post_id,
              status=CASE
                WHEN publications.linkedin_post_id IS NULL THEN 'partial'
                ELSE 'success'
              END,
              updated_at=datetime('now')
            """,
            (update_id, wp_post_id),
        )

    def mark_linkedin_success(self, update_id: int, linkedin_post_id: str) -> None:
        self.conn.execute(
            """
            INSERT INTO publications(update_id, linkedin_post_id, status, updated_at)
            VALUES(?, ?, 'partial', datetime('now'))
            ON CONFLICT(update_id) DO UPDATE SET
              linkedin_post_id=excluded.linkedin_post_id,
              status=CASE
                WHEN publications.wp_post_id IS NULL THEN 'partial'
                ELSE 'success'
              END,
              updated_at=datetime('now')
            """,
            (update_id, linkedin_post_id),
        )

    def get_status(self, update_id: int) -> str | None:
        row = self.conn.execute(
            "SELECT status FROM publications WHERE update_id = ?",
            (update_id,),
        ).fetchone()
        if row is None:
            return None
        return str(row["status"])
