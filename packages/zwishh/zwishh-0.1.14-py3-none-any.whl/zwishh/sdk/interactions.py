"""
Interaction Service SDK
========================

Async client for Zwishh Interaction-service. Wraps the HTTP endpoints exposed by
`interaction-service` and re-uses the resilient logic implemented in
`BaseServiceClient` (connection pooling, retries, API-key injection, timeout
handling, etc.).

Example
-------
```python
from zwishh.sdk.interactions import InteractionServiceClient

interaction_client = InteractionServiceClient(
    base_url="http://interaction.internal",  # service discovery / k8s DNS
    api_key="svc-key",                # shared secret header
)

followers_count = await interaction_client.get_followers_count(123)
print(followers_count)
```
"""
from __future__ import annotations

from .base_client import BaseServiceClient

class InteractionServiceClient(BaseServiceClient):
    """High-level async wrapper for Interaction-service endpoints."""
    async def get_followers_count(self, seller_id: int):
        endpoint = f"sellers/{seller_id}/followers/count"
        return await self.get(endpoint)

    async def get_likes_count(self, product_ids: list[int]):
        endpoint = "products/likes/count"
        params = {"product_ids": product_ids}
        return await self.get(endpoint, params=params)

    async def get_views_count(self, product_ids: list[int]):
        endpoint = "products/view-totals"
        params = {"product_ids": product_ids}
        return await self.get(endpoint, params=params)