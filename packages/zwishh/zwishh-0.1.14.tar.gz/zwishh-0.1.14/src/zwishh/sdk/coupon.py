"""
Coupon Service SDK
===================

Async client for Zwishh Coupon-service. Wraps the HTTP endpoints exposed by
`coupon-service` and re-uses the resilient logic implemented in
`BaseServiceClient` (connection pooling, retries, API-key injection, timeout
handling, etc.).

Example
-------
```python
from zwishh.sdk.coupon import CouponServiceClient

coupon_client = CouponServiceClient(
    base_url="http://coupon.internal",  # service discovery / k8s DNS
    api_key="svc-key",                # shared secret header
)

    coupon = await coupon_client.get_coupon("COUPON_CODE")
print(coupon)

```
"""
from __future__ import annotations

from .base_client import BaseServiceClient

from typing import Dict, Any


class CouponServiceClient(BaseServiceClient):
    """High-level async wrapper for Coupon-service endpoints."""
    async def get_coupon(self, coupon_code: str) -> Dict[str, Any]:
        """Get coupon."""
        endpoint = f"internal/coupon/{coupon_code}"
        return await self.get(endpoint)

    async def validate_coupon(
            self,
            coupon_code: str,
            user_id: str,
            shop_id: str,
            cart_total: float
    ) -> Dict[str, Any]:
        """Validate coupon."""
        endpoint = "internal/coupon/validate"
        body = {
            "coupon_code": coupon_code,
            "user_id": user_id,
            "shop_id": shop_id,
            "cart_total": cart_total
        }
        return await self.post(endpoint, json=body)
    
    async def apply_coupon(self, coupon_code: str) -> Dict[str, Any]:
        """Apply coupon."""
        endpoint = "internal/coupon/apply"
        return await self.post(endpoint, json={"coupon_code": coupon_code})