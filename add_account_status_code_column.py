"""
ISA 계좌 테이블에 account_status_code 컬럼 추가 스크립트
"""
from sqlalchemy import text
from app.database import engine

def add_account_status_code_column():
    """account_status_code 컬럼 추가"""
    with engine.connect() as conn:
        try:
            # 컬럼이 이미 존재하는지 확인
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='isa_account' AND column_name='account_status_code'
            """))
            
            if result.fetchone():
                print("[INFO] account_status_code 컬럼이 이미 존재합니다.")
                return
            
            # 컬럼 추가
            conn.execute(text("""
                ALTER TABLE isa_account 
                ADD COLUMN account_status_code VARCHAR(50)
            """))
            conn.commit()
            print("[OK] account_status_code 컬럼 추가 완료")
        except Exception as e:
            print(f"컬럼 추가 중 오류: {e}")
            conn.rollback()
            raise

if __name__ == "__main__":
    print("=" * 50)
    print("ISA 계좌 테이블에 account_status_code 컬럼 추가")
    print("=" * 50)
    
    try:
        add_account_status_code_column()
        print("\n작업 완료!")
    except Exception as e:
        print(f"\n작업 실패: {e}")


