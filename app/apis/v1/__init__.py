from fastapi import APIRouter

from app.apis.v1.admin_router import router as admin_router
from app.apis.v1.medical_record_router import router as medical_record_router
from app.apis.v1.patient_router import router as patient_router
from app.apis.v1.user_router import router as user_router

# 모든 v1 라우터를 하나로 묶는다. main.py에서 prefix="/api/v1"로 등록된다.
api_router = APIRouter()
api_router.include_router(user_router)
api_router.include_router(admin_router)
api_router.include_router(patient_router)
api_router.include_router(medical_record_router)
