"""
yfinance를 사용하여 미국 ETF 일봉 차트 데이터를 가져와서 데이터베이스에 저장하는 스크립트
"""
import os
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
# 현재 파일: backend-fastapi/app/import/import_usa_etf_daily_chart.py
# app 모듈을 import하려면 backend-fastapi/ 디렉토리가 경로에 있어야 함
current_dir = os.path.dirname(os.path.abspath(__file__))  # backend-fastapi/app/import
app_dir = os.path.dirname(current_dir)  # backend-fastapi/app
backend_dir = os.path.dirname(app_dir)  # backend-fastapi

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import usa_etfs, usa_etfs_daily_chart
import pandas as pd
from decimal import Decimal

def import_single_etf_chart(db: Session, etf, period: str = '2y', interval: str = '1d'):
    """
    단일 ETF의 차트 데이터를 가져와서 저장하는 내부 함수
    
    Args:
        db: 데이터베이스 세션
        etf: ETF 모델 객체
        period: 가져올 기간 (기본값: '2y' - 2년)
        interval: 데이터 간격 (기본값: '1d' - 일봉)
    """
    ticker = etf.ticker
    print(f"\n[INFO] {ticker} ({etf.name}) 티커의 {period} 일봉 데이터를 가져옵니다...")
    
    try:
        import yfinance as yf
        
        # yfinance로 데이터 가져오기
        print(f"[INFO] 데이터 조회 중: {ticker}")
        
        t = yf.Ticker(ticker)
        df = t.history(period=period, interval=interval)
        
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
            
            # yfinance는 Open, High, Low, Close, Volume 컬럼을 반환
            try:
                open_price = Decimal(str(row.get('Open', 0))) if pd.notna(row.get('Open')) else None
                high_price = Decimal(str(row.get('High', 0))) if pd.notna(row.get('High')) else None
                low_price = Decimal(str(row.get('Low', 0))) if pd.notna(row.get('Low')) else None
                close_price = Decimal(str(row.get('Close', 0))) if pd.notna(row.get('Close')) else None
                volume = int(row.get('Volume', 0)) if pd.notna(row.get('Volume')) else None
            except Exception as e:
                print(f"[WARN] {date} 데이터 파싱 실패: {e}")
                continue
            
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
            result = usa_etfs_daily_chart.bulk_upsert_usa_etf_daily_charts(db, charts_to_save)
            print(f"[OK] {result['created']}개의 새로운 데이터를 생성하고 {result['updated']}개의 데이터를 업데이트했습니다.")
        else:
            print("[WARN] 저장할 데이터가 없습니다.")
            
    except ImportError:
        print("[ERROR] yfinance가 설치되지 않았습니다.")
        print("[INFO] 'pip install yfinance' 명령으로 설치해주세요.")
        raise
    except Exception as e:
        print(f"[ERROR] {ticker} 티커 처리 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


def import_usa_etf_daily_chart(period: str = '2y', ticker: str = None):
    """
    yfinance를 사용하여 미국 ETF 일봉 차트 데이터를 가져와서 저장
    
    Args:
        period: 가져올 기간 (기본값: '2y' - 2년). yfinance period 옵션 사용 (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        ticker: 특정 티커만 처리하고 싶을 때 사용 (기본값: None이면 모든 ETF 처리)
    """
    try:
        import yfinance as yf
        
        # 데이터베이스 세션 생성
        db: Session = SessionLocal()
        
        try:
            etf_list = []
            
            # 특정 티커가 지정된 경우
            if ticker:
                print(f"[INFO] 특정 티커 {ticker}만 처리합니다.")
                etf = usa_etfs.get_usa_etf_by_ticker(db, ticker)
                if not etf:
                    print(f"[ERROR] 티커 {ticker}에 해당하는 ETF를 찾을 수 없습니다.")
                    return
                etf_list = [etf]
            else:
                # 모든 ETF 조회
                print(f"[INFO] 모든 미국 ETF를 조회합니다...")
                etf_list = usa_etfs.get_usa_etfs(db, skip=0, limit=1000)
                
                if not etf_list:
                    print(f"[WARN] 등록된 ETF를 찾을 수 없습니다.")
                    return
                
                print(f"[OK] 총 {len(etf_list)}개의 ETF를 찾았습니다.")
            
            # 각 ETF에 대해 차트 데이터 가져오기
            success_count = 0
            fail_count = 0
            
            for idx, etf in enumerate(etf_list, 1):
                print(f"\n{'='*60}")
                print(f"[{idx}/{len(etf_list)}] 처리 중: {etf.ticker} - {etf.name}")
                print(f"{'='*60}")
                
                try:
                    import_single_etf_chart(db, etf, period=period)
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
        print("[ERROR] yfinance가 설치되지 않았습니다.")
        print("[INFO] 'pip install yfinance' 명령으로 설치해주세요.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    # 명령줄 인자 처리
    # 예: python import_usa_etf_daily_chart.py                    # 모든 종목, 2년
    # 예: python import_usa_etf_daily_chart.py 1y                 # 모든 종목, 1년
    # 예: python import_usa_etf_daily_chart.py --ticker QYLD      # 특정 티커만, 2년
    # 예: python import_usa_etf_daily_chart.py --ticker QYLD 1y   # 특정 티커만, 1년
    
    period = "2y"
    ticker = None
    
    # 간단한 인자 파싱
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ticker" or sys.argv[1] == "-t":
            # 티커 모드
            if len(sys.argv) > 2:
                ticker = sys.argv[2]
                if len(sys.argv) > 3:
                    period = sys.argv[3]
            else:
                print("[ERROR] --ticker 옵션 사용 시 티커를 지정해주세요.")
                sys.exit(1)
        else:
            # 첫 번째 인자는 period
            period = sys.argv[1]
    
    if ticker:
        print(f"[INFO] 특정 티커 모드: {ticker}, 기간: {period}")
        import_usa_etf_daily_chart(period=period, ticker=ticker)
    else:
        print(f"[INFO] 모든 종목 처리, 기간: {period}")
        import_usa_etf_daily_chart(period=period)

