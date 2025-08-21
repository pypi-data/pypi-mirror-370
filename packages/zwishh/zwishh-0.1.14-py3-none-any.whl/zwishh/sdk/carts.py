"""Cart Service SDK
=================

Async client for Zwishh Cart-service. Wraps the HTTP endpoints exposed by
`cart-service` and re-uses the resilient logic implemented in
`BaseServiceClient` (connection pooling, retries, API-key injection, timeout
handling, etc.).

Example
-------
```python
from zwishh.sdk.cart import CartServiceClient

cart_client = CartServiceClient(
    base_url="http://cart.internal",  # service discovery / k8s DNS
    api_key="svc-key",                # shared secret header
)

cart = await cart_client.get_cart(123)
print(cart["items_total"])

```
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from .base_client import BaseServiceClient


class CartServiceClient(BaseServiceClient):
    """High-level async wrapper for Cart-service endpoints."""

    # ------------------------------------------------------------------ #
    # Public API                                                         #
    # ------------------------------------------------------------------ #
    async def get_cart(self, cart_id: int) -> Dict[str, Any]:
        """Return cart details for `cart_id`.

        Raises
        ------
        ServiceClientNotFound
            If the cart does not exist (404).
        ServiceClientError
            For any other non-2xx response.
        """

        endpoint = f"internal/carts/{cart_id}"
        return await self.get(endpoint)  # type: ignore[return-value]

    async def delete_cart(self, cart_id: int) -> Optional[Dict[str, Any]]:
        """Delete a cart.

        Returns the service's JSON response (often empty {}) or None if no
        body was returned.
        """

        endpoint = f"internal/carts/{cart_id}"
        return await self.delete(endpoint)  # type: ignore[return-value]

    async def unlock_cart(self, cart_id: int) -> Optional[Dict[str, Any]]:
        """Unlock a cart."""

        endpoint = f"internal/carts/{cart_id}/unlock"
        return await self.post(endpoint)  # type: ignore[return-value]