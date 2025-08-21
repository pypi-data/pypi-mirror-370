"""
Order Service SDK
=================

Async client for Zwishh Order-service. Wraps the HTTP endpoints exposed by
`order-service` and re-uses the resilient logic implemented in
`BaseServiceClient` (connection pooling, retries, API-key injection, timeout
handling, etc.).

Example
-------
```python
from zwishh.sdk.orders import OrderServiceClient

order_client = OrderServiceClient(
    base_url="http://order.internal",  # service discovery / k8s DNS
    api_key="svc-key",                # shared secret header
)

order = await order_client.create_order(cart)
print(order["id"])

```
"""
from __future__ import annotations

from .base_client import BaseServiceClient

from typing import Dict, Any

class OrderServiceClient(BaseServiceClient):
    """High-level async wrapper for Order-service endpoints."""

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #  
    async def create_order(
        self,
        cart: dict,
    ) -> Dict[str, Any]:
        """Create an order from the cart."""

        endpoint = "internal/orders"
        data = {
            "cart": cart
        }
        return await self.post(endpoint, json=data)