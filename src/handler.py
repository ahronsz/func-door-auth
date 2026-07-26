# lambda-auth/src/handler.py
from __future__ import annotations

import logging
from typing import Any

from .application.login_use_case import LoginUseCase
from .application.register_use_case import RegisterUseCase
from .config.settings import get_settings
from .infrastructure.dynamodb_user_repo import DynamoDBUserRepository
from .infrastructure.jwt_service import JWTService
from .infrastructure.password_service import Argon2PasswordHasher, Argon2PasswordVerifier
from .presentation.router import Router

logging.basicConfig(
    level=logging.INFO,
    format='{"time":"%(asctime)s","level":"%(levelname)s","name":"%(name)s","message":"%(message)s"}',
)

_settings = get_settings()
_user_repo = DynamoDBUserRepository(
    table_name=_settings.users_table,
    gsi_name=_settings.users_gsi_username,
    region=_settings.aws_region,
)
_router = Router(
    settings=_settings,
    login_use_case=LoginUseCase(_user_repo, Argon2PasswordVerifier(), JWTService(_settings)),
    register_use_case=RegisterUseCase(_user_repo, Argon2PasswordHasher()),
)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:  # noqa: ANN401
    return _router.handle(event)
