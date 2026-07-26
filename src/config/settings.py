# lambda-auth/src/config/settings.py
from __future__ import annotations

import os
from functools import lru_cache


class Settings:
    """Lee configuración exclusivamente desde variables de entorno."""

    # DynamoDB
    users_table: str
    users_gsi_username: str
    aws_region: str

    # JWT — el secreto NUNCA se loguea
    jwt_secret: str  # noqa: S105 (es un nombre de variable, no un literal)
    jwt_algorithm: str
    jwt_issuer: str
    jwt_expiry_seconds: int

    # CORS
    allowed_origins: list[str]

    def __init__(self) -> None:
        self.users_table = self._require("USERS_TABLE")
        self.users_gsi_username = os.environ.get(
            "USERS_GSI_USERNAME", "username-index"
        )
        self.aws_region = os.environ.get("AWS_REGION", "us-west-2")
        self.jwt_secret = self._require("JWT_SECRET")
        self.jwt_algorithm = os.environ.get("JWT_ALGORITHM", "HS256")
        self.jwt_issuer = os.environ.get("JWT_ISSUER", "door-auth")
        self.jwt_expiry_seconds = int(
            os.environ.get("JWT_EXPIRY_SECONDS", "900")
        )
        raw_origins = os.environ.get(
            "ALLOWED_ORIGINS", "http://localhost:5173"
        )
        self.allowed_origins = [o.strip() for o in raw_origins.split(",")]

    @staticmethod
    def _require(name: str) -> str:
        value = os.environ.get(name)
        if not value:
            raise RuntimeError(f"Variable de entorno requerida no definida: {name}")
        return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
