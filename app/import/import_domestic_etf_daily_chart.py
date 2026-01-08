"""
FinanceDataReader를 사용하여 국내 ETF 일봉 차트 데이터를 가져와서 데이터베이스에 저장하는 스크립트
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
# 현재 파일: backend-fastapi/app/import/import_domestic_etf_daily_chart.py
# app 모듈을 import하려면 backend-fastapi/ 디렉토리가 경로에 있어야 함
current_dir = os.path.dirname(os.path.abspath(__file__))  # backend-fastapi/app/import
app_dir = os.path.dirname(current_dir)  # backend-fastapi/app
backend_dir = os.path.dirname(app_dir)  # backend-fastapi

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import domestic_etfs, domestic_etfs_daily_chart
import pandas as pd

def import_single_etf_chart(db: Session, etf, weeks: int, fdr):
    """
    단일 ETF의 차트 데이터를 가져와서 저장하는 내부 함수
    
    Args:
        db: 데이터베이스 세션
        etf: ETF 모델 객체
        weeks: 가져올 주 수
        fdr: FinanceDataReader 모듈
    """
    ticker = etf.ticker
    print(f"\n[INFO] {ticker} ({etf.name}) 티커의 {weeks}주 일봉 데이터를 가져옵니다...")
    
    # 날짜 계산 (현재로부터 weeks주 전)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(weeks=weeks)
    
    print(f"[INFO] 기간: {start_date} ~ {end_date}")
    
    try:
        # FinanceDataReader로 데이터 가져오기
        # NAVER:티커 형식으로 사용
        symbol = f"NAVER:{ticker}"
        print(f"[INFO] 데이터 조회 중: {symbol}")
        
        df = fdr.DataReader(symbol, start_date, end_date)
        
        if df is None or df.empty:
            print(f"[WARN] {ticker} 티커의 데이터를 가져올 수 없습니다.")
            return
        
        print(f"[OK] {len(df)}개의 일봉 데이터를 가져왔습니다.")
        
        # DataFrame을 데이터베이스 형식으로 변환
        charts_to_save = []
        
        for date_idx, row in df.iterrows():
            # date_idx가 DatetimeIndex인 경우
            if isinstance(date_idx, pd.Timestamp):
                date = date_idx.date()
            elif isinstance(date_idx, datetime):
                date = date_idx.date()
            else:
                try:
                    date = pd.to_datetime(date_idx).date()
                except:
                    print(f"[WARN] 날짜 변환 실패: {date_idx}")
                    continue
            
            # 컬럼명 확인 및 매핑
            # FinanceDataReader는 보통 Open, High, Low, Close, Volume 컬럼을 반환
            open_price = None
            high_price = None
            low_price = None
            close_price = None
            volume = None
            
            # 가능한 컬럼명들 확인
            for col in df.columns:
                col_lower = str(col).lower()
                value = row[col]
                
                if pd.isna(value):
                    continue
                
                if 'open' in col_lower:
                    open_price = int(float(value)) if pd.notna(value) else None
                elif 'high' in col_lower:
                    high_price = int(float(value)) if pd.notna(value) else None
                elif 'low' in col_lower:
                    low_price = int(float(value)) if pd.notna(value) else None
                elif 'close' in col_lower:
                    close_price = int(float(value)) if pd.notna(value) else None
                elif 'volume' in col_lower or '거래량' in col:
                    volume = int(value) if pd.notna(value) else None
            
            # 필수 필드 확인
            if not all([open_price is not None, high_price is not None, 
                       low_price is not None, close_price is not None, volume is not None]):
                print(f"[WARN] {date} 데이터에 필수 필드가 없습니다. 스킵합니다.")
                continue
            
            chart_data = {
                'etf_id': etf.id,
                'date': date,
                'open': open_price,
                'high': high_price,
                'low': low_price,
                'close': close_price,
                'volume': volume
            }
            
            charts_to_save.append(chart_data)
        
        # 일괄 upsert
        if charts_to_save:
            print(f"[INFO] {len(charts_to_save)}개의 일봉 데이터를 데이터베이스에 저장합니다...")
            result = domestic_etfs_daily_chart.bulk_upsert_domestic_etf_daily_charts(db, charts_to_save)
            print(f"[OK] {result['created']}개의 새로운 데이터를 생성하고 {result['updated']}개의 데이터를 업데이트했습니다.")
        else:
            print("[WARN] 저장할 데이터가 없습니다.")
            
    except Exception as e:
        print(f"[ERROR] {ticker} 티커 처리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


def import_domestic_etf_daily_chart(etf_type: str = "high_dividend", weeks: int = 52, ticker: str = None):
    """
    FinanceDataReader를 사용하여 국내 ETF 일봉 차트 데이터를 가져와서 저장
    
    Args:
        etf_type: ETF 유형 (기본값: "high_dividend"). None이면 ticker 파라미터 사용
        weeks: 가져올 주 수 (기본값: 52주)
        ticker: 특정 티커만 처리하고 싶을 때 사용 (기본값: None)
    """
    try:
        import FinanceDataReader as fdr
        
        # 데이터베이스 세션 생성
        db: Session = SessionLocal()
        
        try:
            etf_list = []
            
            # 특정 티커가 지정된 경우
            if ticker:
                print(f"[INFO] 특정 티커 {ticker}만 처리합니다.")
                etf = domestic_etfs.get_domestic_etf_by_ticker(db, ticker)
                if not etf:
                    print(f"[ERROR] 티커 {ticker}에 해당하는 ETF를 찾을 수 없습니다.")
                    return
                etf_list = [etf]
            else:
                # etf_type에 해당하는 모든 ETF 조회
                print(f"[INFO] etf_type='{etf_type}'인 모든 ETF를 조회합니다...")
                etf_list = domestic_etfs.get_domestic_etfs(db, skip=0, limit=1000, etf_type=etf_type)
                
                if not etf_list:
                    print(f"[WARN] etf_type='{etf_type}'인 ETF를 찾을 수 없습니다.")
                    return
                
                print(f"[OK] 총 {len(etf_list)}개의 ETF를 찾았습니다.")
            
            # 각 ETF에 대해 차트 데이터 가져오기
            total_created = 0
            total_updated = 0
            success_count = 0
            fail_count = 0
            
            for idx, etf in enumerate(etf_list, 1):
                print(f"\n{'='*60}")
                print(f"[{idx}/{len(etf_list)}] 처리 중: {etf.ticker} - {etf.name}")
                print(f"{'='*60}")
                
                try:
                    import_single_etf_chart(db, etf, weeks, fdr)
                    success_count += 1
                except Exception as e:
                    print(f"[ERROR] {etf.ticker} 처리 실패: {e}")
                    fail_count += 1
                    continue
            
            # 결과 요약
            print(f"\n{'='*60}")
            print("[결과 요약]")
            print(f"{'='*60}")
            print(f"총 처리 대상: {len(etf_list)}개")
            print(f"성공: {success_count}개")
            print(f"실패: {fail_count}개")
            print(f"{'='*60}\n")
            
        except Exception as e:
            db.rollback()
            print(f"[ERROR] 데이터베이스 처리 중 오류 발생: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            db.close()
        
        print("\n[OK] 모든 작업이 완료되었습니다!")
        
    except ImportError:
        print("[ERROR] FinanceDataReader가 설치되지 않았습니다.")
        print("[INFO] 'pip install FinanceDataReader' 명령으로 설치해주세요.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # 명령줄 인자 처리
    # 예: python import_domestic_etf_daily_chart.py                    # high_dividend 모든 종목, 52주
    # 예: python import_domestic_etf_daily_chart.py high_dividend 52   # high_dividend 모든 종목, 52주
    # 예: python import_domestic_etf_daily_chart.py --ticker 494300    # 특정 티커만, 52주
    # 예: python import_domestic_etf_daily_chart.py --ticker 494300 26 # 특정 티커만, 26주
    
    etf_type = "high_dividend"
    weeks = 52
    ticker = None
    
    # 간단한 인자 파싱
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ticker" or sys.argv[1] == "-t":
            # 티커 모드
            if len(sys.argv) > 2:
                ticker = sys.argv[2]
                if len(sys.argv) > 3:
                    weeks = int(sys.argv[3])
            else:
                print("[ERROR] --ticker 옵션 사용 시 티커를 지정해주세요.")
                sys.exit(1)
        else:
            # 첫 번째 인자는 etf_type 또는 weeks
            try:
                # 숫자면 weeks로 간주
                weeks = int(sys.argv[1])
            except ValueError:
                # 문자열이면 etf_type으로 간주
                etf_type = sys.argv[1]
            
            # 두 번째 인자는 weeks
            if len(sys.argv) > 2:
                try:
                    weeks = int(sys.argv[2])
                except ValueError:
                    pass
    
    if ticker:
        print(f"[INFO] 특정 티커 모드: {ticker}, {weeks}주")
        import_domestic_etf_daily_chart(etf_type=None, weeks=weeks, ticker=ticker)
    else:
        print(f"[INFO] etf_type='{etf_type}'인 모든 종목 처리, {weeks}주")
        import_domestic_etf_daily_chart(etf_type=etf_type, weeks=weeks)

