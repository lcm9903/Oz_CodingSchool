from typing import Annotated

from fastapi import APIRouter, File, Form, Response, UploadFile, status

from app.core.dependencies import ApprovedUser, DBSession, MedicalUser
from app.schemas.medical_record import MedicalRecordResponse
from app.schemas.prediction import PredictionResponse
from app.services.medical_record_service import MedicalRecordService
from app.services.prediction_service import PredictionService
from worker.model import predictor

router = APIRouter(prefix="/medical-records", tags=["Medical Records"])


@router.post(
    "",
    response_model=MedicalRecordResponse,
    status_code=status.HTTP_201_CREATED,
    summary="진료기록 등록 [REQ-MDR-001] (의료진)",
)
async def create_medical_record(
    patient_id: Annotated[int, Form()],
    chart_number: Annotated[str, Form(max_length=50)],
    symptoms: Annotated[str, Form()],
    xray_image: Annotated[UploadFile, File(description="흉부 X-ray 이미지 (png, jpg)")],
    user: MedicalUser,
    db: DBSession,
):
    return await MedicalRecordService(db).create(
        patient_id, chart_number, symptoms, xray_image
    )


@router.get(
    "/{record_id}",
    response_model=MedicalRecordResponse,
    summary="진료기록 상세 조회 [REQ-MDR-003]",
)
async def get_medical_record(record_id: int, user: ApprovedUser, db: DBSession):
    return await MedicalRecordService(db).get_or_404(record_id)


@router.post(
    "/{record_id}/predict",
    response_model=PredictionResponse,
    summary="AI 폐렴 예측 [REQ-PRED-001]",
    responses={
        200: {"description": "같은 모델로 저장된 결과가 있어 추론 없이 반환"},
        201: {"description": "새로 추론하여 저장한 결과"},
        503: {"description": "AI 모델이 준비되지 않음"},
    },
)
async def predict_pneumonia(
    record_id: int, response: Response, user: ApprovedUser, db: DBSession
):
    prediction, created = await PredictionService(db, predictor).predict(record_id)
    response.status_code = status.HTTP_201_CREATED if created else status.HTTP_200_OK
    return prediction


@router.get(
    "/{record_id}/analyses",
    response_model=list[PredictionResponse],
    summary="AI 예측 결과 목록 조회 [REQ-PRED-002]",
)
async def list_predictions(record_id: int, user: ApprovedUser, db: DBSession):
    return await PredictionService(db, predictor).list_by_record(record_id)
