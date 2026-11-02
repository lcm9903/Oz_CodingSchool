"""
비밀번호 해싱과 JWT 발급/검증을 담당한다.

- 비밀번호: argon2 해시로만 저장한다 (원문 저장 금지).
- JWT (NFR-USER-001)
  * 엑세스 토큰 30분, 리프레시 토큰 7일
  * 페이로드에는 최소 식별 정보인 user_id(+ 만료시각 exp)만 담는다.
  * 엑세스/리프레시 토큰은 서로 다른 비밀키로 서명해, 한쪽 토큰을 다른 용도로 쓸 수 없게 한다.
"""

from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import settings

_password_hasher = PasswordHasher()


# ---------- 비밀번호 ----------
def hash_password(plain_password: str) -> str:
    return _password_hasher.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return _password_hasher.verify(hashed_password, plain_password)
    except (VerificationError, InvalidHashError):
        return False


# ---------- JWT ----------
def _create_token(user_id: int, secret_key: str, expires_delta: timedelta) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.now(UTC) + expires_delta,
    }
    return jwt.encode(payload, secret_key, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(
        user_id,
        settings.ACCESS_TOKEN_SECRET_KEY,
        timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


def create_refresh_token(user_id: int) -> str:
    return _create_token(
        user_id,
        settings.REFRESH_TOKEN_SECRET_KEY,
        timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )


def _decode_token(token: str, secret_key: str) -> int | None:
    """토큰이 유효하면 user_id를, 만료/위조 등으로 유효하지 않으면 None을 반환한다."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
    user_id = payload.get("user_id")
    return user_id if isinstance(user_id, int) else None


def decode_access_token(token: str) -> int | None:
    return _decode_token(token, settings.ACCESS_TOKEN_SECRET_KEY)


def decode_refresh_token(token: str) -> int | None:
    return _decode_token(token, settings.REFRESH_TOKEN_SECRET_KEY)
