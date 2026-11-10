from datetime import datetime, timezone

from fastapi import Request
from sqlalchemy import delete, select

from Configuration.config import settings
from Configuration.supabaseClient import getSessionFactory
from Models.otpModel import Otp
from Models.userModel import User
from Schemas.authSchema import VerifyLoginRequest
from Utils.errors import ServiceError
from Utils.security import createAccessToken, verifyOtp
from Utils.tokenHelpers import buildRefreshTokenRow

INVALID_OTP_MESSAGE = "OTP not Valid"


async def verifyLogin(payload: VerifyLoginRequest, request: Request) -> dict:
    username = payload.username.strip()

    session_factory = getSessionFactory()
    async with session_factory() as db:
        try:
            user_result = await db.execute(
                select(User).where(User.username == username)
            )
            user = user_result.scalar_one_or_none()
            if user is None:
                raise ServiceError(401, INVALID_OTP_MESSAGE, display_ui=True)

            otp_result = await db.execute(
                select(Otp)
                .where(Otp.user_id == user.id)
                .with_for_update()
            )
            otp_row = otp_result.scalar_one_or_none()
            if otp_row is None:
                raise ServiceError(401, INVALID_OTP_MESSAGE, display_ui=True)

            now = datetime.now(timezone.utc)
            if otp_row.expires_at <= now:
                await db.execute(delete(Otp).where(Otp.id == otp_row.id))
                await db.commit()
                raise ServiceError(401, INVALID_OTP_MESSAGE, display_ui=True)

            if otp_row.attempts >= settings.otp_max_attempts:
                await db.execute(delete(Otp).where(Otp.id == otp_row.id))
                await db.commit()
                raise ServiceError(401, INVALID_OTP_MESSAGE, display_ui=True)

            if not verifyOtp(payload.otp, otp_row.otp_hash):
                otp_row.attempts += 1
                if otp_row.attempts >= settings.otp_max_attempts:
                    await db.execute(delete(Otp).where(Otp.id == otp_row.id))
                await db.commit()
                raise ServiceError(401, INVALID_OTP_MESSAGE, display_ui=True)

            await db.execute(delete(Otp).where(Otp.id == otp_row.id))

            access_token, _ = createAccessToken(user.id)
            refresh_token, refresh_token_row = buildRefreshTokenRow(
                user.id, request
            )
            db.add(refresh_token_row)

            await db.commit()

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        except ServiceError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
