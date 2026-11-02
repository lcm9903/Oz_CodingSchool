import enum

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db.databases import Base
from app.core.db.models import TimestampMixin


class Department(str, enum.Enum):
    DEVELOPER = "developer"  # 개발팀
    MEDICAL = "medical team"  # 의료진
    RESEARCHER = "researcher"  # 연구진


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"


class UserRole(str, enum.Enum):
    PENDING = "pending"  # 대기자 (가입 직후 기본값)
    STAFF = "staff"  # 스태프
    ADMIN = "admin"  # 어드민


def enum_column(enum_cls: type[enum.Enum], name: str) -> Enum:
    """Enum의 '값'(예: 'medical team')을 DB에 저장하도록 하는 공통 컬럼 타입."""
    return Enum(
        enum_cls,
        name=name,
        values_callable=lambda e: [member.value for member in e],
        validate_strings=True,
    )


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))  # argon2 해시
    name: Mapped[str] = mapped_column(String(50), index=True)
    department: Mapped[Department] = mapped_column(enum_column(Department, "department"))
    gender: Mapped[Gender] = mapped_column(enum_column(Gender, "gender"))
    phone_number: Mapped[str] = mapped_column(String(20))
    role: Mapped[UserRole] = mapped_column(
        enum_column(UserRole, "user_role"), default=UserRole.PENDING
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
