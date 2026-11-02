from fastapi import APIRouter, Query

from app.core.dependencies import AdminUser, DBSession
from app.models.user import Department
from app.schemas.user import RoleUpdateRequest, UserResponse
from app.services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/users", response_model=list[UserResponse], summary="회원 목록 조회 [REQ-USER-004]"
)
async def list_users(
    admin: AdminUser,
    db: DBSession,
    query: str | None = Query(default=None, description="이름 또는 이메일 검색어"),
    department: Department | None = Query(default=None, description="부서 필터"),
):
    return await UserService(db).list_users(query, department)


@router.patch(
    "/users/role", response_model=UserResponse, summary="회원 권한 변경 [REQ-USER-005]"
)
async def update_user_role(data: RoleUpdateRequest, admin: AdminUser, db: DBSession):
    return await UserService(db).update_role(admin, data)
