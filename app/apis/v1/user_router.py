from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.dependencies import CurrentUser, DBSession
from app.schemas.common import MessageResponse
from app.schemas.user import (
    PasswordUpdateRequest,
    TokenResponse,
    UserResponse,
    UserSignupRequest,
    UserUpdateRequest,
)
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])

REFRESH_COOKIE_NAME = "refresh_token"
REFRESH_COOKIE_PATH = "/api/v1/users"  # 리프레시/로그아웃 요청에만 쿠키가 전송되도록 제한


def _set_refresh_cookie(response: Response, token: str) -> None:
    """NFR-USER-001: 리프레시 토큰은 JS에서 접근할 수 없도록 HTTP-only 쿠키로 전달"""
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        path=REFRESH_COOKIE_PATH,
    )


def _delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(key=REFRESH_COOKIE_NAME, path=REFRESH_COOKIE_PATH)


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입 [REQ-USER-001]",
)
async def signup(data: UserSignupRequest, db: DBSession):
    return await UserService(db).signup(data)


@router.post("/login", response_model=TokenResponse, summary="로그인 [REQ-USER-002]")
async def login(
    response: Response,
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DBSession,
):
    """username 필드에 이메일을 입력한다. (OAuth2 표준 폼 → Swagger Authorize 버튼과 호환)"""
    access_token, refresh_token = await UserService(db).login(form.username, form.password)
    _set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post(
    "/refresh", response_model=TokenResponse, summary="엑세스 토큰 재발급 [NFR-USER-001]"
)
async def refresh(
    db: DBSession,
    refresh_token: Annotated[str | None, Cookie(alias=REFRESH_COOKIE_NAME)] = None,
):
    access_token = await UserService(db).refresh_access_token(refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/logout", response_model=MessageResponse, summary="로그아웃 [REQ-USER-003]")
async def logout(response: Response):
    """엑세스 토큰이 만료된 상태에서도 로그아웃할 수 있도록 인증을 요구하지 않는다."""
    _delete_refresh_cookie(response)
    return MessageResponse(message="로그아웃되었습니다.")


@router.get("/me", response_model=UserResponse, summary="내 정보 조회 [REQ-USER-006]")
async def get_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserResponse, summary="내 정보 수정 [REQ-USER-007]")
async def update_me(data: UserUpdateRequest, user: CurrentUser, db: DBSession):
    return await UserService(db).update_me(user, data)


@router.patch(
    "/me/password", response_model=MessageResponse, summary="비밀번호 변경 [REQ-USER-008]"
)
async def update_password(data: PasswordUpdateRequest, user: CurrentUser, db: DBSession):
    await UserService(db).update_password(user, data)
    return MessageResponse(message="비밀번호가 변경되었습니다.")


@router.delete(
    "/me", status_code=status.HTTP_204_NO_CONTENT, summary="회원 탈퇴 [REQ-USER-009]"
)
async def delete_me(response: Response, user: CurrentUser, db: DBSession):
    await UserService(db).delete_me(user)
    _delete_refresh_cookie(response)
    return None
