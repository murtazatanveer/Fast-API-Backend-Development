from fastapi import Request
from sqlalchemy import select

from Configuration.supabaseClient import getSessionFactory
from Models.userModel import User
from Schemas.authSchema import LoginRequest
from Utils.errors import ServiceError
from Utils.security import createAccessToken, verifyPassword
from Utils.tokenHelpers import buildRefreshTokenRow


async def login(payload: LoginRequest, request: Request) -> dict:
    username = payload.username.strip()

    session_factory = getSessionFactory()
    async with session_factory() as db:
        try:
            result = await db.execute(
                select(User).where(User.username == username)
            )
            user = result.scalar_one_or_none()

            if user is None or not verifyPassword(payload.password, user.password_hash):
                raise ServiceError(
                    401,
                    "Invalid username or password",
                    display_ui=True,
                )

            access_token, expires_in = createAccessToken(user.id)
            refresh_token, refresh_token_row = buildRefreshTokenRow(user.id, request)
            db.add(refresh_token_row)

            await db.commit()

            return {
                "user": user,
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": expires_in,
                "refresh_token": refresh_token,
            }
        except ServiceError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
