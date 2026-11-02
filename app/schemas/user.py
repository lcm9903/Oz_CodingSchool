import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field

from app.models.user import Department, Gender, UserRole
from app.schemas.common import PhoneNumber, UTCDateTime

PASSWORD_RULE_MESSAGE = (
    "비밀번호는 대소문자, 특수문자, 숫자를 각 1개씩 포함한 8자리 이상이어야 합니다."
)
_PASSWORD_PATTERN = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z0-9]).{8,}$"
)


def _validate_password_rule(value: str) -> str:
    if not _PASSWORD_PATTERN.match(value):
        raise ValueError(PASSWORD_RULE_MESSAGE)
    return value


Password = Annotated[str, AfterValidator(_validate_password_rule)]


# ---------- 요청(Request) ----------
class UserSignupRequest(BaseModel):
    """REQ-USER-001 회원가입"""

    email: EmailStr
    password: Password
    name: str = Field(min_length=1, max_length=50)
    department: Department
    gender: Gender
    phone_number: PhoneNumber


class UserUpdateRequest(BaseModel):
    """REQ-USER-007 회원 정보 수정 (Partial: 보낸 항목만 수정)"""

    department: Department | None = None
    phone_number: PhoneNumber | None = None


class PasswordUpdateRequest(BaseModel):
    """REQ-USER-008 비밀번호 변경"""

    current_password: str
    new_password: Password


class RoleUpdateRequest(BaseModel):
    """REQ-USER-005 회원 권한 변경 (관리자)"""

    user_id: int
    new_role: UserRole


# ---------- 응답(Response) ----------
class UserResponse(BaseModel):
    """REQ-USER-004 / REQ-USER-006 에서 확인 가능한 항목"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    name: str
    department: Department
    gender: Gender
    phone_number: str
    role: UserRole
    is_active: bool
    created_at: UTCDateTime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
