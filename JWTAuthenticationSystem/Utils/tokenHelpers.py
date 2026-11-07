from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import Request
from uuid6 import uuid7

from Configuration.config import settings
from Models.refreshTokenModel import RefreshToken
from Utils.security import generateRefreshToken, hashRefreshToken


def buildRefreshTokenRow(
    user_id: UUID,
    request: Request,
    family_id: UUID | None = None,
    absolute_expiry: datetime | None = None,
) -> tuple[str, RefreshToken]:
    now = datetime.now(timezone.utc)
    refresh_token = generateRefreshToken()
    refresh_token_row = RefreshToken(
        id=uuid7(),
        user_id=user_id,
        token_hash=hashRefreshToken(refresh_token),
        family_id=family_id if family_id is not None else uuid7(),
        sliding_expiry=now + timedelta(days=settings.refresh_sliding_days),
        absolute_expiry=(
            absolute_expiry
            if absolute_expiry is not None
            else now + timedelta(days=settings.refresh_absolute_days)
        ),
        revoked=False,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    return refresh_token, refresh_token_row
