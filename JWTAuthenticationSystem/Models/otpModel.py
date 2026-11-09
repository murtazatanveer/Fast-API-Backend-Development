from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func, text
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7

from Configuration.supabaseClient import Base


class Otp(Base):
    __tablename__ = "Otps"
    __table_args__ = (
        CheckConstraint("attempts >= 0", name="ck_Otps_attempts_nonnegative"),
    )

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid7
    )
    user_id: Mapped[UUID] = mapped_column(
        "userId",
        PgUUID(as_uuid=True),
        ForeignKey("Users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )
    otp_hash: Mapped[str] = mapped_column(
        "otpHash", String(255), nullable=False
    )
    expires_at: Mapped[datetime] = mapped_column(
        "expiresAt", DateTime(timezone=True), nullable=False
    )
    attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default=text("0"), default=0
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
