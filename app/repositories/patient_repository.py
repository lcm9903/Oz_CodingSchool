from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.patient import Patient
from app.schemas.patient import PatientSearchParams


class PatientRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, patient_id: int) -> Patient | None:
        return await self.db.get(Patient, patient_id)

    async def list(self, params: PatientSearchParams) -> list[Patient]:
        stmt = select(Patient).order_by(Patient.id.desc())
        if params.name:
            stmt = stmt.where(Patient.name.like(f"%{params.name}%"))
        if params.gender:
            stmt = stmt.where(Patient.gender == params.gender)
        if params.min_age is not None:
            stmt = stmt.where(Patient.age >= params.min_age)
        if params.max_age is not None:
            stmt = stmt.where(Patient.age <= params.max_age)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save(self, patient: Patient) -> Patient:
        self.db.add(patient)
        await self.db.commit()
        await self.db.refresh(patient)
        return patient

    async def delete(self, patient: Patient) -> None:
        # 진료기록/예측결과는 FK의 ON DELETE CASCADE로 DB에서 함께 삭제된다.
        await self.db.delete(patient)
        await self.db.commit()
