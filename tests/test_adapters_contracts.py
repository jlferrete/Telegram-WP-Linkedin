from __future__ import annotations

import httpx

from app.adapters.openai import OpenAIAdapter
from app.adapters.pexels import PexelsAdapter
from app.adapters.telegram import TelegramAdapter


def test_telegram_adapter_parses_valid_update() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        _ = request
        return httpx.Response(
            status_code=200,
            json={
                "ok": True,
                "result": [
                    {
                        "update_id": 100,
                        "message": {"chat": {"id": 10}, "text": "https://example.com test"},
                    }
                ],
            },
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = TelegramAdapter(bot_token="x", client=client, api_base_url="https://api.telegram.org")

    updates = adapter.get_updates(offset=0)
    assert len(updates) == 1
    assert updates[0].update_id == 100
    assert updates[0].chat_id == 10


def test_openai_adapter_parses_json_output_text() -> None:
    payload = {
        "output": [
            {
                "content": [
                    {
                        "type": "output_text",
                        "text": '{"title":"A","wordpress_html":"<p>x</p>","linkedin_text":"B"}',
                    }
                ]
            }
        ]
    }

    def handler(request: httpx.Request) -> httpx.Response:
        _ = request
        return httpx.Response(status_code=200, json=payload)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = OpenAIAdapter(api_key="k", client=client, api_base_url="https://api.openai.com/v1")

    generated = adapter.generate_from_url(url="https://example.com", hint_title="hint")
    assert generated.title == "A"
    assert generated.linkedin_text == "B"


def test_pexels_adapter_returns_none_when_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        _ = request
        return httpx.Response(status_code=200, json={"photos": []})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    adapter = PexelsAdapter(api_key="k", client=client, api_base_url="https://api.pexels.com/v1")
    assert adapter.find_image_url("anything") is None
