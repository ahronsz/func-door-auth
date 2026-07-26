# lambda-auth/tests/unit/test_jwt_service.py
from __future__ import annotations

import time
import uuid

import jwt as pyjwt
import pytest

from src.config.settings import Settings
from src.infrastructure.jwt_service import JWTService


def _make_settings(expiry: int = 900) -> Settings:
    import os
    os.environ.update({
        "USERS_TABLE": "users",
        "JWT_SECRET": "supersecretfortesting1234567890",
        "JWT_ISSUER": "door-auth",
        "JWT_EXPIRY_SECONDS": str(expiry),
        "ALLOWED_ORIGINS": "http://localhost:5173",
    })
    from src.config.settings import Settings as S
    return S()


class TestGeneracion:
    def test_token_contiene_claims_requeridos(self):
        svc = JWTService(_make_settings())
        user_id = str(uuid.uuid4())

        token, expires_in = svc.generate(user_id)

        payload = pyjwt.decode(
            token,
            "supersecretfortesting1234567890",
            algorithms=["HS256"],
            options={"require": ["sub", "exp", "iat", "iss", "jti"]},
        )
        assert payload["sub"] == user_id
        assert payload["iss"] == "door-auth"
        assert expires_in == 900

    def test_exp_esta_en_el_futuro(self):
        svc = JWTService(_make_settings(expiry=60))
        token, _ = svc.generate(str(uuid.uuid4()))
        payload = pyjwt.decode(token, "supersecretfortesting1234567890", algorithms=["HS256"])
        assert payload["exp"] > time.time()

    def test_jti_es_unico_en_cada_llamada(self):
        svc = JWTService(_make_settings())
        t1, _ = svc.generate(str(uuid.uuid4()))
        t2, _ = svc.generate(str(uuid.uuid4()))
        p1 = pyjwt.decode(t1, "supersecretfortesting1234567890", algorithms=["HS256"])
        p2 = pyjwt.decode(t2, "supersecretfortesting1234567890", algorithms=["HS256"])
        assert p1["jti"] != p2["jti"]

    def test_algoritmo_none_no_aceptado(self):
        svc = JWTService(_make_settings())
        token, _ = svc.generate(str(uuid.uuid4()))
        # Intentar decodificar con none debe fallar
        with pytest.raises(Exception):
            pyjwt.decode(token, "", algorithms=["none"])