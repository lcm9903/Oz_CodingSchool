from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin

if TYPE_CHECKING:
    from app.models.patient import Patient
    from app.models.prediction import Prediction


class MedicalRecord(TimestampMixin, Base):
    __tablename__ = "medical_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id", ondelete="CASCADE"), index=True
    )
    chart_number: Mapped[str] = mapped_column(String(50))
    symptoms: Mapped[str] = mapped_column(Text)
    # media 폴더 기준 상대경로 (예: xray/0190f3....png). URL은 /media/<경로> 로 제공한다.
    xray_image_path: Mapped[str] = mapped_column(String(255))

    patient: Mapped["Patient"] = relationship(back_populates="medical_records")
    predictions: Mapped[list["Prediction"]] = relationship(
        back_populates="medical_record", passive_deletes=True
    )

    @property
    def xray_image_url(self) -> str:
        return f"/media/{self.xray_image_path}"
