from __future__ import annotations

import argparse
from pathlib import Path

import httpx
from pydantic import ValidationError

from app.adapters.linkedin import LinkedInAdapter
from app.adapters.openai import OpenAIAdapter
from app.adapters.pexels import PexelsAdapter
from app.adapters.telegram import TelegramAdapter
from app.adapters.wordpress import WordPressAdapter
from app.core.pipeline import run_once
from app.infra.config import get_settings
from app.infra.db import connect_db, init_database
from app.repositories.events_repo import EventsRepository
from app.repositories.lock_repo import LockRepository
from app.repositories.publications_repo import PublicationsRepository
from app.repositories.runs_repo import RunsRepository
from app.repositories.state_repo import StateRepository
from app.repositories.updates_repo import UpdatesRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pipeline")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_once_parser = subparsers.add_parser("run-once")
    run_once_parser.add_argument("--dry-run", action="store_true")
    run_once_parser.add_argument("--db-path", type=Path, default=None)

    reprocess_parser = subparsers.add_parser("reprocess")
    reprocess_parser.add_argument("--update-id", type=int, required=True)
    reprocess_parser.add_argument("--db-path", type=Path, default=None)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        settings = get_settings()
    except ValidationError as exc:
        print(f"Configuration error: {exc}")
        return 2

    db_path = args.db_path or settings.app_db_path
    migrations_dir = Path(__file__).resolve().parents[1] / "migrations"
    init_database(db_path=db_path, migrations_dir=migrations_dir)

    if args.command == "reprocess":
        print(f"Reprocess for update_id={args.update_id} is not implemented yet")
        return 0

    conn = connect_db(db_path)
    owner = "run-once"
    try:
        state_repo = StateRepository(conn)
        runs_repo = RunsRepository(conn)
        updates_repo = UpdatesRepository(conn)
        publications_repo = PublicationsRepository(conn)
        events_repo = EventsRepository(conn)
        lock_repo = LockRepository(conn)

        if not lock_repo.acquire(owner):
            print("Another run is active. Exiting.")
            return 1

        with httpx.Client(timeout=30.0) as client:
            telegram = TelegramAdapter(bot_token=settings.telegram_bot_token, client=client)
            openai = OpenAIAdapter(
                api_key=settings.openai_api_key,
                client=client,
                model=settings.openai_model,
            )
            wordpress = WordPressAdapter(
                base_url=settings.wp_base_url,
                user=settings.wp_user,
                app_password=settings.wp_app_password,
                client=client,
            )
            pexels = PexelsAdapter(api_key=settings.pexels_api_key, client=client)
            linkedin = LinkedInAdapter(
                access_token=settings.linkedin_access_token,
                person_urn=settings.linkedin_person_urn,
                client=client,
            )

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
                dry_run=args.dry_run,
                notifier=telegram.notify,
            )

        conn.commit()
        print(
            f"run_id={result.run_id} status={result.status} "
            f"updates={result.updates_processed} next_offset={result.next_offset}"
        )
        return 0
    finally:
        lock_repo = LockRepository(conn)
        lock_repo.release(owner)
        conn.commit()
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
