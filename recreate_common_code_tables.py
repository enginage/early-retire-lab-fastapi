"""
공통코드 테이블 재생성 스크립트
기존 common_code_master, common_code_detail 테이블을 삭제하고 새로 생성합니다.
주의: 이 스크립트는 모든 데이터를 삭제합니다!
"""
from sqlalchemy import text
from app.database import engine, Base
from app.models.common_code_master import CommonCodeMaster
from app.models.common_code_detail import CommonCodeDetail

def recreate_table():
    """테이블 삭제 후 재생성"""
    with engine.connect() as conn:
        # 기존 테이블 삭제 (외래키 때문에 순서 중요)
        try:
            conn.execute(text("DROP TABLE IF EXISTS common_code_detail CASCADE"))
            conn.execute(text("DROP TABLE IF EXISTS common_code_master CASCADE"))
            conn.commit()
            print("[OK] 기존 테이블 삭제 완료")
        except Exception as e:
            print(f"테이블 삭제 중 오류 (무시 가능): {e}")
            conn.rollback()
        
        # 새 테이블 생성
        try:
            Base.metadata.create_all(bind=engine, tables=[CommonCodeMaster.__table__, CommonCodeDetail.__table__])
            print("[OK] 새 테이블 생성 완료")
            print("\n테이블 구조:")
            print("common_code_master:")
            print("  - id: Integer (PK)")
            print("  - code: String(50) UNIQUE - 코드")
            print("  - code_name: String(200) - 코드명")
            print("  - remark: String(500) - 비고")
            print("\ncommon_code_detail:")
            print("  - id: Integer (PK)")
            print("  - master_id: Integer FK -> common_code_master.id")
            print("  - detail_code: String(50) - 상세코드")
            print("  - detail_code_name: String(200) - 상세코드명")
        except Exception as e:
            print(f"테이블 생성 중 오류: {e}")
            raise

if __name__ == "__main__":
    import sys
    import os
    
    # Windows에서 인코딩 설정
    if sys.platform == 'win32':
        os.system('chcp 65001 > nul')
    
    print("=" * 50)
    print("공통코드 테이블 재생성")
    print("=" * 50)
    print("\n경고: 이 작업은 모든 데이터를 삭제합니다!")
    
    # 명령줄 인자로 자동 실행 옵션 제공
    if len(sys.argv) > 1 and sys.argv[1] == '--yes':
        response = 'yes'
    else:
        response = input("\n계속하시겠습니까? (yes/no): ")
    
    if response.lower() == 'yes':
        recreate_table()
        print("\n작업 완료!")
    else:
        print("\n작업이 취소되었습니다.")

