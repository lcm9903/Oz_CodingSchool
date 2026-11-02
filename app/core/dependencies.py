"""
API에서 Depends()로 주입해 쓰는 공통 의존성 모음.

- get_current_user : Authorization: Bearer <access_token> 헤더로 로그인 유저를 찾는다.
- get_approved_user: 승인대기(pending)가 아닌 유저만 통과 (staff, admin)
- get_admin_user   : 관리자(admin)만 통과
- get_medical_user : 승인된 유저 중 부서가 '의료진(medical team)'인 유저만 통과
"""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db.databases import async_get_db
from app.core.security import decode_access_token
from app.models.user import Department, User, UserRole
from app.repositories.user_repository import UserRepository

# Swagger UI의 Authorize 버튼이 이 경로로 로그인 요청을 보낸다.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

DBSession = Annotated[AsyncSession, Depends(async_get_db)]


async def get_current_user(
    db: DBSession, token: Annotated[str, Depends(oauth2_scheme)]
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="인증 정보가 유효하지 않습니다. 다시 로그인해주세요.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    user_id = decode_access_token(token)
    if user_id is None:
        raise credentials_error

    user = await UserRepository(db).get_by_id(user_id)
    if user is None:
        raise credentials_error
    if not user.is_active:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "비활성화된 계정입니다.")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_approved_user(user: CurrentUser) -> User:
    if user.role == UserRole.PENDING:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            "승인 대기 중인 사용자입니다. 관리자의 승인 이후에 사용가능합니다.",
        )
    return user


ApprovedUser = Annotated[User, Depends(get_approved_user)]


async def get_admin_user(user: CurrentUser) -> User:
    if user.role != UserRole.ADMIN:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "관리자 권한이 필요합니다.")
    return user


AdminUser = Annotated[User, Depends(get_admin_user)]


async def get_medical_user(user: ApprovedUser) -> User:
    if user.department != Department.MEDICAL:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "의료진 부서의 사용자만 수행할 수 있습니다."
        )
    return user


MedicalUser = Annotated[User, Depends(get_medical_user)]
