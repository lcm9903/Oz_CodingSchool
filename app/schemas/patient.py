from pydantic import BaseModel, ConfigDict, Field

from app.models.user import Gender
from app.schemas.common import PhoneNumber, UTCDateTime


class PatientCreateRequest(BaseModel):
    """REQ-PTNT-001 환자 등록"""

    name: str = Field(min_length=1, max_length=50)
    age: int = Field(ge=0, le=150)
    gender: Gender
    phone_number: PhoneNumber


class PatientUpdateRequest(BaseModel):
    """REQ-PTNT-004 환자 정보 수정 (Partial)"""

    name: str | None = Field(default=None, min_length=1, max_length=50)
    age: int | None = Field(default=None, ge=0, le=150)
    phone_number: PhoneNumber | None = None


class PatientSearchParams(BaseModel):
    """REQ-PTNT-002 환자 목록 검색 조건 (쿼리 파라미터)"""

    name: str | None = None
    gender: Gender | None = None
    min_age: int | None = Field(default=None, ge=0)
    max_age: int | None = Field(default=None, ge=0)


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    age: int
    gender: Gender
    phone_number: str
    created_at: UTCDateTime
