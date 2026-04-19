from __future__ import annotations

from typing import Protocol

from app.core.models import GeneratedPost, InboundUpdate


class TelegramPort(Protocol):
    def get_updates(self, offset: int) -> list[InboundUpdate]: ...

    def notify(self, chat_id: int, message: str) -> None: ...


class OpenAIPort(Protocol):
    def generate_from_url(self, *, url: str, hint_title: str) -> GeneratedPost: ...


class WordPressPort(Protocol):
    def publish_post(self, *, title: str, html_content: str) -> str: ...


class PexelsPort(Protocol):
    def find_image_url(self, query: str) -> str | None: ...


class LinkedInPort(Protocol):
    def publish_post(self, *, text: str, article_url: str, image_url: str | None = None) -> str: ...
