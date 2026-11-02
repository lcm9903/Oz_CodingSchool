from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medical_record import MedicalRecord
from app.repositories.medical_record_repository import MedicalRecordRepository
from app.services.file_service import delete_media_file, save_xray_image
from app.services.patient_service import PatientService


class MedicalRecordService:
    def __init__(self, db: AsyncSession):
        self.repo = MedicalRecordRepository(db)
        self.patient_service = PatientService(db)

    async def get_or_404(self, record_id: int) -> MedicalRecord:
        record = await self.repo.get_by_id(record_id)
        if record is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "존재하지 않는 진료기록입니다.")
        return record

    async def create(
        self, patient_id: int, chart_number: str, symptoms: str, xray_image: UploadFile
    ) -> MedicalRecord:
        await self.patient_service.get_or_404(patient_id)

        chart_number, symptoms = chart_number.strip(), symptoms.strip()
        if not chart_number or not symptoms:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "차트 번호와 증상을 입력해주세요."
            )

        image_path = await save_xray_image(xray_image)
        record = MedicalRecord(
            patient_id=patient_id,
            chart_number=chart_number,
            symptoms=symptoms,
            xray_image_path=image_path,
        )
        try:
            return await self.repo.save(record)
        except Exception:
            delete_media_file(image_path)  # DB 저장 실패 시 저장해둔 파일 정리
            raise

    async def list_by_patient(self, patient_id: int) -> list[MedicalRecord]:
        await self.patient_service.get_or_404(patient_id)
        return await self.repo.list_by_patient(patient_id)
