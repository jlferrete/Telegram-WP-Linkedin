from __future__ import annotations

import os
from pathlib import Path

import pytest
from app.main import main as pipeline_main


def _required_env_vars() -> dict[str, str | None]:
    names = (
        "TELEGRAM_BOT_TOKEN",
        "OPENAI_API_KEY",
        "PEXELS_API_KEY",
        "WP_BASE_URL",
        "WP_USER",
        "WP_APP_PASSWORD",
        "LINKEDIN_ACCESS_TOKEN",
        "LINKEDIN_PERSON_URN",
        "E2E_TELEGRAM_TRIGGER_OFFSET",
    )
    return {name: os.environ.get(name) for name in names}


def _missing_required_env(required: dict[str, str | None]) -> list[str]:
    return [name for name, value in required.items() if value is None or value.strip() == ""]


@pytest.mark.e2e
def test_e2e_controlled_run_once_happy_path(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    required = _required_env_vars()
    missing = _missing_required_env(required)
    if missing:
        pytest.skip(f"Missing required E2E env vars: {', '.join(missing)}")

    trigger_offset_raw = required["E2E_TELEGRAM_TRIGGER_OFFSET"]
    assert trigger_offset_raw is not None
    trigger_offset = int(trigger_offset_raw)
    if trigger_offset < 0:
        pytest.fail("E2E_TELEGRAM_TRIGGER_OFFSET must be >= 0")

    db_path = tmp_path / "e2e.db"

    monkeypatch.setattr(
        "sys.argv",
        [
            "pipeline",
            "run-once",
            "--db-path",
            str(db_path),
        ],
    )
    monkeypatch.setenv("APP_DB_PATH", str(db_path))

    for key, value in required.items():
        if value is not None:
            monkeypatch.setenv(key, value)

    from app.infra.config import get_settings

    get_settings.cache_clear()
    try:
        exit_code = pipeline_main()
    finally:
        get_settings.cache_clear()

    assert exit_code == 0

    from app.infra.db import connect_db

    conn = connect_db(db_path)
    try:
        run_row = conn.execute(
            "SELECT run_id, status FROM runs ORDER BY started_at DESC LIMIT 1"
        ).fetchone()
        assert run_row is not None
        assert str(run_row["status"]) in {"success", "partial"}

        offset_row = conn.execute(
            "SELECT value FROM state WHERE key = 'telegram_offset'"
        ).fetchone()
        assert offset_row is not None
        new_offset = int(str(offset_row["value"]))
        assert new_offset >= trigger_offset

        updates_row = conn.execute(
            "SELECT COUNT(*) AS c FROM updates WHERE update_id >= ?",
            (trigger_offset,),
        ).fetchone()
        assert updates_row is not None
        assert int(updates_row["c"]) >= 1

        pub_row = conn.execute(
            """
            SELECT COUNT(*) AS c
            FROM publications p
            JOIN updates u ON u.update_id = p.update_id
            WHERE u.update_id >= ?
            """,
            (trigger_offset,),
        ).fetchone()
        assert pub_row is not None
        assert int(pub_row["c"]) >= 1
    finally:
        conn.close()
