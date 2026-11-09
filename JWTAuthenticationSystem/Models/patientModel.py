from uuid import UUID

from sqlalchemy import CheckConstraint, Float, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column

from Configuration.supabaseClient import Base


class Patient(Base):
    __tablename__ = "Patients"
    __table_args__ = (
        CheckConstraint("id ~ '^P[0-9]{3}$'", name="ck_patients_id_format"),
        CheckConstraint("age > 0 AND age < 81", name="ck_patients_age_range"),
        CheckConstraint(
            "gender IN ('male', 'female', 'other')", name="ck_patients_gender"
        ),
        CheckConstraint("height > 0", name="ck_patients_height_positive"),
        CheckConstraint("weight > 0", name="ck_patients_weight_positive"),
        Index("ix_Patients_createdBy_id", "createdBy", "id"),
    )

    id: Mapped[str] = mapped_column(String(4), primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(6), nullable=False)
    height: Mapped[float] = mapped_column(Float, nullable=False)
    weight: Mapped[float] = mapped_column(Float, nullable=False)
    bmi: Mapped[float] = mapped_column(Float, nullable=False)
    verdict: Mapped[str] = mapped_column(String(20), nullable=False)
    created_by: Mapped[UUID] = mapped_column(
        "createdBy",
        PgUUID(as_uuid=True),
        ForeignKey("Users.id", ondelete="CASCADE"),
        nullable=False,
    )
