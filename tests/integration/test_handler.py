# lambda-auth/tests/integration/test_handler.py
from __future__ import annotations

import json
import os
import uuid
from unittest.mock import MagicMock, patch

import pytest

os.environ.update({
    "USERS_TABLE": "users",
    "JWT_SECRET": "supersecretfortesting1234567890ab",
    "JWT_ISSUER": "door-auth",
    "JWT_EXPIRY_SECONDS": "900",
    "ALLOWED_ORIGINS": "http://localhost:5173",
    "AWS_REGION": "us-east-1",
    "AWS_DEFAULT_REGION": "us-east-1",
    "AWS_ACCESS_KEY_ID": "test",
    "AWS_SECRET_ACCESS_KEY": "test",
})


def _make_event(method: str, path: str, body: dict | None = None, origin: str = "http://localhost:5173") -> dict:
    return {
        "requestContext": {
            "http": {"method": method, "path": path},
            "requestId": str(uuid.uuid4()),
        },
        "headers": {"origin": origin, "content-type": "application/json"},
        "body": json.dumps(body) if body else None,
    }


class TestLoginIntegration:
    def test_options_devuelve_204_con_cors(self):
        from src.handler import lambda_handler
        event = _make_event("OPTIONS", "/auth/login")
        resp = lambda_handler(event, None)
        assert resp["statusCode"] == 204
        assert "Access-Control-Allow-Origin" in resp["headers"]

    def test_ruta_inexistente_devuelve_404(self):
        from src.handler import lambda_handler
        event = _make_event("GET", "/not/found")
        resp = lambda_handler(event, None)
        assert resp["statusCode"] == 404

    def test_body_invalido_devuelve_400(self):
        from src.handler import lambda_handler
        event = _make_event("POST", "/auth/login", body={"username": ""})
        resp = lambda_handler(event, None)
        assert resp["statusCode"] == 400

    def test_origin_no_permitido_no_incluye_cors(self):
        from src.handler import lambda_handler
        event = _make_event("POST", "/auth/login", body={"username": "u", "password": "p"}, origin="https://evil.com")
        resp = lambda_handler(event, None)
        assert "Access-Control-Allow-Origin" not in resp.get("headers", {})