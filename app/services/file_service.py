"""업로드 파일(X-ray 이미지)을 media 폴더에 저장/삭제한다."""

from io import BytesIO
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from uuid6 import uuid7

from app.core.config import settings

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10MB
XRAY_SUBDIR = "xray"


async def save_xray_image(file: UploadFile) -> str:
    """
    이미지를 검증한 뒤 media/xray/<uuid>.<ext> 로 저장하고,
    media 폴더 기준 상대경로(예: 'xray/0190....png')를 반환한다.
    """
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "PNG 또는 JPG 이미지만 업로드할 수 있습니다."
        )

    content = await file.read()
    if not content:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "빈 파일입니다.")
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "이미지 크기는 10MB 이하여야 합니다."
        )

    # 확장자만 바꾼 가짜 이미지가 아닌지 실제로 열어서 확인
    try:
        with Image.open(BytesIO(content)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, "올바른 이미지 파일이 아닙니다."
        ) from None

    relative_path = f"{XRAY_SUBDIR}/{uuid7()}{extension}"
    destination = settings.MEDIA_DIR / relative_path
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(content)
    return relative_path


def media_path(relative_path: str) -> Path:
    return settings.MEDIA_DIR / relative_path


def delete_media_file(relative_path: str) -> None:
    path = media_path(relative_path)
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass  # 파일 삭제 실패가 API 실패로 이어지지 않도록 무시
