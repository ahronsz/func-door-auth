# lambda-auth/src/presentation/response.py
from __future__ import annotations

import json
import uuid
from typing import Any, Optional


def _make_body(
    data: Optional[Any],
    error: Optional[dict[str, Any]],
    request_id: str,
) -> str:
    return json.dumps(
        {"data": data, "error": error, "requestId": request_id},
        default=str,
    )


def success(data: Any, status_code: int = 200, request_id: Optional[str] = None) -> dict[str, Any]:
    rid = request_id or str(uuid.uuid4())
    return {
        "statusCode": status_code,
        "body": _make_body(data, None, rid),
        "headers": {"Content-Type": "application/json"},
    }


def error(
    code: str,
    message: str,
    status_code: int,
    details: Optional[list[Any]] = None,
    request_id: Optional[str] = None,
) -> dict[str, Any]:
    rid = request_id or str(uuid.uuid4())
    return {
        "statusCode": status_code,
        "body": _make_body(
            None,
            {"code": code, "message": message, "details": details or []},
            rid,
        ),
        "headers": {"Content-Type": "application/json"},
    }