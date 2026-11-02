# 📚 과제 문서 (docs)

오즈코딩스쿨 AI 헬스케어 7기 웹 개발 트랙 과제 **「FastAPI를 활용한 인공지능 모델 서빙」**의 단계별 산출물 문서입니다.
흉부 X-ray 이미지로 폐렴 여부를 예측하는 AI 진단 지원 웹 서비스를 만듭니다.

> 프로젝트 실행 방법은 루트의 [README.md](../README.md)를 참고하세요.

## 문서 목록

| 단계 | 문서 | 내용 | 완료 조건 |
|---|---|---|---|
| 3일차 ① | [3일차_프로젝트_뜯어보기.md](./3일차_프로젝트_뜯어보기.md) | 디렉터리·파일 역할, DB 연결 설정, SQLAlchemy 모델과 alembic 마이그레이션, API 구현 흐름 | PR을 거쳐 `main` 머지 |
| 3일차 ② | [3일차_db_migration.md](./3일차_db_migration.md) | ERD, 테이블 설계 포인트, 마이그레이션 수행 방법, DB Viewer 캡처 | 모델·마이그레이션 파일 PR 머지, DB Viewer로 스키마 확인 |
| 4일차 | [4일차_USER_API_설계.md](./4일차_USER_API_설계.md) | 회원가입·로그인·JWT 인증, 마이페이지, 관리자 회원 관리 API 명세 | `main` 또는 `develop` 머지, Swagger UI 테스트 |
| 5일차 | [5일차_환자관리_API_설계.md](./5일차_환자관리_API_설계.md) | 환자 등록·조회·수정·삭제, 진료기록(X-ray 업로드) API 명세 | `main` 또는 `develop` 머지 |
| 6일차 | [6일차_폐렴예측_API_설계.md](./6일차_폐렴예측_API_설계.md) | AI 모델(SimpleCNN) 구조와 추론 과정, 폐렴 예측 API 명세, 모델 평가 기준 | `main` 머지 |
| 7일차 | [7일차_앱_실행화면.md](./7일차_앱_실행화면.md) | 엔드포인트별 프론트엔드 동작 화면 | `main` 또는 `develop` 머지 |

## 서비스 한눈에 보기

```
회원가입 ─▶ 관리자 승인 ─▶ 로그인
                              │
              ┌───────────────┼────────────────┐
              ▼               ▼                ▼
          환자 관리        진료기록 등록       AI 폐렴 예측
       (등록·조회·수정·삭제)  (X-ray 업로드)   (Positive/Negative + Confidence)
```

| 권한 | 할 수 있는 일 |
|---|---|
| 승인대기 (`pending`) | 로그인만 가능, 관리자 승인 필요 |
| 스태프 (`staff`) | 환자·진료기록 조회, AI 예측 |
| 스태프 + 의료진 부서 | 위 기능 + 환자 등록·수정·삭제, 진료기록 등록 |
| 어드민 (`admin`) | 위 기능 + 회원 목록 조회, 권한 변경 |

## 전체 API 요약

| 구분 | 요구사항 | Method | URL |
|---|---|---|---|
| 회원 | REQ-USER-001 | POST | `/api/v1/users/signup` |
| | REQ-USER-002 | POST | `/api/v1/users/login` |
| | NFR-USER-001 | POST | `/api/v1/users/refresh` |
| | REQ-USER-003 | POST | `/api/v1/users/logout` |
| | REQ-USER-006 | GET | `/api/v1/users/me` |
| | REQ-USER-007 | PATCH | `/api/v1/users/me` |
| | REQ-USER-008 | PATCH | `/api/v1/users/me/password` |
| | REQ-USER-009 | DELETE | `/api/v1/users/me` |
| 관리자 | REQ-USER-004 | GET | `/api/v1/admin/users` |
| | REQ-USER-005 | PATCH | `/api/v1/admin/users/role` |
| 환자 | REQ-PTNT-001 | POST | `/api/v1/patients` |
| | REQ-PTNT-002 | GET | `/api/v1/patients` |
| | REQ-PTNT-003 | GET | `/api/v1/patients/{patient_id}` |
| | REQ-PTNT-004 | PATCH | `/api/v1/patients/{patient_id}` |
| | REQ-PTNT-005 | DELETE | `/api/v1/patients/{patient_id}` |
| 진료기록 | REQ-MDR-001 | POST | `/api/v1/medical-records` |
| | REQ-MDR-002 | GET | `/api/v1/patients/{patient_id}/medical-records` |
| | REQ-MDR-003 | GET | `/api/v1/medical-records/{record_id}` |
| AI 예측 | REQ-PRED-001 | POST | `/api/v1/medical-records/{record_id}/predict` |
| | REQ-PRED-002 | GET | `/api/v1/medical-records/{record_id}/analyses` |

## 캡처 이미지 넣는 방법 (`images/`)

3일차 DB Viewer 화면과 7일차 실행화면은 직접 캡처해야 합니다.
아래 파일명으로 `docs/images/`에 저장하면 각 문서에 자동으로 표시됩니다.

**3일차_db_migration.md**
| 파일명 | 캡처할 화면 |
|---|---|
| `db_viewer_tables.png` | DB Viewer(DBeaver 등)의 `ai_health` 테이블 목록 |
| `db_viewer_erd.png` | DB Viewer의 ERD 화면 |

**7일차_앱_실행화면.md**
| 파일명 | 캡처할 화면 |
|---|---|
| `01_signup.png` | 회원가입 |
| `02_login.png` / `02_login_pending.png` | 로그인 / 승인대기 홈 화면 |
| `03_refresh.png` | 토큰 재발급 (Network 탭) |
| `04_logout.png` | 로그아웃 |
| `05_my_page.png` | 마이페이지 |
| `06_update_me.png` | 내 정보 수정 |
| `07_update_password.png` | 비밀번호 변경 |
| `08_delete_me.png` | 회원 탈퇴 |
| `09_admin_users.png` / `09_admin_users_filter.png` | 회원 목록 / 검색·필터 |
| `10_update_role.png` | 회원 권한 변경 |
| `11_patient_create.png` / `11_patient_create_forbidden.png` | 환자 등록 / 의료진 아닌 계정의 등록 시도 |
| `12_patients.png` / `12_patients_filter.png` | 환자 목록 / 검색·필터 |
| `13_patient_detail.png` | 환자 상세 |
| `14_patient_update.png` | 환자 정보 수정 |
| `15_patient_delete.png` | 환자 삭제 |
| `16_record_create.png` | 진료기록 등록 |
| `17_record_list.png` | 진료기록 목록 |
| `18_record_detail.png` | 진료기록 상세 |
| `19_predict.png` / `19_predict_cached.png` | AI 예측 실행 / 재요청 시 200 응답 (Network 탭) |
| `20_analyses.png` | 예측 결과 목록 |
| `21_swagger.png` | Swagger UI |

> 💡 개발자도구(F12) → Network 탭을 함께 열어두고 캡처하면 API 요청과 상태코드까지 보여줄 수 있습니다.

## Git 브랜치 전략

모든 문서와 코드는 **PR을 거쳐** `develop` 또는 `main` 브랜치에 머지합니다.

```
feature/<작업명> ──PR──▶ develop ──PR──▶ main
```
