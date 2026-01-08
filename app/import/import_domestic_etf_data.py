"""
pykrx를 사용하여 국내 ETF 데이터를 가져와서 데이터베이스에 저장하는 스크립트
"""
from pykrx import stock
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import domestic_etf
from datetime import datetime
import sys

def import_etf_data(date_str: str = None):
    """
    pykrx를 사용하여 ETF 데이터를 가져와서 저장
    
    Args:
        date_str: 날짜 문자열 (YYYYMMDD 형식). None이면 오늘 날짜 사용
    """
    if date_str is None:
        # 오늘 날짜를 YYYYMMDD 형식으로 변환
        today = datetime.now()
        date_str = today.strftime("%Y%m%d")
    
    print(f"[INFO] {date_str} 기준으로 ETF 데이터를 가져옵니다...")
    
    try:
        # ETF 티커 리스트 가져오기
        tickers = stock.get_etf_ticker_list(date_str)
        print(f"[OK] {len(tickers)}개의 ETF 티커를 찾았습니다.")
        
        # 데이터베이스 세션 생성
        db: Session = SessionLocal()
        
        etf_list = []
        success_count = 0
        error_count = 0
        
        for ticker in tickers:
            try:
                # 종목명 가져오기
                name = stock.get_etf_ticker_name(ticker)
                
                etf_data = {
                    'ticker': ticker,
                    'name': name
                }
                etf_list.append(etf_data)
                
                # 진행 상황 출력 (100개마다)
                if len(etf_list) % 100 == 0:
                    print(f"  진행 중... {len(etf_list)}개 처리됨")
                    
            except Exception as e:
                print(f"  [WARN] 티커 {ticker} 처리 중 오류: {e}")
                error_count += 1
                continue
        
        # 일괄 저장
        if etf_list:
            print(f"\n[INFO] {len(etf_list)}개의 ETF 데이터를 데이터베이스에 저장합니다...")
            created_count = domestic_etf.bulk_create_domestic_etfs(db, etf_list)
            print(f"[OK] {created_count}개의 새로운 ETF가 저장되었습니다.")
            print(f"   (이미 존재하는 ETF는 건너뛰었습니다.)")
        
        if error_count > 0:
            print(f"[WARN] {error_count}개의 티커 처리 중 오류가 발생했습니다.")
        
        db.close()
        print("\n[OK] 작업이 완료되었습니다!")
        
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # 명령줄 인자로 날짜를 받을 수 있음 (예: python import_domestic_etf_data.py 20251218)
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    import_etf_data(date_str)

