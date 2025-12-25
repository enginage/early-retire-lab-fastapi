"""
국내ETF 테이블 생성 스크립트
"""
from app.database import Base, engine
from app.models.domestic_etf import DomesticETF

def create_table():
    """테이블 생성"""
    try:
        Base.metadata.create_all(bind=engine, tables=[DomesticETF.__table__])
        print("[OK] domestic_etf 테이블이 성공적으로 생성되었습니다.")
    except Exception as e:
        print(f"[ERROR] 테이블 생성 중 오류 발생: {e}")

if __name__ == "__main__":
    create_table()

