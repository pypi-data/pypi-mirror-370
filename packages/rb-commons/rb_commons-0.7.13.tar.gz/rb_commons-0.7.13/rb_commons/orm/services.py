from abc import ABCMeta
from typing import Any, Callable, Awaitable, Dict

from sqlalchemy.ext.asyncio import AsyncSession

from rb_commons.http.exceptions import ForbiddenException
from rb_commons.schemes.jwt import Claims


class FeignClientMeta(ABCMeta):
    def __new__(cls, name, bases, namespace):
        feign_clients = namespace.get('feign_clients', {})

        for client_name, init_func in feign_clients.items():
            method_name = f'get_{client_name}'

            async def getter(self, name=client_name, init_func=init_func):
                attr_name = f'_{name}'
                if getattr(self, attr_name, None) is None:
                    client = await init_func()
                    setattr(self, attr_name, client)
                return getattr(self, attr_name)

            namespace[method_name] = getter

        return super().__new__(cls, name, bases, namespace)


class BaseService(metaclass=FeignClientMeta):
    feign_clients: Dict[str, Callable[[], Awaitable[Any]]] = {}

    def __init__(self, claims: Claims, session: AsyncSession):
        self.claims = claims
        self.session = session

        for name in self.feign_clients:
            setattr(self, f'_{name}', None)

    def _verify_shop_permission(self, target: Any, raise_exception: bool = True) -> bool:
        if self.claims.shop_id != getattr(target, "shop_id", None):
            if raise_exception:
                raise ForbiddenException("You are not allowed to access this resource")
            return False
        return True
