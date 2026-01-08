"""
국내 ETF 배당 정보를 seibro.or.kr에서 스크래핑하는 스크립트
"""
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
# 현재 파일: backend-fastapi/app/scrapers/domestic_etfs_dividend.py
# app 모듈을 import하려면 backend-fastapi/ 디렉토리가 경로에 있어야 함
current_dir = os.path.dirname(os.path.abspath(__file__))  # backend-fastapi/app/scrapers
app_dir = os.path.dirname(current_dir)  # backend-fastapi/app
backend_dir = os.path.dirname(app_dir)  # backend-fastapi

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import logging
from datetime import datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import domestic_etfs, domestic_etfs_dividend

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def scrape_domestic_etf_dividend(ticker: str = "494300", save_to_db: bool = True):
    """
    seibro.or.kr에서 국내 ETF 배당 정보를 스크래핑
    
    Args:
        ticker: ETF 티커 (기본값: 494300)
        save_to_db: 데이터베이스에 저장할지 여부 (기본값: True)
    
    Returns:
        pandas.DataFrame: 스크래핑한 데이터프레임
    """
    url = "https://seibro.or.kr/websquare/control.jsp?w2xPath=/IPORTAL/user/etf/BIP_CNTS06030V.xml&menuNo=179"
    
    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 헤드리스 모드 (브라우저 창 숨김)
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    try:
        # Chrome 드라이버 초기화 (webdriver-manager 사용)
        logger.info("Chrome 드라이버를 초기화합니다...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 페이지 접속
        logger.info(f"페이지 접속 중: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # INPUT_SN2 요소 찾기 및 입력
        logger.info(f"티커 입력 중: {ticker}")
        wait = WebDriverWait(driver, 10)
        input_element = wait.until(
            EC.presence_of_element_located((By.ID, "INPUT_SN2"))
        )
        
        # 기존 값 클리어 후 입력
        input_element.clear()
        input_element.send_keys(ticker)
        
        # 엔터 키 입력
        input_element.send_keys(Keys.RETURN)
        
        # 검색 결과 로딩 대기
        logger.info("검색 결과 로딩 대기 중...")
        time.sleep(3)
        
        # iframe으로 전환
        logger.info("iframe으로 전환 중...")
        iframe_element = wait.until(
            EC.presence_of_element_located((By.ID, "iframeEtfnm"))
        )
        driver.switch_to.frame(iframe_element)
        logger.info("iframe으로 전환 완료")
        
        # contentsList의 첫 번째 li > a 클릭
        logger.info("contentsList의 첫 번째 링크 클릭 중...")
        contents_list = wait.until(
            EC.presence_of_element_located((By.ID, "contentsList"))
        )
        
        # 첫 번째 링크 확인
        first_link = contents_list.find_element(By.CSS_SELECTOR, "li:first-child > a")
        link_text = first_link.text if first_link.text else first_link.get_attribute("href")
        logger.info(f"첫 번째 링크 정보: text={first_link.text}, href={first_link.get_attribute('href')}")
        
        # JavaScript로 클릭 시도 (일반 클릭이 안 될 수 있음)
        try:
            driver.execute_script("arguments[0].click();", first_link)
            logger.info("JavaScript로 첫 번째 링크 클릭 완료")
        except:
            first_link.click()
            logger.info("일반 클릭으로 첫 번째 링크 클릭 완료")
        
        # 첫 번째 링크 클릭 후 대기
        logger.info("페이지 로딩 대기 중...")
        time.sleep(3)
        
        # 메인 컨텍스트에서 조회 버튼 찾기
        logger.info("조회 버튼 검색 중...")
        search_button = None
        button_found_context = None
        
        try:
            driver.switch_to.default_content()
            search_button = driver.find_element(By.ID, "group125")
            logger.info("메인 컨텍스트에서 조회 버튼을 찾았습니다.")
            button_found_context = "main"
        except:
            logger.warning("메인 컨텍스트에서 조회 버튼을 찾지 못했습니다.")
        
        if not search_button:
            raise Exception("조회 버튼(group125)을 찾을 수 없습니다.")
        
        # 조회 버튼 클릭
        logger.info("조회 버튼 클릭 중...")
        if button_found_context == "main":
            driver.switch_to.default_content()
            search_button = driver.find_element(By.ID, "group125")
        
        driver.execute_script("arguments[0].click();", search_button)
        logger.info("조회 버튼 클릭 완료")
        
        # 그리드 데이터 로딩 대기
        logger.info("그리드 데이터 로딩 대기 중...")
        time.sleep(3)
        
        # grid1 요소 찾기 (메인 컨텍스트)
        driver.switch_to.default_content()
        grid_element = wait.until(
            EC.presence_of_element_located((By.ID, "grid1"))
        )
        
        # 그리드 내부의 테이블 데이터 추출
        logger.info("그리드 데이터 추출 중...")
        
        # grid1 내부의 테이블 행 찾기
        rows = grid_element.find_elements(By.TAG_NAME, "tr")
        
        if not rows:
            logger.warning("그리드에서 데이터를 찾을 수 없습니다.")
            return pd.DataFrame()
        
        # 테이블 헤더 추출
        headers = []
        header_row = rows[0] if rows else None
        if header_row:
            header_cells = header_row.find_elements(By.TAG_NAME, "th")
            if not header_cells:
                header_cells = header_row.find_elements(By.TAG_NAME, "td")
            headers = [cell.text.strip() for cell in header_cells]
        
        # 데이터 행 추출
        data_rows = []
        start_idx = 1 if header_row else 0  # 헤더가 있으면 1부터 시작
        
        for row in rows[start_idx:]:
            cells = row.find_elements(By.TAG_NAME, "td")
            if cells:
                row_data = [cell.text.strip() for cell in cells]
                if any(row_data):  # 빈 행이 아닌 경우만 추가
                    data_rows.append(row_data)
        
        # 헤더가 없는 경우 기본 헤더 생성
        if not headers and data_rows:
            headers = [f"컬럼{i+1}" for i in range(len(data_rows[0]))]
        
        # 데이터프레임 생성
        if data_rows:
            df = pd.DataFrame(data_rows, columns=headers[:len(data_rows[0])])
            logger.info(f"데이터 추출 완료: {len(df)}개 행, {len(df.columns)}개 컬럼")
            logger.info(df.head())
            # 데이터베이스에 저장
            if save_to_db:
                db: Session = None
                try:
                    db = SessionLocal()
                    # ETF 정보 조회
                    etf = domestic_etfs.get_domestic_etf_by_ticker(db, ticker)
                    if not etf:
                        logger.warning(f"티커 {ticker}에 해당하는 ETF를 찾을 수 없습니다.")
                        return df
                    
                    # 데이터프레임을 데이터베이스 형식으로 변환
                    dividends_to_save = []
                    for _, row in df.iterrows():
                        dividend_data = {
                            'etf_id': etf.id,
                            'record_date': row[4],  # 기준일자 (필수)
                            'payment_date': row[5],
                            'dividend_amt': row[7],
                        }

                        # record_date가 필수이므로 None이면 스킵
                        if dividend_data['record_date']:
                            dividends_to_save.append(dividend_data)
                    
                    # 일괄 upsert
                    if dividends_to_save:
                        result = domestic_etfs_dividend.bulk_upsert_domestic_etf_dividends(db, dividends_to_save)
                        logger.info(f"{result['created']}개의 배당 정보를 생성하고 {result['updated']}개의 배당 정보를 업데이트했습니다.")
                    else:
                        logger.warning("저장할 배당 정보가 없습니다.")
                except Exception as e:
                    logger.error(f"데이터베이스 저장 중 오류 발생: {e}")
                    import traceback
                    traceback.print_exc()
                    if db:
                        try:
                            db.rollback()
                        except:
                            pass
                finally:
                    if db:
                        try:
                            db.close()
                        except:
                            pass
            
            return df
        else:
            logger.warning("추출된 데이터가 없습니다.")
            return pd.DataFrame()
            
    except Exception as e:
        logger.error(f"스크래핑 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return pd.DataFrame()
    
    finally:
        if driver:
            try:
                # iframe에서 나오기 (에러 발생 시 대비)
                driver.switch_to.default_content()
            except:
                pass
            driver.quit()
            logger.info("브라우저를 종료했습니다.")


def scrape_all_high_dividend_etfs(etf_type: str = "high_dividend", ticker: str = None):
    """
    high_dividend 타입의 모든 ETF 배당 정보를 스크래핑
    
    Args:
        etf_type: ETF 유형 (기본값: "high_dividend"). None이면 ticker 파라미터 사용
        ticker: 특정 티커만 처리하고 싶을 때 사용 (기본값: None)
    """
    etf_list = []
    
    # ETF 리스트 조회 (세션을 빨리 닫기 위해 별도로 처리)
    db: Session = SessionLocal()
    try:
        # 특정 티커가 지정된 경우
        if ticker:
            logger.info(f"[INFO] 특정 티커 {ticker}만 처리합니다.")
            etf = domestic_etfs.get_domestic_etf_by_ticker(db, ticker)
            if not etf:
                logger.error(f"[ERROR] 티커 {ticker}에 해당하는 ETF를 찾을 수 없습니다.")
                return
            etf_list = [etf]
        else:
            # etf_type에 해당하는 모든 ETF 조회
            logger.info(f"[INFO] etf_type='{etf_type}'인 모든 ETF를 조회합니다...")
            etf_list = domestic_etfs.get_domestic_etfs(db, skip=0, limit=1000, etf_type=etf_type)
            
            if not etf_list:
                logger.warning(f"[WARN] etf_type='{etf_type}'인 ETF를 찾을 수 없습니다.")
                return
            
            logger.info(f"[OK] 총 {len(etf_list)}개의 ETF를 찾았습니다.")
    finally:
        # ETF 리스트 조회 후 바로 세션 닫기 (장시간 스크래핑 중 타임아웃 방지)
        db.close()
    
    # 각 ETF에 대해 배당 정보 스크래핑
    # scrape_domestic_etf_dividend 함수가 내부에서 자체 세션을 사용하므로
    # 여기서는 세션 없이 처리
    success_count = 0
    fail_count = 0
    
    for idx, etf in enumerate(etf_list, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"[{idx}/{len(etf_list)}] 처리 중: {etf.ticker} - {etf.name}")
        logger.info(f"{'='*60}")
        
        try:
            df = scrape_domestic_etf_dividend(etf.ticker, save_to_db=True)
            if not df.empty:
                logger.info(f"[OK] {etf.ticker} 배당 정보 스크래핑 완료: {len(df)}개 행")
                success_count += 1
            else:
                logger.warning(f"[WARN] {etf.ticker} 배당 정보를 찾을 수 없습니다.")
                fail_count += 1
        except Exception as e:
            logger.error(f"[ERROR] {etf.ticker} 처리 실패: {e}")
            import traceback
            traceback.print_exc()
            fail_count += 1
            continue
    
    # 결과 요약
    logger.info(f"\n{'='*60}")
    logger.info("[결과 요약]")
    logger.info(f"{'='*60}")
    logger.info(f"총 처리 대상: {len(etf_list)}개")
    logger.info(f"성공: {success_count}개")
    logger.info(f"실패: {fail_count}개")
    logger.info(f"{'='*60}\n")


if __name__ == "__main__":
    # 명령줄 인자 처리
    # 예: python domestic_etfs_dividend.py                    # high_dividend 모든 종목
    # 예: python domestic_etfs_dividend.py high_dividend      # high_dividend 모든 종목
    # 예: python domestic_etfs_dividend.py --ticker 494300    # 특정 티커만
    
    etf_type = "high_dividend"
    ticker = None
    
    # 간단한 인자 파싱
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ticker" or sys.argv[1] == "-t":
            # 티커 모드
            if len(sys.argv) > 2:
                ticker = sys.argv[2]
            else:
                logger.error("[ERROR] --ticker 옵션 사용 시 티커를 지정해주세요.")
                sys.exit(1)
        else:
            # 첫 번째 인자는 etf_type
            etf_type = sys.argv[1]
    
    if ticker:
        logger.info(f"[INFO] 특정 티커 모드: {ticker}")
        scrape_all_high_dividend_etfs(etf_type=None, ticker=ticker)
    else:
        logger.info(f"[INFO] etf_type='{etf_type}'인 모든 종목 처리")
        scrape_all_high_dividend_etfs(etf_type=etf_type)

