from fastapi import Request
from sqlalchemy import delete, select

from Configuration.config import settings
from Configuration.supabaseClient import getSessionFactory
from Models.refreshTokenModel import RefreshToken
from Schemas.authSchema import AccessTokenPayload
from Utils.security import hashRefreshToken


async def logout(request: Request, current_user: AccessTokenPayload) -> None:
    raw_refresh_token = request.cookies.get(settings.refresh_cookie_name)
    if not raw_refresh_token or not raw_refresh_token.strip():
        return

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
                return

            if refresh_token_row.user_id != current_user.user_id:
                return

            await db.execute(
                delete(RefreshToken).where(
                    RefreshToken.family_id == refresh_token_row.family_id
                )
            )
            await db.commit()
        except Exception:
            await db.rollback()
            raise
