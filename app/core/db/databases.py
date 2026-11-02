from typing import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# 1) 접속 URL 구성
#    DATABASE_URL이 지정되어 있으면 그대로 사용하고, 없으면 MySQL(aiomysql 드라이버) URL을 만든다.
if settings.DATABASE_URL:
    DATABASE_URL = settings.DATABASE_URL
else:
    DATABASE_PREFIX = "mysql+aiomysql://"
    DATABASE_URI = (
        f"{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    DATABASE_URL = f"{DATABASE_PREFIX}{DATABASE_URI}?charset=utf8mb4"

# 2) 비동기 엔진 생성 (pool_pre_ping: 끊어진 커넥션 자동 감지)
async_engine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# SQLite는 기본적으로 외래키(ON DELETE CASCADE)가 꺼져 있으므로 연결 시마다 켜준다.
if DATABASE_URL.startswith("sqlite"):

    @event.listens_for(async_engine.sync_engine, "connect")
    def _enable_sqlite_fk(dbapi_connection, _):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# 3) 비동기 세션 팩토리
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine, autoflush=False, expire_on_commit=False
)

# 4) 모든 모델이 상속할 Base 클래스
Base = declarative_base()


# 5) 요청마다 세션을 하나 열고, 요청이 끝나면 닫아주는 의존성 함수
async def async_get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as db:
        yield db
