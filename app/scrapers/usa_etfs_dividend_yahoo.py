"""
yfinance를 사용하여 Yahoo Finance에서 미국 ETF 배당 정보를 가져와서 데이터베이스에 저장하는 스크립트
"""
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))  # backend-fastapi/app/scrapers
app_dir = os.path.dirname(current_dir)  # backend-fastapi/app
backend_dir = os.path.dirname(app_dir)  # backend-fastapi

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

import time
import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import usa_etfs, usa_etfs_dividend
import pandas as pd

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_usa_etf_dividend_yahoo(ticker: str = "QYLD", save_to_db: bool = True, years: list = [2024, 2025]):
    """
    Yahoo Finance (yfinance)에서 미국 ETF 배당 정보를 가져오기
    
    Args:
        ticker: ETF 티커 (기본값: QYLD)
        save_to_db: 데이터베이스에 저장할지 여부 (기본값: True)
        years: 가져올 연도 리스트 (기본값: [2024, 2025])
    
    Returns:
        list: 스크래핑한 배당 데이터 리스트
    """
    try:
        import yfinance as yf
    except ImportError:
        logger.error("yfinance가 설치되지 않았습니다. 'pip install yfinance' 명령으로 설치해주세요.")
        return []
    
    db: Session = None
    
    try:
        # 데이터베이스 세션 생성
        if save_to_db:
            db = SessionLocal()
            etf = usa_etfs.get_usa_etf_by_ticker(db, ticker)
            if not etf:
                logger.error(f"티커 {ticker}에 해당하는 ETF를 데이터베이스에서 찾을 수 없습니다.")
                return []
        
        logger.info(f"Yahoo Finance에서 {ticker} 배당 데이터를 가져오는 중...")
        
        # yfinance로 티커 정보 가져오기
        t = yf.Ticker(ticker)
        
        # 배당 데이터 가져오기 (dividends 속성은 Series로 날짜(index)와 배당금액(value) 반환)
        dividends = t.dividends

        logger.info(f"dividends: {dividends}")
        if dividends is None or dividends.empty:
            logger.warning(f"{ticker} 티커의 배당 데이터를 찾을 수 없습니다.")
            return []
        
        logger.info(f"{len(dividends)}개의 배당 데이터를 찾았습니다.")
        
        # 데이터프레임으로 변환
        df = dividends.reset_index()
        df.columns = ['Date', 'Dividend']
        
        # 연도 필터링
        if years:
            df = df[df['Date'].dt.year.isin(years)]
            logger.info(f"필터링 후 {len(df)}개의 배당 데이터 ({years}년)")
        
        if df.empty:
            logger.warning(f"필터링 후 배당 데이터가 없습니다.")
            return []
        
        # 데이터 변환
        # yfinance.dividends가 반환하는 날짜를 record_date로 저장
        dividends_data = []
        for _, row in df.iterrows():
            record_date = row['Date'].date()  # yfinance의 날짜를 record_date로 사용
            dividend_amount = Decimal(str(row['Dividend']))
            
            dividend_info = {
                'record_date': record_date,
                'dividend_amt': dividend_amount
            }
            
            dividends_data.append(dividend_info)
            logger.debug(f"배당 데이터: record_date={record_date}, amount=${dividend_amount}")
        
        logger.info(f"총 {len(dividends_data)}개의 배당 데이터를 추출했습니다.")
        
        # 데이터베이스에 저장
        if save_to_db and db and etf and dividends_data:
            try:
                dividends_to_save = []
                for div_data in dividends_data:
                    dividend_data = {
                        'etf_id': etf.id,
                        'record_date': div_data['record_date'],
                        'dividend_amt': div_data['dividend_amt']
                    }
                    dividends_to_save.append(dividend_data)
                
                if dividends_to_save:
                    result = usa_etfs_dividend.bulk_upsert_usa_etf_dividends(db, dividends_to_save)
                    logger.info(f"{result['created']}개의 배당 정보를 생성하고 {result['updated']}개의 배당 정보를 업데이트했습니다.")
            except Exception as e:
                logger.error(f"데이터베이스 저장 중 오류 발생: {e}")
                import traceback
                traceback.print_exc()
                if db:
                    db.rollback()
        
        return dividends_data
        
    except Exception as e:
        logger.error(f"배당 데이터 가져오기 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        if db:
            db.rollback()
        return []
    finally:
        if db:
            db.close()


def scrape_all_usa_etf_dividends_yahoo(ticker: str = None, years: list = [2024, 2025]):
    """
    모든 미국 ETF 또는 특정 티커의 배당 정보를 Yahoo Finance에서 가져오기
    
    Args:
        ticker: 특정 티커만 처리 (None이면 모든 ETF 처리)
        years: 가져올 연도 리스트 (기본값: [2024, 2025])
    """
    db_session_for_etf_list: Session = SessionLocal()
    try:
        if ticker:
            etf = usa_etfs.get_usa_etf_by_ticker(db_session_for_etf_list, ticker)
            if not etf:
                logger.error(f"[ERROR] 티커 {ticker}에 해당하는 ETF를 찾을 수 없습니다.")
                return
            etf_list = [etf]
        else:
            logger.info(f"[INFO] 모든 미국 ETF를 조회합니다...")
            etf_list = usa_etfs.get_usa_etfs(db_session_for_etf_list, skip=0, limit=1000)
            if not etf_list:
                logger.warning(f"[WARN] 등록된 ETF를 찾을 수 없습니다.")
                return
            logger.info(f"[OK] 총 {len(etf_list)}개의 ETF를 찾았습니다.")
    finally:
        db_session_for_etf_list.close()
    
    success_count = 0
    fail_count = 0
    
    for idx, etf in enumerate(etf_list, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"[{idx}/{len(etf_list)}] 처리 중: {etf.ticker} - {etf.name}")
        logger.info(f"{'='*60}")
        try:
            dividends = scrape_usa_etf_dividend_yahoo(etf.ticker, save_to_db=True, years=years)
            if dividends:
                logger.info(f"[OK] {etf.ticker} 배당 정보 스크래핑 완료: {len(dividends)}개")
                success_count += 1
            else:
                logger.warning(f"[WARN] {etf.ticker} 배당 정보를 찾을 수 없습니다.")
                fail_count += 1
            
            # API 요청 제한을 피하기 위한 대기 시간
            time.sleep(1)
            
        except Exception as e:
            logger.error(f"[ERROR] {etf.ticker} 처리 실패: {e}")
            fail_count += 1
            continue
    
    logger.info(f"\n{'='*60}")
    logger.info("[결과 요약]")
    logger.info(f"{'='*60}")
    logger.info(f"총 처리 대상: {len(etf_list)}개")
    logger.info(f"성공: {success_count}개")
    logger.info(f"실패: {fail_count}개")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    # 기본값: QYLD 티커의 2024, 2025 데이터
    import sys
    
    ticker = None
    if len(sys.argv) > 1:
        ticker = sys.argv[1]
    
    scrape_all_usa_etf_dividends_yahoo(ticker=ticker, years=[2024, 2025])

