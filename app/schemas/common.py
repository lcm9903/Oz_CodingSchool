import re
from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, PlainSerializer


def _to_utc_iso(value: datetime) -> str:
    """
    DB에는 UTC 시각이 시간대 정보 없이 저장된다.
    응답 시 'Z'(UTC)를 붙여 브라우저가 사용자 지역 시간(예: KST)으로 올바르게 변환하게 한다.
    """
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


UTCDateTime = Annotated[datetime, PlainSerializer(_to_utc_iso, return_type=str)]

PHONE_PATTERN = re.compile(r"^01[016789]\d{7,8}$")


def validate_phone_number(value: str) -> str:
    """'010-1234-5678' 같은 입력도 숫자만 남겨 검사한다."""
    digits = re.sub(r"\D", "", value)
    if not PHONE_PATTERN.match(digits):
        raise ValueError("휴대폰 번호 형식이 올바르지 않습니다. (예: 01012345678)")
    return digits


PhoneNumber = Annotated[str, AfterValidator(validate_phone_number)]


class MessageResponse(BaseModel):
    message: str
