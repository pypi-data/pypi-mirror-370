from typing import Annotated
from rb_commons.schemes.jwt import Claims
from fastapi import Request, Depends


async def get_claims(request: Request) -> Claims:
    return Claims.from_headers(dict(request.headers))

ClaimsDep = Annotated[Claims, Depends(get_claims)]