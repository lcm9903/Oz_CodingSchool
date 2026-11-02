from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.repositories.medical_record_repository import MedicalRecordRepository
from app.repositories.patient_repository import PatientRepository
from app.schemas.patient import (
    PatientCreateRequest,
    PatientSearchParams,
    PatientUpdateRequest,
)
from app.services.file_service import delete_media_file


class PatientService:
    def __init__(self, db: AsyncSession):
        self.repo = PatientRepository(db)
        self.record_repo = MedicalRecordRepository(db)

    async def get_or_404(self, patient_id: int) -> Patient:
        patient = await self.repo.get_by_id(patient_id)
        if patient is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "존재하지 않는 환자입니다.")
        return patient

    async def create(self, data: PatientCreateRequest) -> Patient:
        return await self.repo.save(Patient(**data.model_dump()))

    async def list(self, params: PatientSearchParams) -> list[Patient]:
        if (
            params.min_age is not None
            and params.max_age is not None
            and params.min_age > params.max_age
        ):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "최소 나이가 최대 나이보다 클 수 없습니다."
            )
        return await self.repo.list(params)

    async def update(self, patient_id: int, data: PatientUpdateRequest) -> Patient:
        patient = await self.get_or_404(patient_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(patient, field, value)
        return await self.repo.save(patient)

    async def delete(self, patient_id: int) -> None:
        """환자와 관련 데이터(진료기록, 예측결과, 업로드 이미지)를 모두 삭제한다."""
        patient = await self.get_or_404(patient_id)
        image_paths = await self.record_repo.list_image_paths_by_patient(patient_id)
        await self.repo.delete(patient)
        for path in image_paths:
            delete_media_file(path)
