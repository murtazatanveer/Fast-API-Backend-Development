from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from uuid6 import uuid7

from Configuration.supabaseClient import getSessionFactory
from Models.userModel import User
from Schemas.authSchema import SignupRequest
from Utils.errors import ServiceError
from Utils.security import hashPassword


async def signup(payload: SignupRequest) -> None:
    email = payload.email.strip().lower()
    username = payload.username.strip()

    session_factory = getSessionFactory()
    async with session_factory() as db:
        try:
            existing_user = await db.execute(
                select(User).where(
                    (User.email == email) | (User.username == username)
                )
            )
            if existing_user.scalar_one_or_none() is not None:
                raise ServiceError(
                    409,
                    "An account with this email or username already exists",
                    display_ui=True,
                )

            password_hash = hashPassword(payload.password)
            user = User(
                id=uuid7(),
                email=email,
                username=username,
                password_hash=password_hash,
            )
            db.add(user)

            await db.commit()
        except ServiceError:
            await db.rollback()
            raise
        except IntegrityError:
            await db.rollback()
            raise ServiceError(
                409,
                "An account with this email or username already exists",
                display_ui=True,
            )
        except Exception:
            await db.rollback()
            raise
