from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.medical_record import MedicalRecord


class MedicalRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, record_id: int) -> MedicalRecord | None:
        return await self.db.get(MedicalRecord, record_id)

    async def list_by_patient(self, patient_id: int) -> list[MedicalRecord]:
        stmt = (
            select(MedicalRecord)
            .where(MedicalRecord.patient_id == patient_id)
            .order_by(MedicalRecord.id.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def list_image_paths_by_patient(self, patient_id: int) -> list[str]:
        stmt = select(MedicalRecord.xray_image_path).where(
            MedicalRecord.patient_id == patient_id
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save(self, record: MedicalRecord) -> MedicalRecord:
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)
        return record
