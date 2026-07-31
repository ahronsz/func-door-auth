# lambda-auth/src/presentation/router.py
from __future__ import annotations

import json
import logging
import uuid
from typing import Any

import jwt as pyjwt
from pydantic import ValidationError

from ..application.login_use_case import LoginUseCase
from ..application.register_use_case import RegisterUseCase
from ..config.settings import Settings
from ..domain.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserInactiveError,
    UserNotFoundError,
)
from .response import error, success
from .schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)

logger = logging.getLogger(__name__)


def _request_id(event: dict[str, Any]) -> str:
    return event.get("requestContext", {}).get("requestId") or str(uuid.uuid4())


def _cors_headers(origin: str, allowed_origins: list[str]) -> dict[str, str]:
    if origin in allowed_origins:
        return {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "86400",
        }
    return {}


def _get_method(event: dict[str, Any]) -> str:
    return (event.get("requestContext", {}).get("http", {}).get("method") or "").upper()


def _get_path(event: dict[str, Any]) -> str:
    return event.get("requestContext", {}).get("http", {}).get("path") or event.get("path", "")


class Router:
    def __init__(
        self,
        settings: Settings,
        login_use_case: LoginUseCase,
        register_use_case: RegisterUseCase,
    ) -> None:
        self._settings = settings
        self._login = login_use_case
        self._register = register_use_case

    def handle(self, event: dict[str, Any]) -> dict[str, Any]:
        rid = _request_id(event)
        origin = (event.get("headers") or {}).get("origin", "")
        cors = _cors_headers(origin, self._settings.allowed_origins)
        method = _get_method(event)
        path = _get_path(event).rstrip("/")

        # OPTIONS preflight
        if method == "OPTIONS":
            return {
                "statusCode": 204,
                "body": "",
                "headers": {**cors, "Content-Type": "application/json"},
            }

        # Rutas públicas
        if method == "POST" and path == "/auth/login":
            resp = self._handle_login(event, rid)
        elif method == "POST" and path == "/auth/register":
            resp = self._handle_register(event, rid)
        else:
            resp = error("NOT_FOUND", "Ruta no encontrada", 404, request_id=rid)

        resp["headers"] = {**resp.get("headers", {}), **cors}
        return resp

    # ── Handlers ────────────────────────────────────────────────────────────

    def _handle_login(self, event: dict[str, Any], rid: str) -> dict[str, Any]:
        try:
            body = json.loads(event.get("body") or "{}")
            req = LoginRequest.model_validate(body)
        except (json.JSONDecodeError, ValidationError):
            return error("VALIDATION_ERROR", "Solicitud inválida", 400, request_id=rid)

        try:
            result = self._login.execute(req.username, req.password)
        except (InvalidCredentialsError, UserNotFoundError, UserInactiveError):
            return error("INVALID_CREDENTIALS", "Credenciales inválidas", 401, request_id=rid)
        except Exception:
            logger.exception("login_error", extra={"rid": rid})
            return error("INTERNAL_ERROR", "Error interno", 500, request_id=rid)

        data = LoginResponse(
            accessToken=result.access_token,
            tokenType=result.token_type,
            expiresIn=result.expires_in,
        ).model_dump(by_alias=True)
        return success(data, 200, rid)

    def _handle_register(self, event: dict[str, Any], rid: str) -> dict[str, Any]:
        try:
            body = json.loads(event.get("body") or "{}")
            req = RegisterRequest.model_validate(body)
        except (json.JSONDecodeError, ValidationError) as exc:
            details = []
            if hasattr(exc, "errors"):
                details = [f"{e['loc']}: {e['msg']}" for e in exc.errors()]
            return error("VALIDATION_ERROR", "Solicitud inválida", 400, details=details, request_id=rid)

        try:
            result = self._register.execute(req.username, req.password)
        except UserAlreadyExistsError:
            # Respuesta genérica para no revelar si el usuario existe
            return error("CONFLICT", "No se pudo completar el registro", 409, request_id=rid)
        except Exception:
            logger.exception("register_error", extra={"rid": rid})
            return error("INTERNAL_ERROR", "Error interno", 500, request_id=rid)

        data = RegisterResponse(
            user_id=result.user_id,
            username=result.username,
        ).model_dump(by_alias=True)
        return success(data, 201, rid)
