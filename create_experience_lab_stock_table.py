"""
체험실 종목 테이블 생성 스크립트
"""
from app.database import Base, engine
from app.models.experience_lab_stock import ExperienceLabStock

def create_table():
    """테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine, tables=[ExperienceLabStock.__table__])
        print("[OK] experience_lab_stock 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"[ERROR] 테이블 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    create_table()

