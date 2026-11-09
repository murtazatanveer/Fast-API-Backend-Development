import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from uuid6 import uuid7

from Configuration.config import settings
from Configuration.supabaseClient import getSessionFactory
from Models.otpModel import Otp
from Models.userModel import User
from Schemas.authSchema import LoginRequest
from Utils.emailHelpers import maskEmail, sendOtpEmail
from Utils.errors import ServiceError
from Utils.security import generateOtp, hashOtp, verifyPassword

logger = logging.getLogger(__name__)


async def login(payload: LoginRequest) -> dict:
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

            otp = generateOtp()
            otp_hash = hashOtp(otp)
            expires_at = datetime.now(timezone.utc) + timedelta(
                minutes=settings.otp_expire_minutes
            )

            await db.execute(
                insert(Otp)
                .values(
                    id=uuid7(),
                    user_id=user.id,
                    otp_hash=otp_hash,
                    expires_at=expires_at,
                    attempts=0,
                )
                .on_conflict_do_update(
                    index_elements=[Otp.user_id],
                    set_={
                        "otpHash": otp_hash,
                        "expiresAt": expires_at,
                        "attempts": 0,
                    },
                )
            )
            await db.commit()

            try:
                await sendOtpEmail(user.email, otp)
            except Exception:
                logger.exception("Failed to send OTP email")
                try:
                    await db.execute(delete(Otp).where(Otp.user_id == user.id))
                    await db.commit()
                except Exception:
                    logger.exception("Failed to clean up OTP row")
                    await db.rollback()
                raise ServiceError(
                    500,
                    "Server is not responding. Please try again later",
                    display_ui=True,
                )

            return {"email": maskEmail(user.email)}
        except ServiceError:
            await db.rollback()
            raise
        except Exception:
            await db.rollback()
            raise
