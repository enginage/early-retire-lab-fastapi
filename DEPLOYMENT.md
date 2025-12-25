# Vercel 배포 가이드

## Backend (FastAPI) 배포

### 1. Vercel 프로젝트 생성

1. Vercel 대시보드에서 새 프로젝트 생성
2. GitHub 저장소 연결: `enginage/early-retire-lab-fastapi`

### 2. 환경 변수 설정

Vercel 대시보드 > Settings > Environment Variables에서 다음 변수 추가:

- `DATABASE_URL`: PostgreSQL 연결 문자열
  - 예: `postgresql://user:password@host:port/database?sslmode=require`

- `ALLOWED_ORIGINS` (선택사항): CORS 허용 origin 목록 (쉼표로 구분)
  - 예: `https://early-retire-lab.vercel.app,https://www.yourdomain.com`
  - 설정하지 않으면 모든 origin 허용 (`*`)

### 3. 빌드 설정

Vercel는 자동으로 `vercel.json`을 읽어 설정을 적용합니다.

### 4. 배포 확인

배포 후 API 문서는 `https://your-project.vercel.app/docs`에서 확인 가능합니다.

## Frontend (React + Vite) 배포

### 1. Vercel 프로젝트 생성

1. Vercel 대시보드에서 새 프로젝트 생성
2. GitHub 저장소 연결: `enginage/early-retire-lab-frontend`

### 2. 환경 변수 설정

Vercel 대시보드 > Settings > Environment Variables에서 다음 변수 추가:

- `VITE_API_BASE_URL`: Backend API URL
  - 프로덕션: `https://your-backend-project.vercel.app`
  - 개발: `http://localhost:8000` (로컬 개발용)

### 3. 빌드 설정

- Framework Preset: Vite
- Build Command: `npm run build`
- Output Directory: `dist`
- Install Command: `npm install`

또는 `vercel.json` 파일이 자동으로 인식됩니다.

### 4. 배포 확인

배포 후 프론트엔드가 정상적으로 백엔드 API에 연결되는지 확인합니다.

## 보안 주의사항

⚠️ **중요**: 데이터베이스 연결 정보와 API 키는 절대 Git에 커밋하지 마세요.

- `.env` 파일은 `.gitignore`에 포함되어 있습니다
- 환경 변수는 Vercel 대시보드에서만 관리하세요
- GitHub에 노출된 시크릿이 있다면 즉시 변경하세요

