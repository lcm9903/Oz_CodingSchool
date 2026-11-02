import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from starlette.staticfiles import StaticFiles

from app.apis.v1 import api_router
from app.core.config import settings
from worker.model import predictor

logging.basicConfig(level=logging.INFO)

STATIC_DIR = settings.STATIC_DIR
MEDIA_DIR = settings.MEDIA_DIR

# 만약 static, media 폴더가 존재하지 않으면 생성
STATIC_DIR.mkdir(parents=True, exist_ok=True)
MEDIA_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 서버가 시작될 때 AI 모델을 한 번만 메모리에 올려둔다.
    predictor.load()
    yield


app = FastAPI(
    title="AI Health - 흉부 X-ray 폐렴 진단 지원 API",
    version="1.0.0",
    lifespan=lifespan,
)


# 요청 값 검증 실패(422)를 400으로 통일한다.
# 프론트엔드가 400 응답을 기준으로 비밀번호 규칙 안내 등을 표시하기 때문.
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": jsonable_encoder(exc.errors(), custom_encoder={Exception: str})},
    )


# ⚠️ API 라우터는 아래의 catch-all 라우트보다 먼저 등록해야 한다.
app.include_router(api_router, prefix="/api/v1")

# 'static' 폴더를 '/static' 경로로 마운트 (CSS, JS 파일 서빙용)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
# 'media' 폴더를 '/media' 경로로 마운트 (사용자 업로드 파일 서빙용)
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")


@app.get(path="/healthcheck", status_code=200, include_in_schema=False)
async def healthcheck():
    return {"status": "ok", "ai_model_ready": predictor.is_ready}


@app.get("/", include_in_schema=False)
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/{path:path}", include_in_schema=False)
async def catch_all(path: str):
    # 프론트엔드(SPA) 화면 경로는 모두 index.html을 돌려준다.
    # API나 정적 파일 경로는 제외 (FastAPI가 먼저 매칭하지 못한 경우에만 실행됨)
    if (
        path.startswith("api/")
        or path.startswith("static/")
        or path.startswith("media/")
    ):
        raise HTTPException(status_code=404)
    return FileResponse(STATIC_DIR / "index.html")
