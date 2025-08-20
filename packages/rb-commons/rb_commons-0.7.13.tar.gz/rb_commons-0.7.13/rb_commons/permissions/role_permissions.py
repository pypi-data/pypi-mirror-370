from typing import Annotated
from fastapi import Depends
from rb_commons.configs.injections import get_claims
from rb_commons.http.exceptions import ForbiddenException
from rb_commons.schemes.jwt import Claims, UserRole


class BasePermission:
    def __call__(self, claims: Claims = Depends(get_claims)):
        if not self.has_permission(claims):
            raise ForbiddenException(message=f"Access denied", status=401, code="0000")

        return claims

    def has_permission(self, claims: Claims) -> bool:
        return False


class IsAdmin(BasePermission):
    def has_permission(self, claims: Claims) -> bool:
        return claims.user_role == UserRole.ADMIN and claims.shop_id is not None


class IsCustomer(BasePermission):
    def has_permission(self, claims: Claims) -> bool:
        return claims.user_role == UserRole.CUSTOMER and claims.user_id is not None and claims.shop_id is not None \
        and claims.customer_id is not None


IsAdminDep = Annotated[Claims, Depends(IsAdmin())]
IsCustomerDep = Annotated[Claims, Depends(IsCustomer())]
