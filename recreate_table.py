"""
데이터베이스 테이블 재생성 스크립트
기존 early_retirement_initial_setting 테이블을 삭제하고 새로 생성합니다.
주의: 이 스크립트는 모든 데이터를 삭제합니다!
"""
from sqlalchemy import text
from app.database import engine, Base
from app.models.early_retirement_initial_setting import EarlyRetirementInitialSetting

def recreate_table():
    """테이블 삭제 후 재생성"""
    with engine.connect() as conn:
        # 기존 테이블 삭제
        try:
            conn.execute(text("DROP TABLE IF EXISTS early_retirement_initial_setting CASCADE"))
            conn.commit()
            print("✓ 기존 테이블 삭제 완료")
        except Exception as e:
            print(f"테이블 삭제 중 오류 (무시 가능): {e}")
            conn.rollback()
        
        # 새 테이블 생성
        try:
            Base.metadata.create_all(bind=engine, tables=[EarlyRetirementInitialSetting.__table__])
            print("✓ 새 테이블 생성 완료")
            print("\n테이블 구조:")
            print("  - id: Integer (PK)")
            print("  - investable_assets: Numeric(15, 0) - 투자가능자산")
            print("  - standby_fund_ratio: Numeric(5, 0) - 대기자금 비율 (%)")
            print("  - standby_fund: Numeric(15, 0) - 대기자금 (자동계산)")
            print("  - dividend_option: Enum - 배당옵션")
        except Exception as e:
            print(f"테이블 생성 중 오류: {e}")
            raise

if __name__ == "__main__":
    print("=" * 50)
    print("데이터베이스 테이블 재생성")
    print("=" * 50)
    print("\n⚠️  경고: 이 작업은 모든 데이터를 삭제합니다!")
    response = input("\n계속하시겠습니까? (yes/no): ")
    
    if response.lower() == 'yes':
        recreate_table()
        print("\n✓ 작업 완료!")
    else:
        print("\n작업이 취소되었습니다.")

