# lambda-auth/src/infrastructure/dynamodb_user_repo.py
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

import boto3
from boto3.dynamodb.conditions import Key

from ..domain.entities import User

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table

logger = logging.getLogger(__name__)


class DynamoDBUserRepository:
    """Implementación de UserRepository sobre DynamoDB."""

    def __init__(self, table_name: str, gsi_name: str, region: str) -> None:
        dynamodb = boto3.resource("dynamodb", region_name=region)
        self._table: "Table" = dynamodb.Table(table_name)
        self._gsi_name = gsi_name

    def find_by_username(self, username: str) -> Optional[User]:
        try:
            response = self._table.query(
                IndexName=self._gsi_name,
                KeyConditionExpression=Key("username").eq(username),
                Limit=1,
            )
        except Exception:
            logger.exception("dynamodb_query_error", extra={"gsi": self._gsi_name})
            raise

        items = response.get("Items", [])
        if not items:
            return None

        item = items[0]
        return User(
            user_id=item["user_id"],
            username=item["username"],
            password=item["password"],
            active=bool(item.get("active", False)),
        )


    def create(self, user: User) -> User:
        try:
            self._table.put_item(
                Item={
                    "user_id": user.user_id,
                    "username": user.username,
                    "password": user.password,
                    "active": user.active,
                },
                ConditionExpression="attribute_not_exists(user_id)",
            )
        except Exception:
            logger.exception("dynamodb_put_error", extra={"username": user.username})
            raise

        logger.info("user_created", extra={"user_id": user.user_id[:8] + "..."})
        return user
