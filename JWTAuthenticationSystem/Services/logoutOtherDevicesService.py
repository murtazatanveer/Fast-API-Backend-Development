from fastapi import Request
from sqlalchemy import delete, distinct, func, select

from Configuration.config import settings
from Configuration.supabaseClient import getSessionFactory
from Models.refreshTokenModel import RefreshToken
from Schemas.authSchema import AccessTokenPayload
from Utils.errors import ServiceError
from Utils.security import hashRefreshToken


async def logoutOtherDevices(
    request: Request, current_user: AccessTokenPayload
) -> int:
    raw_refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not raw_refresh_token or not raw_refresh_token.strip():
        raise ServiceError(401, "Unauthorized", display_ui=True)

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

            if (
                refresh_token_row is None
                or refresh_token_row.user_id != current_user.user_id
            ):
                raise ServiceError(401, "Unauthorized", display_ui=True)

            other_devices = (
                await db.execute(
                    select(func.count(distinct(RefreshToken.family_id))).where(
                        RefreshToken.user_id == current_user.user_id,
                        RefreshToken.family_id != refresh_token_row.family_id,
                        RefreshToken.revoked.is_(False),
                    )
                )
            ).scalar_one() or 0

            await db.execute(
                delete(RefreshToken).where(
                    RefreshToken.user_id == current_user.user_id,
                    RefreshToken.family_id != refresh_token_row.family_id,
                )
            )

            await db.commit()

            return other_devices
        except ServiceError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
