from pydantic import BaseModel, ConfigDict

from app.schemas.common import UTCDateTime


class MedicalRecordResponse(BaseModel):
    """
    진료기록 응답.
    등록 요청은 이미지 업로드가 있어 JSON이 아닌 multipart/form-data(Form, File)로 받는다.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    chart_number: str
    symptoms: str
    xray_image_url: str  # 모델의 @property 값
    created_at: UTCDateTime
