import uuid
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict


class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    GUEST = "guest"

class Claims(BaseModel):
    model_config = ConfigDict(extra="ignore")

    user_id: Optional[int] = Field(None, alias="x-user-id")
    customer_id: Optional[int] = Field(None, alias="x-customer-id")
    user_role: UserRole = Field(UserRole.GUEST, alias="x-user-role")
    shop_id: Optional[uuid.UUID] = Field(None, alias="x-shop-id")
    jwt_token: Optional[str] = Field(None, alias="x-jwt-token")

    @classmethod
    def from_headers(cls, headers: dict) -> 'Claims':
        raw_claims = {
            "x-user-id": headers.get("x-user-id"),
            "x-customer-id": headers.get("x-customer-id"),
            "x-user-role": headers.get("x-user-role", "admin"),
            "x-shop-id": headers.get("x-shop-id"),
            "x-jwt-token": headers.get("x-jwt-token")
        }

        try:
            if raw_claims["x-user-id"]:
                try:
                    raw_claims["x-user-id"] = int(raw_claims["x-user-id"])
                except ValueError as e:
                    raise ValueError(f"Invalid user_id format: {e}")

            if raw_claims["x-customer-id"] and raw_claims["x-customer-id"] != 'null':
                try:
                    raw_claims["x-customer-id"] = int(raw_claims["x-customer-id"])
                except ValueError as e:
                    raise ValueError(f"Invalid customer_id format: {e}")

            if raw_claims["x-shop-id"]:
                try:
                    raw_claims["x-shop-id"] = uuid.UUID(raw_claims["x-shop-id"])
                except ValueError as e:
                    raise ValueError(f"Invalid shop_id format: {e}")

            if raw_claims["x-user-role"]:
                try:
                    UserRole(raw_claims["x-user-role"].lower())
                except ValueError as e:
                    raise ValueError(f"Invalid user_role: {e}")

            if raw_claims["x-jwt-token"]:
                try:
                    raw_claims["x-jwt-token"] = str(raw_claims["x-jwt-token"])
                except ValueError as e:
                    raise ValueError(f"Invalid jwt token format: {e}")

            return cls(**raw_claims)

        except Exception as e:
            raise ValueError(f"Failed to parse claims: {str(e)}")
