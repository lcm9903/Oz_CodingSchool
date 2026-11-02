from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    hash_password,
    verify_password,
)
from app.models.user import Department, User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user import (
    PasswordUpdateRequest,
    RoleUpdateRequest,
    UserSignupRequest,
    UserUpdateRequest,
)


class UserService:
    """회원/인증 관련 비즈니스 로직 (검증, 권한 판단, 토큰 발급 등)"""

    def __init__(self, db: AsyncSession):
        self.repo = UserRepository(db)

    # ---------- REQ-USER-001 회원가입 ----------
    async def signup(self, data: UserSignupRequest) -> User:
        if await self.repo.get_by_email(data.email):
            raise HTTPException(status.HTTP_409_CONFLICT, "이미 가입된 이메일입니다.")

        user = User(
            email=data.email,
            password=hash_password(data.password),
            name=data.name,
            department=data.department,
            gender=data.gender,
            phone_number=data.phone_number,
            role=UserRole.PENDING,  # 가입 직후에는 관리자 승인 대기
            is_active=True,
        )
        return await self.repo.save(user)

    # ---------- REQ-USER-002 로그인 / NFR-USER-001 토큰 발급 ----------
    async def login(self, email: str, password: str) -> tuple[str, str]:
        user = await self.repo.get_by_email(email)
        if user is None or not verify_password(password, user.password):
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED,
                "이메일 또는 비밀번호가 올바르지 않습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "비활성화된 계정입니다.")
        return create_access_token(user.id), create_refresh_token(user.id)

    async def refresh_access_token(self, refresh_token: str | None) -> str:
        """리프레시 토큰으로 엑세스 토큰을 재발급. 리프레시 토큰도 만료되면 401 → 재로그인 유도"""
        error = HTTPException(
            status.HTTP_401_UNAUTHORIZED, "로그인이 만료되었습니다. 다시 로그인해주세요."
        )
        if not refresh_token:
            raise error
        user_id = decode_refresh_token(refresh_token)
        if user_id is None:
            raise error
        user = await self.repo.get_by_id(user_id)
        if user is None or not user.is_active:
            raise error
        return create_access_token(user.id)

    # ---------- REQ-USER-007 회원 정보 수정 (Partial) ----------
    async def update_me(self, user: User, data: UserUpdateRequest) -> User:
        # exclude_unset: 요청에 실제로 포함된 필드만 수정한다.
        for field, value in data.model_dump(exclude_unset=True).items():
            if value is not None:
                setattr(user, field, value)
        return await self.repo.save(user)

    # ---------- REQ-USER-008 비밀번호 변경 ----------
    async def update_password(self, user: User, data: PasswordUpdateRequest) -> None:
        if not verify_password(data.current_password, user.password):
            # 401은 프론트에서 '토큰 만료'로 처리되어 로그아웃되므로 403을 사용한다.
            raise HTTPException(
                status.HTTP_403_FORBIDDEN, "현재 비밀번호가 일치하지 않습니다."
            )
        if data.current_password == data.new_password:
            raise HTTPException(
                status.HTTP_409_CONFLICT, "새 비밀번호가 현재 비밀번호와 같습니다."
            )
        user.password = hash_password(data.new_password)
        await self.repo.save(user)

    # ---------- REQ-USER-009 회원 탈퇴 (DB에서 즉시 삭제) ----------
    async def delete_me(self, user: User) -> None:
        await self.repo.delete(user)

    # ---------- REQ-USER-004 회원 목록 조회 (관리자) ----------
    async def list_users(
        self, query: str | None, department: Department | None
    ) -> list[User]:
        return await self.repo.list(query=query, department=department)

    # ---------- REQ-USER-005 회원 권한 변경 (관리자) ----------
    async def update_role(self, admin: User, data: RoleUpdateRequest) -> User:
        if admin.id == data.user_id:
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST, "본인의 권한은 변경할 수 없습니다."
            )
        target = await self.repo.get_by_id(data.user_id)
        if target is None:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "존재하지 않는 회원입니다.")
        target.role = data.new_role
        return await self.repo.save(target)
