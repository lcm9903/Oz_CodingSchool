from typing import TYPE_CHECKING

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin
from app.models.user import Gender, enum_column

if TYPE_CHECKING:
    from app.models.medical_record import MedicalRecord


class Patient(TimestampMixin, Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), index=True)
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[Gender] = mapped_column(enum_column(Gender, "patient_gender"))
    phone_number: Mapped[str] = mapped_column(String(20))

    # 환자 삭제 시 진료기록(→ 예측결과)까지 DB의 ON DELETE CASCADE로 함께 삭제된다.
    medical_records: Mapped[list["MedicalRecord"]] = relationship(
        back_populates="patient", passive_deletes=True
    )
