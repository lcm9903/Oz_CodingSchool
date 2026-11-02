from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import Department, User


class UserRepository:
    """users 테이블에 대한 DB 접근(조회/저장/삭제)만 담당한다."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.db.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def list(
        self, query: str | None = None, department: Department | None = None
    ) -> list[User]:
        stmt = select(User).order_by(User.id)
        if query:
            keyword = f"%{query}%"
            stmt = stmt.where(or_(User.name.like(keyword), User.email.like(keyword)))
        if department:
            stmt = stmt.where(User.department == department)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def save(self, user: User) -> User:
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def delete(self, user: User) -> None:
        await self.db.delete(user)
        await self.db.commit()
