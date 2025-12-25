# Early Retire Lab Backend (FastAPI)

FastAPI 기반 백엔드 API 서버

## 환경 설정

### Python 버전
Python 3.11 이상 필요

### 의존성 설치

```bash
pip install -r requirements.txt
```

또는 가상환경 사용:

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 환경 변수 설정

`.env` 파일을 생성하고 다음 내용을 추가:

```
DATABASE_URL=postgresql://postgres.cyuolmjjxpbakrpnytae:gA95PzY49k3qloq3@aws-1-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require
```

## 실행 방법

### 개발 서버 실행

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프로덕션 실행

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## API 엔드포인트

### 금융기관 API

- `GET /api/v1/financial-institutions/` - 전체 조회
- `GET /api/v1/financial-institutions/{id}` - 단일 조회
- `POST /api/v1/financial-institutions/` - 생성
- `PUT /api/v1/financial-institutions/{id}` - 수정
- `DELETE /api/v1/financial-institutions/{id}` - 삭제

## API 문서

서버 실행 후 다음 URL에서 API 문서 확인:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

