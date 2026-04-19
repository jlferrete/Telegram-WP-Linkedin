from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class InboundUpdate:
    update_id: int
    chat_id: int
    text: str
    raw_payload: str


@dataclass(frozen=True)
class LinkPayload:
    source_url: str
    source_title: str


@dataclass(frozen=True)
class GeneratedPost:
    title: str
    wordpress_html: str
    linkedin_text: str


@dataclass(frozen=True)
class PublicationResult:
    status: str
    wp_post_id: str | None
    linkedin_post_id: str | None
    last_error: str | None
