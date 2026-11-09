import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from passlib.context import CryptContext
from uuid6 import uuid7

from Configuration.config import settings

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hashPassword(password: str) -> str:
    return password_context.hash(password)


def verifyPassword(password: str, password_hash: str) -> bool:
    return password_context.verify(password, password_hash)


def generateOtp() -> str:
    return f"{secrets.randbelow(1_000_000):06d}"


def hashOtp(otp: str) -> str:
    return password_context.hash(otp)


def verifyOtp(otp: str, otp_hash: str) -> bool:
    return password_context.verify(otp, otp_hash)


def createAccessToken(user_id: UUID) -> tuple[str, int]:
    now = datetime.now(timezone.utc)
    lifetime = timedelta(minutes=settings.access_token_expire_minutes)
    payload = {
        "sub": str(user_id),
        "jti": str(uuid7()),
        "type": "access",
        "iat": now,
        "exp": now + lifetime,
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
    }
    access_token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
    return access_token, int(lifetime.total_seconds())


def decodeAccessToken(token: str) -> dict:
    return jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        audience=settings.jwt_audience,
        issuer=settings.jwt_issuer,
    )


def generateRefreshToken() -> str:
    return secrets.token_urlsafe(48)


def hashRefreshToken(refresh_token: str) -> str:
    return hashlib.sha256(refresh_token.encode("utf-8")).hexdigest()


def getRefreshCookieSettings() -> dict:
    return {
        "key": settings.refresh_cookie_name,
        "httponly": True,
        "secure": settings.refresh_cookie_secure,
        "samesite": settings.refresh_cookie_samesite,
        "path": None,
        "max_age": settings.refresh_absolute_days * 24 * 60 * 60,
    }


def getClearRefreshCookieSettings() -> dict:
    return {
        "key": settings.refresh_cookie_name,
        "httponly": True,
        "secure": settings.refresh_cookie_secure,
        "samesite": settings.refresh_cookie_samesite,
        "path": None,
    }
