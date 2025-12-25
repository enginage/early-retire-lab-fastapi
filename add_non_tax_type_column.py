"""
ISA 계좌 테이블에 non_tax_type 컬럼 추가 스크립트
"""
from sqlalchemy import text
from app.database import SessionLocal, engine

def add_non_tax_type_column():
    db = SessionLocal()
    try:
        # non_tax_type 컬럼 추가 (기존 데이터는 빈 문자열로 설정)
        with engine.connect() as conn:
            # 컬럼이 이미 존재하는지 확인
            check_query = text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='isa_account' AND column_name='non_tax_type'
            """)
            result = conn.execute(check_query)
            if result.fetchone():
                print("non_tax_type 컬럼이 이미 존재합니다.")
                return
            
            # 컬럼 추가
            alter_query = text("""
                ALTER TABLE isa_account 
                ADD COLUMN non_tax_type VARCHAR(50) NOT NULL DEFAULT ''
            """)
            conn.execute(alter_query)
            conn.commit()
            print("non_tax_type 컬럼이 성공적으로 추가되었습니다.")
    except Exception as e:
        print(f"오류 발생: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_non_tax_type_column()

