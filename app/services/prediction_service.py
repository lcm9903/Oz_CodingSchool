from fastapi import HTTPException, status
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction
from app.repositories.prediction_repository import PredictionRepository
from app.services.file_service import media_path
from app.services.medical_record_service import MedicalRecordService
from worker.model import ModelNotReadyError, PneumoniaPredictor


class PredictionService:
    def __init__(self, db: AsyncSession, predictor: PneumoniaPredictor):
        self.db = db
        self.repo = PredictionRepository(db)
        self.record_service = MedicalRecordService(db)
        self.predictor = predictor

    # ---------- REQ-PRED-001 AI 폐렴 예측 ----------
    async def predict(self, record_id: int) -> tuple[Prediction, bool]:
        """
        Returns:
            (예측 결과, 새로 추론했는지 여부)
        같은 진료기록 + 같은 모델의 결과가 이미 있으면 추론하지 않고 저장된 결과를 돌려준다.
        """
        record = await self.record_service.get_or_404(record_id)
        model_name = self.predictor.model_name

        saved = await self.repo.get_by_record_and_model(record.id, model_name)
        if saved:
            return saved, False

        image_file = media_path(record.xray_image_path)
        if not image_file.exists():
            raise HTTPException(
                status.HTTP_404_NOT_FOUND, "진료기록의 X-ray 이미지 파일을 찾을 수 없습니다."
            )

        try:
            # 모델 추론은 CPU를 오래 쓰는 동기 작업이므로 별도 스레드에서 실행해
            # 다른 요청 처리가 멈추지 않게 한다.
            is_pneumonia, confidence = await run_in_threadpool(
                self.predictor.predict, image_file
            )
        except ModelNotReadyError as exc:
            raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(exc)) from exc
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(
                status.HTTP_500_INTERNAL_SERVER_ERROR, f"AI 예측 중 오류가 발생했습니다: {exc}"
            ) from exc

        prediction = Prediction(
            medical_record_id=record.id,
            is_pneumonia=is_pneumonia,
            confidence=confidence,
            heatmap_image_url=None,  # 히트맵은 선택사항 (미구현)
            ai_model=model_name,
        )
        try:
            return await self.repo.save(prediction), True
        except IntegrityError:
            # 버튼을 연속으로 눌러 같은 결과가 동시에 저장되려 한 경우: 먼저 저장된 결과를 응답
            await self.db.rollback()
            saved = await self.repo.get_by_record_and_model(record.id, model_name)
            if saved is None:
                raise
            return saved, False

    # ---------- REQ-PRED-002 예측 결과 목록 조회 ----------
    async def list_by_record(self, record_id: int) -> list[Prediction]:
        await self.record_service.get_or_404(record_id)
        return await self.repo.list_by_record(record_id)
