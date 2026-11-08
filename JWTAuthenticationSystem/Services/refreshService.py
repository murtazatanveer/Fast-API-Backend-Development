from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import delete, select, update

from Configuration.config import settings
from Configuration.supabaseClient import getSessionFactory
from Models.refreshTokenModel import RefreshToken
from Utils.errors import ServiceError
from Utils.security import createAccessToken, hashRefreshToken
from Utils.tokenHelpers import buildRefreshTokenRow

SESSION_EXPIRED_MESSAGE = "Session expired. Please log in again."


async def refresh(request: Request) -> dict:
    raw_refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not raw_refresh_token or not raw_refresh_token.strip():
        raise ServiceError(401, SESSION_EXPIRED_MESSAGE, display_ui=True)

    token_hash = hashRefreshToken(raw_refresh_token)

    session_factory = getSessionFactory()
    async with session_factory() as db:
        try:
            result = await db.execute(
                select(RefreshToken)
                .where(RefreshToken.token_hash == token_hash)
                .with_for_update()
            )
            refresh_token_row = result.scalar_one_or_none()

            if refresh_token_row is None:
                raise ServiceError(401, SESSION_EXPIRED_MESSAGE, display_ui=True)

            now = datetime.now(timezone.utc)

            if refresh_token_row.revoked:
                await db.execute(
                    update(RefreshToken)
                    .where(
                        RefreshToken.family_id == refresh_token_row.family_id,
                        RefreshToken.revoked.is_(False),
                    )
                    .values(revoked=True)
                )
                await db.commit()
                raise ServiceError(401, SESSION_EXPIRED_MESSAGE, display_ui=True)

            if refresh_token_row.absolute_expiry <= now:
                await db.execute(
                    delete(RefreshToken).where(
                        RefreshToken.family_id == refresh_token_row.family_id
                    )
                )
                await db.commit()
                raise ServiceError(401, SESSION_EXPIRED_MESSAGE, display_ui=True)

            if refresh_token_row.sliding_expiry <= now:
                await db.execute(
                    delete(RefreshToken).where(
                        RefreshToken.family_id == refresh_token_row.family_id
                    )
                )
                await db.commit()
                raise ServiceError(401, SESSION_EXPIRED_MESSAGE, display_ui=True)

            refresh_token_row.revoked = True
            new_refresh_token, new_refresh_token_row = buildRefreshTokenRow(
                refresh_token_row.user_id,
                request,
                family_id=refresh_token_row.family_id,
                absolute_expiry=refresh_token_row.absolute_expiry,
            )
            db.add(new_refresh_token_row)
            await db.commit()

            access_token, _ = createAccessToken(refresh_token_row.user_id)

            return {
                "access_token": access_token,
                "refresh_token": new_refresh_token,
            }
        except ServiceError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
