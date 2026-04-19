from __future__ import annotations

import httpx

from app.adapters.errors import AdapterContractError
from app.core.ports import LinkedInPort


class LinkedInAdapter(LinkedInPort):
    def __init__(
        self,
        access_token: str,
        person_urn: str,
        client: httpx.Client,
        api_base_url: str = "https://api.linkedin.com/v2",
    ) -> None:
        self.access_token = access_token
        self.person_urn = person_urn
        self.client = client
        self.api_base_url = api_base_url.rstrip("/")

    def publish_post(self, *, text: str, article_url: str, image_url: str | None = None) -> str:
        media_url = image_url if image_url is not None else article_url
        media_category = "IMAGE" if image_url is not None else "ARTICLE"

        payload = {
            "author": self.person_urn,
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {"text": text},
                    "shareMediaCategory": media_category,
                    "media": [{"status": "READY", "originalUrl": media_url}],
                }
            },
            "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
        }

        response = self.client.post(
            f"{self.api_base_url}/ugcPosts",
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
            },
            json=payload,
        )
        response.raise_for_status()

        response_id = response.headers.get("x-restli-id")
        if response_id:
            return str(response_id)

        data = response.json() if response.content else {}
        post_id = data.get("id") if isinstance(data, dict) else None
        if post_id is None:
            raise AdapterContractError("LinkedIn response missing post id")
        return str(post_id)
