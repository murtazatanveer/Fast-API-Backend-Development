from typing import Annotated
from uuid import UUID

import jwt
from fastapi import Header, HTTPException

from Schemas.authSchema import AccessTokenPayload
from Utils.security import decodeAccessToken


def unauthorizedException() -> HTTPException:
    return HTTPException(
        status_code=401,
        detail="Unauthorized",
        headers={"WWW-Authenticate": "Bearer"},
    )


def verifyAccessToken(
    authToken: Annotated[str, Header(..., description="Provide JWT access token")],
) -> AccessTokenPayload:
    if not authToken.startswith("Bearer_"):
        raise unauthorizedException()

    token = authToken.split("Bearer_", 1)[1].strip()
    if not token:
        raise unauthorizedException()

    try:
        payload = decodeAccessToken(token)

        if payload.get("type") != "access":
            raise unauthorizedException()

        return AccessTokenPayload(
            user_id=UUID(payload["sub"]),
            jti=payload["jti"],
            exp=payload["exp"],
            iat=payload.get("iat"),
        )
    except HTTPException:
        raise
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise unauthorizedException()
