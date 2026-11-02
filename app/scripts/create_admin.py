"""
첫 관리자 계정을 만들거나, 이미 가입한 계정을 관리자로 승격하는 스크립트.

가입 직후 모든 계정은 '승인대기(pending)' 상태이므로,
회원 관리 화면을 쓰려면 최소 한 명의 관리자가 필요하다.

사용법 (프로젝트 루트에서)
    # 이미 회원가입한 계정을 관리자로 승격
    uv run python -m app.scripts.create_admin admin@example.com

    # 새 관리자 계정 생성
    uv run python -m app.scripts.create_admin admin@example.com --password 'Admin123!' \
        --name 관리자 --department developer --gender female --phone 01012345678
"""

import argparse
import asyncio

from app.core.db.databases import AsyncSessionLocal, async_engine
from app.core.security import hash_password
from app.models import Department, Gender, User, UserRole
from app.repositories.user_repository import UserRepository


async def main(args: argparse.Namespace) -> None:
    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)
        user = await repo.get_by_email(args.email)

        if user:
            user.role = UserRole.ADMIN
            await repo.save(user)
            print(f"✅ {user.email} 계정을 관리자로 변경했습니다.")
        elif args.password:
            user = User(
                email=args.email,
                password=hash_password(args.password),
                name=args.name,
                department=Department(args.department),
                gender=Gender(args.gender),
                phone_number=args.phone,
                role=UserRole.ADMIN,
                is_active=True,
            )
            await repo.save(user)
            print(f"✅ 관리자 계정 {user.email} 을(를) 생성했습니다.")
        else:
            print("❌ 해당 이메일의 계정이 없습니다. 새로 만들려면 --password 를 함께 입력하세요.")

    await async_engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="관리자 계정 생성/승격")
    parser.add_argument("email")
    parser.add_argument("--password")
    parser.add_argument("--name", default="관리자")
    parser.add_argument(
        "--department", default="developer", choices=[d.value for d in Department]
    )
    parser.add_argument("--gender", default="female", choices=[g.value for g in Gender])
    parser.add_argument("--phone", default="01000000000")
    asyncio.run(main(parser.parse_args()))
