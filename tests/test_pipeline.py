from __future__ import annotations

from pathlib import Path

from app.core.models import GeneratedPost, InboundUpdate
from app.core.pipeline import run_once
from app.infra.db import init_database
from app.repositories.events_repo import EventsRepository
from app.repositories.publications_repo import PublicationsRepository
from app.repositories.runs_repo import RunsRepository
from app.repositories.state_repo import StateRepository
from app.repositories.updates_repo import UpdatesRepository


class DummyTelegram:
    def __init__(self, updates: list[InboundUpdate]) -> None:
        self._updates = updates
        self.notifications: list[tuple[int, str]] = []

    def get_updates(self, offset: int) -> list[InboundUpdate]:
        _ = offset
        return self._updates

    def notify(self, chat_id: int, message: str) -> None:
        self.notifications.append((chat_id, message))


class DummyOpenAI:
    def __init__(self) -> None:
        self.calls = 0

    def generate_from_url(self, *, url: str, hint_title: str) -> GeneratedPost:
        self.calls += 1
        return GeneratedPost(
            title=hint_title,
            wordpress_html=f"<p>{url}</p>",
            linkedin_text=f"Resumen {hint_title}",
        )


class DummyWordPress:
    def __init__(self) -> None:
        self.calls = 0

    def publish_post(self, *, title: str, html_content: str) -> str:
        self.calls += 1
        _ = (title, html_content)
        return "wp-1"


class DummyPexels:
    def __init__(self) -> None:
        self.calls = 0

    def find_image_url(self, query: str) -> str | None:
        self.calls += 1
        _ = query
        return "https://images.example.com/1.jpg"


class DummyLinkedIn:
    def __init__(self) -> None:
        self.calls = 0

    def publish_post(self, *, text: str, article_url: str, image_url: str | None = None) -> str:
        self.calls += 1
        _ = (text, article_url, image_url)
        return "li-1"


class FlakyLinkedIn(DummyLinkedIn):
    def __init__(self, fail_times: int) -> None:
        super().__init__()
        self.fail_times = fail_times

    def publish_post(self, *, text: str, article_url: str, image_url: str | None = None) -> str:
        self.calls += 1
        _ = (text, article_url, image_url)
        if self.calls <= self.fail_times:
            import httpx

            request = httpx.Request("POST", "https://api.linkedin.com/v2/ugcPosts")
            response = httpx.Response(status_code=503, request=request)
            raise httpx.HTTPStatusError("temporary", request=request, response=response)
        return "li-1"


def test_run_once_dry_run_does_not_advance_offset(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    init_database(db_path=db_path, migrations_dir=migrations_dir)

    from app.infra.db import connect_db

    conn = connect_db(db_path)
    try:
        state_repo = StateRepository(conn)
        runs_repo = RunsRepository(conn)
        updates_repo = UpdatesRepository(conn)
        publications_repo = PublicationsRepository(conn)
        events_repo = EventsRepository(conn)
        updates = [InboundUpdate(101, 1, "https://example.com hello", "{}")]
        telegram = DummyTelegram(updates)
        openai = DummyOpenAI()
        wordpress = DummyWordPress()
        pexels = DummyPexels()
        linkedin = DummyLinkedIn()

        result = run_once(
            telegram=telegram,
            openai=openai,
            wordpress=wordpress,
            pexels=pexels,
            linkedin=linkedin,
            state_repo=state_repo,
            runs_repo=runs_repo,
            updates_repo=updates_repo,
            publications_repo=publications_repo,
            events_repo=events_repo,
            dry_run=True,
            notifier=telegram.notify,
        )
        conn.commit()

        assert result.status == "success"
        assert result.next_offset == 102
        assert state_repo.get("telegram_offset") == "0"
        assert openai.calls == 0
        assert wordpress.calls == 0
        assert pexels.calls == 0
        assert linkedin.calls == 0
    finally:
        conn.close()


def test_run_once_retries_transient_linkedin_failures(tmp_path: Path) -> None:
    db_path = tmp_path / "app.db"
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    init_database(db_path=db_path, migrations_dir=migrations_dir)

    from app.infra.db import connect_db

    conn = connect_db(db_path)
    try:
        state_repo = StateRepository(conn)
        runs_repo = RunsRepository(conn)
        updates_repo = UpdatesRepository(conn)
        publications_repo = PublicationsRepository(conn)
        events_repo = EventsRepository(conn)

        updates = [InboundUpdate(201, 1, "https://example.com retry", "{}")]
        telegram = DummyTelegram(updates)
        linkedin = FlakyLinkedIn(fail_times=2)

        result = run_once(
            telegram=telegram,
            openai=DummyOpenAI(),
            wordpress=DummyWordPress(),
            pexels=DummyPexels(),
            linkedin=linkedin,
            state_repo=state_repo,
            runs_repo=runs_repo,
            updates_repo=updates_repo,
            publications_repo=publications_repo,
            events_repo=events_repo,
            dry_run=False,
            notifier=telegram.notify,
        )
        conn.commit()

        assert result.status == "success"
        assert state_repo.get("telegram_offset") == "202"
        assert publications_repo.get_status(201) == "success"
        assert linkedin.calls == 3

        retry_rows = conn.execute(
            "SELECT COUNT(*) AS c FROM events "
            "WHERE update_id = 201 AND stage = 'linkedin' AND status = 'retry'"
        ).fetchone()
        assert retry_rows is not None
        assert int(retry_rows["c"]) == 2
    finally:
        conn.close()
