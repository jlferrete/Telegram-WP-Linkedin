from __future__ import annotations

import json

import httpx
from pydantic import BaseModel, ValidationError

from app.adapters.errors import AdapterContractError
from app.core.models import GeneratedPost
from app.core.ports import OpenAIPort


class _GeneratedPostPayload(BaseModel):
    title: str
    wordpress_html: str
    linkedin_text: str


class OpenAIAdapter(OpenAIPort):
    def __init__(
        self,
        api_key: str,
        client: httpx.Client,
        model: str = "gpt-4.1-mini",
        api_base_url: str = "https://api.openai.com/v1",
    ) -> None:
        self.api_key = api_key
        self.client = client
        self.model = model
        self.api_base_url = api_base_url.rstrip("/")

    def generate_from_url(self, *, url: str, hint_title: str) -> GeneratedPost:
        prompt = (
            "Genera contenido para publicar en WordPress y LinkedIn en JSON con "
            "campos: title, wordpress_html, linkedin_text. "
            f"URL: {url}. Titulo sugerido: {hint_title}."
        )
        response = self.client.post(
            f"{self.api_base_url}/responses",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model,
                "input": prompt,
                "text": {"format": {"type": "json_object"}},
            },
        )
        response.raise_for_status()
        payload = response.json()

        output_text = self._extract_output_text(payload)
        try:
            parsed = _GeneratedPostPayload.model_validate(json.loads(output_text))
        except (ValidationError, json.JSONDecodeError) as exc:
            raise AdapterContractError(f"OpenAI response contract mismatch: {exc}") from exc

        return GeneratedPost(
            title=parsed.title,
            wordpress_html=parsed.wordpress_html,
            linkedin_text=parsed.linkedin_text,
        )

    def _extract_output_text(self, payload: dict[str, object]) -> str:
        output = payload.get("output")
        if not isinstance(output, list):
            raise AdapterContractError("OpenAI response missing output list")

        for item in output:
            if not isinstance(item, dict):
                continue
            content = item.get("content")
            if not isinstance(content, list):
                continue
            for chunk in content:
                if not isinstance(chunk, dict):
                    continue
                if chunk.get("type") == "output_text" and isinstance(chunk.get("text"), str):
                    text_value = chunk["text"]
                    if isinstance(text_value, str):
                        return text_value

        raise AdapterContractError("OpenAI response missing output_text content")
