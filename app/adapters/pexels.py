from __future__ import annotations

import httpx

from app.adapters.errors import AdapterContractError
from app.core.ports import PexelsPort


class PexelsAdapter(PexelsPort):
    def __init__(
        self,
        api_key: str,
        client: httpx.Client,
        api_base_url: str = "https://api.pexels.com/v1",
    ) -> None:
        self.api_key = api_key
        self.client = client
        self.api_base_url = api_base_url.rstrip("/")

    def find_image_url(self, query: str) -> str | None:
        response = self.client.get(
            f"{self.api_base_url}/search",
            headers={"Authorization": self.api_key},
            params={"query": query, "per_page": 1},
        )
        response.raise_for_status()
        payload = response.json()
        photos = payload.get("photos") if isinstance(payload, dict) else None
        if not isinstance(photos, list) or not photos:
            return None

        first = photos[0]
        if not isinstance(first, dict):
            raise AdapterContractError("Pexels photo item malformed")
        src = first.get("src")
        if not isinstance(src, dict):
            raise AdapterContractError("Pexels photo src malformed")
        image_url = src.get("large")
        if image_url is None:
            image_url = src.get("original")
        if image_url is None:
            return None
        if not isinstance(image_url, str):
            raise AdapterContractError("Pexels image url must be string")
        return image_url
