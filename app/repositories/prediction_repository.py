from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction


class PredictionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_record_and_model(
        self, record_id: int, ai_model: str
    ) -> Prediction | None:
        stmt = select(Prediction).where(
            Prediction.medical_record_id == record_id,
            Prediction.ai_model == ai_model,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_record(self, record_id: int) -> list[Prediction]:
        stmt = (
            select(Prediction)
            .where(Prediction.medical_record_id == record_id)
            .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save(self, prediction: Prediction) -> Prediction:
        self.db.add(prediction)
        await self.db.commit()
        await self.db.refresh(prediction)
        return prediction
