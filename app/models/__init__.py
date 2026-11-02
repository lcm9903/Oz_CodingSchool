# alembic/env.py가 `from app import models`로 이 패키지를 불러오면
# 아래 모델들이 Base.metadata에 등록되어 autogenerate 대상이 된다.
from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.models.user import Department, Gender, User, UserRole

__all__ = [
    "Department",
    "Gender",
    "MedicalRecord",
    "Patient",
    "Prediction",
    "User",
    "UserRole",
]
