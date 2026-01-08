"""
네이버 금융에서 USD/KRW 환율 데이터를 스크래핑하여 데이터베이스에 저장하는 스크립트
"""
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
# 현재 파일: backend-fastapi/app/scrapers/usd_krw_exchange.py
# app 모듈을 import하려면 backend-fastapi/ 디렉토리가 경로에 있어야 함
current_dir = os.path.dirname(os.path.abspath(__file__))  # backend-fastapi/app/scrapers
app_dir = os.path.dirname(current_dir)  # backend-fastapi/app
backend_dir = os.path.dirname(app_dir)  # backend-fastapi

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from datetime import datetime, timedelta, date
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

import requests
from bs4 import BeautifulSoup
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import usd_krw_exchange
from app.schemas.usd_krw_exchange import USDKRWExchangeCreate
from decimal import Decimal
import time
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def parse_korean_date(date_str: str) -> date:
    """
    한국어 날짜 문자열을 date 객체로 변환
    예: "2026.01.05" -> date(2026, 1, 5)
    """
    try:
        # 공백 제거 후 점(.)으로 분리
        parts = date_str.strip().split('.')
        if len(parts) == 3:
            year = int(parts[0])
            month = int(parts[1])
            day = int(parts[2])
            return date(year, month, day)
    except Exception as e:
        logger.error(f"날짜 파싱 실패: {date_str}, 오류: {e}")
    return None

def parse_exchange_rate(rate_str: str) -> Decimal:
    """
    환율 문자열을 Decimal로 변환
    예: "1,448.20" -> Decimal("1448.20")
    """
    try:
        # 쉼표 제거 후 Decimal로 변환
        cleaned = rate_str.strip().replace(',', '')
        return Decimal(cleaned)
    except Exception as e:
        logger.error(f"환율 파싱 실패: {rate_str}, 오류: {e}")
    return None

def scrape_naver_exchange_rate(page: int = 1, target_date: date = None) -> list:
    """
    네이버 금융에서 USD/KRW 환율 데이터를 스크래핑
    
    Args:
        page: 페이지 번호 (기본값: 1)
        target_date: 이 날짜 이전 데이터를 가져올지 결정 (None이면 제한 없음)
    
    Returns:
        [(date, exchange_rate), ...] 리스트
    """
    url = f"https://finance.naver.com/marketindex/exchangeDailyQuote.naver?marketindexCd=FX_USDKRW&page={page}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'euc-kr'  # 네이버는 euc-kr 인코딩 사용
        
        if response.status_code != 200:
            logger.error(f"페이지 {page} 요청 실패: HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # 테이블 찾기
        table = soup.find('table', class_='tbl_exchange')
        if not table:
            logger.error(f"페이지 {page}에서 테이블을 찾을 수 없습니다.")
            return []
        
        # tbody에서 행들 찾기
        tbody = table.find('tbody')
        if not tbody:
            logger.error(f"페이지 {page}에서 tbody를 찾을 수 없습니다.")
            return []
        
        rows = tbody.find_all('tr')
        exchange_data = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 2:
                continue
            
            # 첫 번째 열: 날짜
            date_cell = cols[0].get_text(strip=True)
            exchange_date = parse_korean_date(date_cell)
            
            if not exchange_date:
                continue
            
            # target_date가 설정되어 있고 현재 날짜가 target_date 이전이면 중지
            if target_date and exchange_date < target_date:
                return exchange_data  # 더 이상 진행하지 않음
            
            # 두 번째 열: 매매기준율 (종가)
            rate_cell = cols[1].get_text(strip=True)
            exchange_rate = parse_exchange_rate(rate_cell)
            
            if exchange_rate:
                exchange_data.append((exchange_date, exchange_rate))
        
        return exchange_data
    
    except Exception as e:
        logger.error(f"페이지 {page} 스크래핑 중 오류: {e}")
        return []

def scrape_all_exchange_rates(years: int = 2) -> list:
    """
    2년치 환율 데이터를 모든 페이지에서 스크래핑
    
    Args:
        years: 가져올 년수 (기본값: 2)
    
    Returns:
        [(date, exchange_rate), ...] 리스트
    """
    # 목표 날짜 계산 (현재로부터 years년 전)
    target_date = (datetime.now() - timedelta(days=years * 365)).date()
    
    logger.info(f"{years}년치 USD/KRW 환율 데이터를 스크래핑합니다...")
    logger.info(f"목표 날짜: {target_date} 이후 데이터를 수집합니다.")
    
    all_data = []
    page = 1
    max_pages = 100  # 안전장치: 최대 100페이지까지만
    
    while page <= max_pages:
        logger.info(f"페이지 {page} 스크래핑 중...")
        
        page_data = scrape_naver_exchange_rate(page, target_date)
        
        if not page_data:
            logger.info(f"페이지 {page}에 데이터가 없습니다. 스크래핑 종료.")
            break
        
        all_data.extend(page_data)
        
        # 마지막 날짜가 target_date 이전이면 더 이상 진행하지 않음
        if page_data:
            last_date = page_data[-1][0]
            if last_date < target_date:
                logger.info(f"목표 날짜({target_date})에 도달했습니다. 스크래핑 종료.")
                break
        
        logger.info(f"페이지 {page} 완료: {len(page_data)}개 레코드 (총 {len(all_data)}개)")
        
        page += 1
        time.sleep(0.5)  # 서버 부하를 줄이기 위한 대기
    
    # 날짜 기준으로 정렬 (최신순)
    all_data.sort(key=lambda x: x[0], reverse=True)
    
    logger.info(f"총 {len(all_data)}개의 환율 데이터를 수집했습니다.")
    return all_data

def scrape_and_save_usd_krw_exchange(years: int = 2):
    """
    네이버 금융에서 USD/KRW 환율 데이터를 스크래핑하여 데이터베이스에 저장
    
    Args:
        years: 가져올 년수 (기본값: 2)
    """
    db: Session = SessionLocal()
    
    try:
        # 스크래핑
        exchange_data = scrape_all_exchange_rates(years)
        
        if not exchange_data:
            logger.warning("수집된 데이터가 없습니다.")
            return
        
        # 스키마로 변환
        exchanges = []
        for exchange_date, exchange_rate in exchange_data:
            exchange_create = USDKRWExchangeCreate(
                date=exchange_date,
                exchange_rate=exchange_rate
            )
            exchanges.append(exchange_create)
        
        logger.info(f"데이터베이스에 저장 중... ({len(exchanges)}개 레코드)")
        
        # 일괄 upsert
        result_count = usd_krw_exchange.bulk_upsert_usd_krw_exchanges(db, exchanges)
        
        logger.info("작업 완료!")
        logger.info(f"처리된 레코드: {result_count}개")
        
    except Exception as e:
        logger.error(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    scrape_and_save_usd_krw_exchange(years=2)

