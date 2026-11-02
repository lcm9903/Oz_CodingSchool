from pydantic import BaseModel, ConfigDict

from app.schemas.common import UTCDateTime


class PredictionResponse(BaseModel):
    """REQ-PRED-001 / REQ-PRED-002 예측 결과"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    medical_record_id: int
    is_pneumonia: bool
    confidence: float  # 0~100 (%)
    heatmap_image_url: str | None
    ai_model: str
    created_at: UTCDateTime
