from __future__ import annotations

import logging
from typing import Any, Dict

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
)

logger = logging.getLogger("zwishh.sdk")

__all__ = [
    "ServiceClientError",
    "ServiceClientNotFound",
    "ServiceClientUnauthorized",
    "BaseServiceClient",
]

class ServiceClientError(Exception):
    """Base class for service-specific errors."""


class ServiceClientNotFound(ServiceClientError):
    """Service resource not found error."""


class ServiceClientUnauthorized(ServiceClientError):
    """Service unauthorized error."""


class BaseServiceClient:
    """Reusable async HTTP client with retries and API-key injection."""

    _DEFAULT_TIMEOUT = httpx.Timeout(5.0, read=10.0)

    def __init__(self, base_url: str, api_key: str = "", timeout: httpx.Timeout | None = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout or self._DEFAULT_TIMEOUT

    # ------------------------------------------------------------------ #
    # Public helpers                                                     #
    # ------------------------------------------------------------------ #
    async def get(self, endpoint: str, **kwargs: Any) -> Any:  # noqa: ANN401
        return await self._request("GET", endpoint, **kwargs)

    async def post(self, endpoint: str, **kwargs: Any) -> Any:  # noqa: ANN401
        return await self._request("POST", endpoint, **kwargs)

    async def put(self, endpoint: str, **kwargs: Any) -> Any:  # noqa: ANN401
        return await self._request("PUT", endpoint, **kwargs)

    async def patch(self, endpoint: str, **kwargs: Any) -> Any:  # noqa: ANN401
        return await self._request("PATCH", endpoint, **kwargs)

    async def delete(self, endpoint: str, **kwargs: Any) -> Any:  # noqa: ANN401
        return await self._request("DELETE", endpoint, **kwargs)

    # ------------------------------------------------------------------ #
    # Internal request wrapper                                           #
    # ------------------------------------------------------------------ #
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        reraise=True
    )
    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        json: Any | None = None,
        params: Dict[str, Any] | None = None,
        headers: Dict[str, str] | None = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_headers = self._merge_headers(headers)

        logger.info(f"Request: {method} {url}")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:   
            try:
                response = await client.request(
                    method=method,
                    url=url,
                    json=json,
                    params=params,
                    headers=request_headers
                )
                response.raise_for_status()
                return response.json() if response.content else {}
            except httpx.HTTPStatusError as exc:
                logger.error(f"Response: {exc.response.text}")
                self._handle_http_error(exc)

    # ------------------------------------------------------------------ #
    # Helpers                                                            #
    # ------------------------------------------------------------------ #
    def _merge_headers(self, extra: Dict[str, str] | None) -> Dict[str, str]:
        base = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            base["X-Service-API-Key"] = self.api_key
        if extra:
            base.update(extra.copy())
        return base

    @staticmethod
    def _handle_http_error(exc: httpx.HTTPStatusError) -> None:  # noqa: ANN001
        status = exc.response.status_code
        if status == 404:
            raise ServiceClientNotFound(exc.response.text) from exc
        if status in (401, 403):
            raise ServiceClientUnauthorized() from exc
        raise ServiceClientError(f"Service responded with {status}") from exc


