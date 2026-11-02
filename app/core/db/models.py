import uuid as uuid_pkg
from datetime import datetime

from sqlalchemy import Boolean, DateTime, func
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import Mapped, mapped_column
from uuid6 import uuid7


class UUIDMixin:
    uuid: Mapped[uuid_pkg.UUID] = mapped_column(
        CHAR(36), primary_key=True, default=uuid7
    )


class TimestampMixin:
    """
    생성/수정 시각을 DB 서버 시간(UTC 기준 컨테이너)으로 기록한다.

    기존 코드의 default=datetime.now(UTC)는 '서버가 켜진 순간' 한 번만 계산되어
    모든 행이 같은 시각으로 저장되는 버그가 있어 func.now()로 바꿨다.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, server_default=func.now(), onupdate=func.now()
    )


class SoftDeleteMixin:
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
