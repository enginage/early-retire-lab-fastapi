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
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
if allowed_origins == ["*"]:
    # 프로덕션에서는 기본적으로 모든 origin 허용 (필요시 환경 변수로 제한)
    allowed_origins = ["*"]

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

