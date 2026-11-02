from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db.databases import Base

if TYPE_CHECKING:
    from app.models.medical_record import MedicalRecord


class Prediction(Base):
    """AI 폐렴 예측 결과 (REQ-PRED-001, REQ-PRED-002)"""

    __tablename__ = "predictions"
    # 같은 진료기록 + 같은 모델의 결과는 하나만 저장한다.
    # → 이미 결과가 있으면 추론을 다시 하지 않고 저장된 결과를 응답 (REQ-PRED-001)
    __table_args__ = (
        UniqueConstraint("medical_record_id", "ai_model", name="uq_record_model"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    medical_record_id: Mapped[int] = mapped_column(
        ForeignKey("medical_records.id", ondelete="CASCADE"), index=True
    )
    is_pneumonia: Mapped[bool] = mapped_column(Boolean)
    confidence: Mapped[float] = mapped_column(Float)  # 0~100 (%)
    heatmap_image_url: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ai_model: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    medical_record: Mapped["MedicalRecord"] = relationship(back_populates="predictions")
