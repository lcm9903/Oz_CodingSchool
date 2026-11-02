from pathlib import Path

from pydantic_settings import BaseSettings

# 프로젝트 루트 경로 (app/core/config.py 기준 두 단계 위)
BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """
    애플리케이션 전역 설정.
    .env 파일 또는 환경변수에서 값을 읽어오며, 없으면 아래 기본값을 사용한다.
    """

    # --- Database ---
    DB_USER: str = "root"
    DB_PASSWORD: str = "password1234"
    DB_HOST: str = "localhost"
    DB_PORT: str = "3306"
    DB_NAME: str = "ai_health"
    # 값이 있으면 위 MySQL 설정 대신 이 URL을 사용한다.
    # 예) 로컬 테스트용 SQLite: sqlite+aiosqlite:///./ai_health.db
    DATABASE_URL: str | None = None

    # --- JWT (NFR-USER-001) ---
    # 반드시 .env에서 길고 무작위한 값으로 교체할 것
    ACCESS_TOKEN_SECRET_KEY: str = "change-me-access-secret"
    REFRESH_TOKEN_SECRET_KEY: str = "change-me-refresh-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # 엑세스 토큰 만료: 30분
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # 리프레시 토큰 만료: 7일
    # HTTPS 환경에서는 True로 설정 (로컬 http 개발 환경은 False)
    COOKIE_SECURE: bool = False

    # --- 파일 저장 경로 ---
    MEDIA_DIR: Path = BASE_DIR / "media"
    STATIC_DIR: Path = BASE_DIR / "static"

    # --- AI 모델 (worker) ---
    # model_state_dict.pth(가중치만) 권장. model.pth(구조 포함)도 지원한다.
    AI_MODEL_PATH: Path = BASE_DIR / "worker" / "models" / "model_state_dict.pth"
    AI_MODEL_NAME: str = "SimpleCNN-v1"
    # 노션 제공 SimpleCNN은 128x128 입력으로 학습됨 (다른 크기면 Linear 층에서 오류)
    AI_IMAGE_SIZE: int = 128
    AI_THRESHOLD: float = 0.5  # 폐렴 확률이 이 값 이상이면 Positive
    AI_NORMALIZE: str = "none"  # 학습 시 정규화: "none"(0~1) 또는 "imagenet"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
