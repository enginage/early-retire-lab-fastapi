from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.database import engine, Base
import os

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Early Retire Lab API",
    description="조기은퇴연구소 백엔드 API",
    version="1.0.0"
)

# CORS 설정
# 환경 변수에서 허용할 origin 목록 가져오기
allowed_origins_env = os.getenv("ALLOWED_ORIGINS", "")
if allowed_origins_env:
    # 환경 변수에 값이 있으면 쉼표로 분리해서 사용
    allowed_origins = [origin.strip() for origin in allowed_origins_env.split(",")]
else:
    # 환경 변수가 없으면 기본값으로 로컬 및 Vercel 도메인 허용
    allowed_origins = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://early-retire-lab.vercel.app",
        "https://enginage.github.io",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Early Retire Lab API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

