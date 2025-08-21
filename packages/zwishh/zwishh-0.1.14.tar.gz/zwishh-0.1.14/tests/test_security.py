"""
Unit tests for zwishh.security helpers.

Run with:  pytest -q
"""

import base64
import json
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
import respx
import httpx

from zwishh.utils.security import (
    SecurityConfig,
    verify_service_api_key_dep,
    get_current_user_id_dep,
)

CONFIG = SecurityConfig(
    service_api_key="svc-secret",
    auth_service_url="https://auth.example.test",
    allowed_roles={"seller"},
)


# --------------------------------------------------------------------------- #
# Helper FastAPI app so we can exercise dependencies just like in production. #
# --------------------------------------------------------------------------- #
app = FastAPI()

@app.get("/internal/ping")
async def _ping(_: None = Depends(verify_service_api_key_dep(CONFIG))):  # noqa: FBT001
    return {"ok": True}


@app.get("/me")
async def _me(current_user: int = Depends(get_current_user_id_dep(CONFIG))):
    return {"user_id": current_user}


client = TestClient(app)


# --------------------------------------------------------------------------- #
# Tests – Service‑to‑service key                                             #
# --------------------------------------------------------------------------- #
def test_service_api_key_ok():
    res = client.get("/internal/ping", headers={"X-Service-API-Key": "svc-secret"})
    assert res.status_code == 200 and res.json() == {"ok": True}


def test_service_api_key_bad():
    res = client.get("/internal/ping", headers={"X-Service-API-Key": "WRONG"})
    assert res.status_code == 403


# --------------------------------------------------------------------------- #
# Tests – User ID resolver                                                   #
# --------------------------------------------------------------------------- #
def _encode_userinfo(payload: dict) -> str:
    raw = json.dumps(payload).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def test_userinfo_header_path():
    ui_header = _encode_userinfo({"sub": 42, "role": "seller"})
    res = client.get("/me", headers={"X-Apigateway-Api-Userinfo": ui_header})
    assert res.status_code == 200 and res.json() == {"user_id": 42}


@respx.mock  # intercept outbound HTTP call
def test_authorization_header_path():
    token = "Bearer abc.def.ghi"
    mock_resp = {"sub": 99, "role": "seller"}
    respx.get("https://auth.example.test/me").mock(return_value=httpx.Response(200, json=mock_resp))

    res = client.get("/me", headers={"Authorization": token})
    assert res.status_code == 200 and res.json() == {"user_id": 99}


@respx.mock
def test_authorization_invalid_token():
    token = "Bearer broken"
    respx.get("https://auth.example.test/me").mock(return_value=httpx.Response(401))
    res = client.get("/me", headers={"Authorization": token})
    assert res.status_code == 401
