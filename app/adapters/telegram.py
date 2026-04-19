from __future__ import annotations

import json

import httpx

from app.adapters.errors import AdapterContractError
from app.core.models import InboundUpdate
from app.core.ports import TelegramPort


class TelegramAdapter(TelegramPort):
    def __init__(self, bot_token: str, client: httpx.Client, api_base_url: str = "https://api.telegram.org") -> None:
        self.bot_token = bot_token
        self.client = client
        self.api_base_url = api_base_url.rstrip("/")

    def get_updates(self, offset: int) -> list[InboundUpdate]:
        response = self.client.get(
            f"{self.api_base_url}/bot{self.bot_token}/getUpdates",
            params={"offset": offset, "timeout": 30},
        )
        response.raise_for_status()
        payload = response.json()
        raw_results = payload.get("result", [])
        if not isinstance(raw_results, list):
            raise AdapterContractError("Telegram getUpdates response missing result list")

        updates: list[InboundUpdate] = []
        for item in raw_results:
            update = self._parse_update(item)
            if update is not None:
                updates.append(update)
        return updates

    def notify(self, chat_id: int, message: str) -> None:
        response = self.client.post(
            f"{self.api_base_url}/bot{self.bot_token}/sendMessage",
            json={"chat_id": chat_id, "text": message},
        )
        response.raise_for_status()

    def _parse_update(self, raw_item: object) -> InboundUpdate | None:
        if not isinstance(raw_item, dict):
            return None
        update_id = raw_item.get("update_id")
        if not isinstance(update_id, int):
            return None

        message = raw_item.get("message")
        if not isinstance(message, dict):
            message = raw_item.get("channel_post")
        if not isinstance(message, dict):
            return None

        chat = message.get("chat")
        text = message.get("text")
        if not isinstance(chat, dict) or not isinstance(text, str):
            return None

        chat_id = chat.get("id")
        if not isinstance(chat_id, int):
            return None

        return InboundUpdate(
            update_id=update_id,
            chat_id=chat_id,
            text=text,
            raw_payload=json.dumps(raw_item, ensure_ascii=True),
        )
