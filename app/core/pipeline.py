from __future__ import annotations

from dataclasses import dataclass
from typing import Callable
from uuid import uuid4

from app.infra.retry import RetryConfig, is_retryable_exception, retry_call
from app.core.models import InboundUpdate
from app.core.ports import LinkedInPort, OpenAIPort, PexelsPort, TelegramPort, WordPressPort
from app.repositories.events_repo import EventsRepository
from app.repositories.publications_repo import PublicationsRepository
from app.repositories.runs_repo import RunsRepository
from app.repositories.state_repo import StateRepository
from app.repositories.updates_repo import UpdatesRepository


def _extract_link_payload(text: str) -> tuple[str | None, str]:
    tokens = text.split()
    candidate_url = next((token for token in tokens if token.startswith("http://") or token.startswith("https://")), None)
    if candidate_url is None:
        return None, text[:80]
    title_hint = text.replace(candidate_url, "").strip()
    if not title_hint:
        title_hint = "Contenido compartido desde Telegram"
    return candidate_url, title_hint


@dataclass(frozen=True)
class RunResult:
    run_id: str
    status: str
    updates_processed: int
    next_offset: int | None


def run_once(
    *,
    telegram: TelegramPort,
    openai: OpenAIPort,
    wordpress: WordPressPort,
    pexels: PexelsPort,
    linkedin: LinkedInPort,
    state_repo: StateRepository,
    runs_repo: RunsRepository,
    updates_repo: UpdatesRepository,
    publications_repo: PublicationsRepository,
    events_repo: EventsRepository,
    dry_run: bool,
    notifier: Callable[[int, str], None] | None = None,
) -> RunResult:
    run_id = str(uuid4())
    runs_repo.create_started(run_id)

    offset_raw = state_repo.get("telegram_offset") or "0"
    offset = int(offset_raw)

    events_repo.add(run_id=run_id, stage="polling", status="started", detail=f"offset={offset}")
    updates = sorted(telegram.get_updates(offset=offset), key=lambda item: item.update_id)
    events_repo.add(
        run_id=run_id,
        stage="polling",
        status="success",
        detail=f"updates={len(updates)}",
    )

    if not updates:
        runs_repo.finish(run_id, status="success")
        return RunResult(run_id=run_id, status="success", updates_processed=0, next_offset=None)

    has_failures = False
    processed_count = 0

    for update in updates:
        processed_count += 1
        _process_update(
            run_id=run_id,
            update=update,
            updates_repo=updates_repo,
            publications_repo=publications_repo,
            events_repo=events_repo,
            dry_run=dry_run,
            openai=openai,
            wordpress=wordpress,
            pexels=pexels,
            linkedin=linkedin,
            notifier=notifier,
        )

        status_row = publications_repo.get_status(update.update_id)
        if status_row in {"failed", "partial"}:
            has_failures = True

    max_update = max(update.update_id for update in updates)
    next_offset = max_update + 1

    if not dry_run:
        state_repo.set("telegram_offset", str(next_offset))

    runs_repo.finish(run_id, status="partial" if has_failures else "success")
    return RunResult(
        run_id=run_id,
        status="partial" if has_failures else "success",
        updates_processed=processed_count,
        next_offset=next_offset,
    )


def _process_update(
    *,
    run_id: str,
    update: InboundUpdate,
    updates_repo: UpdatesRepository,
    publications_repo: PublicationsRepository,
    events_repo: EventsRepository,
    dry_run: bool,
    openai: OpenAIPort,
    wordpress: WordPressPort,
    pexels: PexelsPort,
    linkedin: LinkedInPort,
    notifier: Callable[[int, str], None] | None,
) -> None:
    if updates_repo.exists(update.update_id):
        events_repo.add(
            run_id=run_id,
            update_id=update.update_id,
            stage="dedupe",
            status="skipped",
            detail="update already processed",
        )
        return

    updates_repo.insert(
        update_id=update.update_id,
        chat_id=update.chat_id,
        text=update.text,
        run_id=run_id,
        source_payload=update.raw_payload,
    )

    source_url, title_hint = _extract_link_payload(update.text)
    if source_url is None:
        publications_repo.upsert_status(update_id=update.update_id, status="failed", last_error="url not found")
        events_repo.add(
            run_id=run_id,
            update_id=update.update_id,
            stage="extract",
            status="failed",
            detail="No URL found in Telegram message",
        )
        return

    if dry_run:
        publications_repo.upsert_status(update_id=update.update_id, status="pending", last_error=None)
        events_repo.add(
            run_id=run_id,
            update_id=update.update_id,
            stage="publish",
            status="skipped",
            detail="dry-run enabled",
        )
        return

    wp_post_id: str | None = None
    retry_config = RetryConfig(attempts=3, base_delay_seconds=0.5, max_delay_seconds=4.0, jitter_factor=0.2)

    def on_retry(stage: str) -> Callable[[int, Exception, float], None]:
        def _handler(attempt: int, exc: Exception, delay: float) -> None:
            events_repo.add(
                run_id=run_id,
                update_id=update.update_id,
                stage=stage,
                status="retry",
                detail=f"attempt={attempt};delay={delay:.2f};error={exc}",
            )

        return _handler

    try:
        generated = retry_call(
            lambda: openai.generate_from_url(url=source_url, hint_title=title_hint),
            config=retry_config,
            should_retry=is_retryable_exception,
            on_retry=on_retry("openai"),
        )
        wp_post_id = retry_call(
            lambda: wordpress.publish_post(title=generated.title, html_content=generated.wordpress_html),
            config=retry_config,
            should_retry=is_retryable_exception,
            on_retry=on_retry("wordpress"),
        )
        publications_repo.mark_wordpress_success(update_id=update.update_id, wp_post_id=wp_post_id)

        image_url = retry_call(
            lambda: pexels.find_image_url(generated.title),
            config=retry_config,
            should_retry=is_retryable_exception,
            on_retry=on_retry("pexels"),
        )
        linkedin_post_id = retry_call(
            lambda: linkedin.publish_post(
                text=generated.linkedin_text,
                article_url=source_url,
                image_url=image_url,
            ),
            config=retry_config,
            should_retry=is_retryable_exception,
            on_retry=on_retry("linkedin"),
        )
        publications_repo.mark_linkedin_success(update_id=update.update_id, linkedin_post_id=linkedin_post_id)
        events_repo.add(
            run_id=run_id,
            update_id=update.update_id,
            stage="publish",
            status="success",
            detail=f"wp={wp_post_id};linkedin={linkedin_post_id}",
        )
        if notifier is not None:
            notifier(update.chat_id, f"Publicado OK. update_id={update.update_id}")
    except Exception as exc:
        status = "partial" if wp_post_id else "failed"
        publications_repo.upsert_status(update_id=update.update_id, status=status, last_error=str(exc))
        events_repo.add(
            run_id=run_id,
            update_id=update.update_id,
            stage="publish",
            status="failed",
            detail=str(exc),
        )
        if notifier is not None:
            notifier(update.chat_id, f"Fallo publicacion update_id={update.update_id}: {exc}")
