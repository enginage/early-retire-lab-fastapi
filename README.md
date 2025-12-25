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

```env
DATABASE_URL=postgresql://user:password@host:port/database?sslmode=require
```

**주의**: 실제 데이터베이스 URL은 보안상 `.env` 파일에만 저장하고 Git에 커밋하지 마세요.

Vercel 배포 시 환경 변수는 Vercel 대시보드에서 설정해야 합니다.

자세한 배포 가이드는 [DEPLOYMENT.md](./DEPLOYMENT.md)를 참조하세요.

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
