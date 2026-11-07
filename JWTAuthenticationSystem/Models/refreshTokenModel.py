from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from uuid6 import uuid7

from Configuration.supabaseClient import Base

if TYPE_CHECKING:
    from Models.userModel import User


class RefreshToken(Base):
    __tablename__ = "RefreshTokens"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), primary_key=True, default=uuid7
    )
    user_id: Mapped[UUID] = mapped_column(
        "userId",
        PgUUID(as_uuid=True),
        ForeignKey("Users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(
        "tokenHash", String(64), unique=True, index=True, nullable=False
    )
    family_id: Mapped[UUID] = mapped_column(
        "familyId", PgUUID(as_uuid=True), index=True, nullable=False
    )
    sliding_expiry: Mapped[datetime] = mapped_column(
        "slidingExpiry", DateTime(timezone=True), nullable=False
    )
    absolute_expiry: Mapped[datetime] = mapped_column(
        "absoluteExpiry", DateTime(timezone=True), nullable=False
    )
    revoked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    revoked_at: Mapped[datetime | None] = mapped_column(
        "revokedAt", DateTime(timezone=True), nullable=True
    )
    replaced_by_token_id: Mapped[UUID | None] = mapped_column(
        "replacedByTokenId", PgUUID(as_uuid=True), nullable=True
    )
    user_agent: Mapped[str | None] = mapped_column(
        "userAgent", String(255), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(
        "ipAddress", String(45), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        "createdAt",
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="refresh_tokens")
