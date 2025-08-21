"""Zwishh - shared security helpers
=================================

This module exposes two ready-to-use **FastAPI dependencies**:

1. **`verify_service_api_key_dep`** - verifies the *service-to-service* API key
   arriving in the `X-Service-API-Key` header.

2. **`get_current_user_id_dep`** - extracts the current user ID either from the
   API-Gateway header (`X-Apigateway-Api-Userinfo`) **or** by delegating the
   check to your Auth service (`/me` endpoint) using the `Authorization`
   header.

Both helpers are *fully configurable* through a single `SecurityConfig`
instance, so the package is reusable across all Zwishh micro-services without
hard-coding environment-specific globals.

Usage example
-------------
```python
from fastapi import Depends, FastAPI
from zwishh.security import SecurityConfig, verify_service_api_key_dep, get_current_user_id_dep

config = SecurityConfig(
    service_api_key="super-secret-svc-key",
    auth_service_url="https://auth.zwishh.internal",  # points to Auth-service
    allowed_roles={"user"},
)

app = FastAPI()

# Plug into global dependencies
app.dependencies.append(Depends(verify_service_api_key_dep(config)))

@app.get("/protected")
async def protected_route(current_user: int = Depends(get_current_user_id_dep(config))):
    return {"user_id": current_user}
```
"""

from __future__ import annotations

import base64
import json
from typing import Callable, Optional, Set

import httpx
from fastapi import Header, HTTPException, Security, status, Depends

from fastapi.security import APIKeyHeader, HTTPBearer, HTTPAuthorizationCredentials
from pydantic import AnyHttpUrl, BaseModel, Field, ConfigDict

__all__ = [
    "SecurityConfig",
    "verify_service_api_key_dep",
    "get_current_user_id_dep",
]


class SecurityConfig(BaseModel):
    """Runtime settings injected into the security helpers."""

    service_api_key: str = Field(..., description="Shared secret for service-to-service calls")
    auth_service_url: AnyHttpUrl = Field(..., description="Base URL of the Auth service")
    allowed_roles: Set[str] = Field(default_factory=lambda: {"user"}, description="Roles allowed to access the endpoint")
    request_timeout: float = Field(5.0, description="Timeout (seconds) for the call to Auth service")

    # make it hashable / safe to share between threads
    model_config = ConfigDict(frozen=True) 


# ---------------------------------------------------------------------------
# Helper functions (internal)
# ---------------------------------------------------------------------------

def _decode_base64url(data: str) -> bytes:
    """Decode *URL‑safe* base64, adding missing padding automatically."""

    padding_needed = (4 - len(data) % 4) % 4
    data += "=" * padding_needed
    return base64.urlsafe_b64decode(data)


# ---------------------------------------------------------------------------
# Public dependency factories
# ---------------------------------------------------------------------------

def verify_service_api_key_dep(config: SecurityConfig) -> Callable[[str | None], None]:
    """Return a FastAPI dependency that verifies the service API key."""

    api_key_header = APIKeyHeader(name="X-Service-API-Key", auto_error=False)

    async def _dependency(api_key: str | None = Security(api_key_header)) -> None:
        if api_key != config.service_api_key:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid service API key",
            )

    return _dependency


def get_current_user_id_dep(config: SecurityConfig) -> Callable[[Optional[str], Optional[str]], int]:
    """Return a FastAPI dependency that resolves the current *user ID*.

    Resolution order:
    1. `X-Apigateway-Api-Userinfo` header (URL-safe base64 JSON)
    2. `Authorization` header - validated by calling `auth_service_url` `/me`.
    """

    security = HTTPBearer(
        bearerFormat="JWT",
        scheme_name="Authorization",
        description="Bearer token",
        auto_error=False,
    )

    async def _dependency(
        x_apigateway_api_userinfo: Optional[str] = Header(
            None, alias="X-Apigateway-Api-Userinfo"
        ),
        authorization: HTTPAuthorizationCredentials = Depends(security),
    ) -> int:
        # ------------------------------------------------------------------
        # 1. API-Gateway header path
        # ------------------------------------------------------------------
        if x_apigateway_api_userinfo:
            try:
                decoded = _decode_base64url(x_apigateway_api_userinfo)
                user_info = json.loads(decoded)
            except Exception as exc:  # pragma: no cover – defensive
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid API-Gateway user-info header: {exc}",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc

            # Role / user id validation
            _validate_user_info(user_info, config.allowed_roles)
            return int(user_info["sub"])

        # ------------------------------------------------------------------
        # 2. Fallback to Authorization header + Auth-service
        # ------------------------------------------------------------------
        if authorization is None:
            raise _missing_credentials()

        auth_header = f"{authorization.scheme} {authorization.credentials}"
        user_info = await _fetch_user_info_from_auth_service(
            auth_service_url=str(config.auth_service_url),
            authorization_header=auth_header,
            timeout=config.request_timeout,
        )

        _validate_user_info(user_info, config.allowed_roles)
        return int(user_info["sub"])

    return _dependency


# ---------------------------------------------------------------------------
# Internal helpers (not exported)
# ---------------------------------------------------------------------------

def _validate_user_info(user_info: dict, allowed_roles: Set[str]) -> None:
    """Ensure the *role* is permitted and `sub` exists in `user_info`."""

    if "sub" not in user_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing user id in token",
        )

    role = user_info.get("role")
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden role",
        )


async def _fetch_user_info_from_auth_service(
    *,
    auth_service_url: str,
    authorization_header: str,
    timeout: float,
) -> dict:
    """Call the Auth service `/me` endpoint and return the JSON payload."""

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.get(
            f"{auth_service_url.rstrip('/')}/me",
            headers={"Authorization": authorization_header},
        )

    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        return resp.json()
    except ValueError as exc:  # invalid JSON
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Auth service returned malformed JSON",
        ) from exc


def _missing_credentials() -> HTTPException:  # tiny helper to DRY
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing authentication credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
