"""
Delivery Service SDK
===================

Async client for Zwishh Delivery-service. Wraps the HTTP endpoints exposed by
`delivery-service` and re-uses the resilient logic implemented in
`BaseServiceClient` (connection pooling, retries, API-key injection, timeout
handling, etc.).

Example
-------
```python
from zwishh.sdk.delivery import DeliveryServiceClient

delivery_client = DeliveryServiceClient(
    base_url="http://delivery.internal",  # service discovery / k8s DNS
    api_key="svc-key",                # shared secret header
)

quote = await delivery_client.get_quote(cart)
print(quote)

```
"""
from __future__ import annotations

from .base_client import BaseServiceClient

from typing import Dict, Any


class DeliveryServiceClient(BaseServiceClient):
    """High-level async wrapper for Delivery-service endpoints."""

    async def get_quote(self, pickup_address: dict, drop_address: dict, cart_total: float) -> Dict[str, Any]:
        """Get quote for order."""
        endpoint = "internal/delivery/get_quote"
        body = {"pickup_address": pickup_address, "drop_address": drop_address, "cart_total": cart_total}
        return await self.post(endpoint, json=body)

    async def place_order(
            self,
            pickup_point: dict,
            drop_point: dict,
            delivery_partner: str,
            cart_total: float,
            order_id: str,
            items: list[dict],
    ) -> Dict[str, Any]:
        """Place order."""
        endpoint = "internal/delivery/place_order"
        body = {
            "pickup_point": pickup_point,
            "drop_point": drop_point,
            "delivery_partner": delivery_partner,
            "cart_total": cart_total,
            "order_id": order_id,
            "items": items
        }
        return await self.post(endpoint, json=body)

    async def cancel_order(self, order_id: int) -> Dict[str, Any]:
        """Cancel order."""
        endpoint = "internal/delivery/cancel_order"
        return await self.post(endpoint, json={"order_id": order_id})

    async def track_order(self, order_id: int) -> Dict[str, Any]:
        """Track order."""
        endpoint = "internal/delivery/track_order"
        return await self.post(endpoint, json={"order_id": order_id})
