from typing import Annotated

from fastapi import APIRouter, Query, Response, status

from app.core.dependencies import ApprovedUser, DBSession, MedicalUser
from app.schemas.medical_record import MedicalRecordResponse
from app.schemas.patient import (
    PatientCreateRequest,
    PatientResponse,
    PatientSearchParams,
    PatientUpdateRequest,
)
from app.services.medical_record_service import MedicalRecordService
from app.services.patient_service import PatientService

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post(
    "",
    response_model=PatientResponse,
    status_code=status.HTTP_201_CREATED,
    summary="환자 등록 [REQ-PTNT-001] (의료진)",
)
async def create_patient(data: PatientCreateRequest, user: MedicalUser, db: DBSession):
    return await PatientService(db).create(data)


@router.get(
    "", response_model=list[PatientResponse], summary="환자 목록 조회 [REQ-PTNT-002]"
)
async def list_patients(
    params: Annotated[PatientSearchParams, Query()], user: ApprovedUser, db: DBSession
):
    return await PatientService(db).list(params)


@router.get(
    "/{patient_id}", response_model=PatientResponse, summary="환자 상세 조회 [REQ-PTNT-003]"
)
async def get_patient(patient_id: int, user: ApprovedUser, db: DBSession):
    return await PatientService(db).get_or_404(patient_id)


@router.patch(
    "/{patient_id}",
    response_model=PatientResponse,
    summary="환자 정보 수정 [REQ-PTNT-004] (의료진)",
)
async def update_patient(
    patient_id: int, data: PatientUpdateRequest, user: MedicalUser, db: DBSession
):
    return await PatientService(db).update(patient_id, data)


@router.delete(
    "/{patient_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="환자 삭제 [REQ-PTNT-005] (의료진)",
)
async def delete_patient(patient_id: int, user: MedicalUser, db: DBSession):
    await PatientService(db).delete(patient_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{patient_id}/medical-records",
    response_model=list[MedicalRecordResponse],
    summary="환자별 진료기록 목록 조회 [REQ-MDR-002]",
)
async def list_patient_records(patient_id: int, user: ApprovedUser, db: DBSession):
    return await MedicalRecordService(db).list_by_patient(patient_id)
