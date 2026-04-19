from __future__ import annotations

import base64

import httpx

from app.adapters.errors import AdapterContractError
from app.core.ports import WordPressPort


class WordPressAdapter(WordPressPort):
    def __init__(self, base_url: str, user: str, app_password: str, client: httpx.Client) -> None:
        self.base_url = base_url.rstrip("/")
        self.user = user
        self.app_password = app_password
        self.client = client

    def publish_post(self, *, title: str, html_content: str) -> str:
        token = base64.b64encode(f"{self.user}:{self.app_password}".encode()).decode("ascii")
        response = self.client.post(
            f"{self.base_url}/wp-json/wp/v2/posts",
            headers={"Authorization": f"Basic {token}"},
            json={"title": title, "content": html_content, "status": "publish"},
        )
        response.raise_for_status()
        payload = response.json()
        post_id = payload.get("id") if isinstance(payload, dict) else None
        if post_id is None:
            raise AdapterContractError("WordPress response missing id")
        return str(post_id)
