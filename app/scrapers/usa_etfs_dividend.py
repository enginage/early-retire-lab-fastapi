"""
Seeking Alpha에서 미국 ETF 배당 정보를 스크래핑하는 스크립트
"""
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))  # backend-fastapi/app/scrapers
app_dir = os.path.dirname(current_dir)  # backend-fastapi/app
backend_dir = os.path.dirname(app_dir)  # backend-fastapi

if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
import logging
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import usa_etfs, usa_etfs_dividend

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_date(date_str: str) -> date:
    """
    날짜 문자열을 date 객체로 변환
    여러 형식 지원:
    - "MM/DD/YYYY" 또는 "M/D/YYYY" (예: "12/30/2025", "1/8/2025")
    - "Jan 15, 2024" 또는 "Jan 15,2024"
    - "January 15, 2024"
    """
    if not date_str or not date_str.strip():
        return None
    
    date_str = date_str.strip()
    
    # 형식 1: MM/DD/YYYY 또는 M/D/YYYY (예: "12/30/2025", "1/8/2025")
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").date()
    except:
        pass
    
    # 형식 2: "Jan 15, 2024" 또는 "Jan 15,2024"
    try:
        # 쉼표 뒤 공백 정규화
        date_str_cleaned = date_str.replace(', ', ',').replace(',', ', ')
        return datetime.strptime(date_str_cleaned, "%b %d, %Y").date()
    except:
        pass
    
    # 형식 3: "January 15, 2024"
    try:
        date_str_cleaned = date_str.replace(', ', ',').replace(',', ', ')
        return datetime.strptime(date_str_cleaned, "%B %d, %Y").date()
    except Exception as e:
        logger.error(f"날짜 파싱 실패: {date_str}, 오류: {e}")
        return None


def parse_dividend_amount(amount_str: str) -> Decimal:
    """
    배당금액 문자열을 Decimal로 변환
    예: "$0.50" -> Decimal("0.50")
    """
    try:
        # $ 기호 제거 및 공백 제거
        cleaned = amount_str.strip().replace('$', '').replace(',', '').strip()
        return Decimal(cleaned)
    except Exception as e:
        logger.error(f"배당금액 파싱 실패: {amount_str}, 오류: {e}")
        return None


def scrape_usa_etf_dividend(ticker: str = "QYLD", save_to_db: bool = True, years: list = [2024, 2025]):
    """
    Seeking Alpha에서 미국 ETF 배당 정보를 스크래핑
    
    Args:
        ticker: ETF 티커 (기본값: QYLD)
        save_to_db: 데이터베이스에 저장할지 여부 (기본값: True)
        years: 가져올 연도 리스트 (기본값: [2024, 2025])
    
    Returns:
        list: 스크래핑한 배당 데이터 리스트
    """
    url = f"https://seekingalpha.com/symbol/{ticker}/dividends/history"
    
    # Chrome 옵션 설정 (사람처럼 보이도록)
    chrome_options = Options()
    # 헤드리스 모드 비활성화 (사람처럼 보이기 위해)
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')  # 자동화 감지 방지
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])  # 자동화 플래그 제거
    chrome_options.add_experimental_option('useAutomationExtension', False)  # 자동화 확장 비활성화
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--start-maximized')
    # 더 현실적인 User-Agent
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    driver = None
    db: Session = None
    
    try:
        # 데이터베이스 세션 생성
        if save_to_db:
            db = SessionLocal()
            etf = usa_etfs.get_usa_etf_by_ticker(db, ticker)
            if not etf:
                logger.error(f"티커 {ticker}에 해당하는 ETF를 데이터베이스에서 찾을 수 없습니다.")
                return []
        
        # Chrome 드라이버 초기화
        logger.info("Chrome 드라이버를 초기화합니다...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # 자동화 감지 방지를 위한 JavaScript 실행
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            '''
        })
        
        # 페이지 접속
        logger.info(f"페이지 접속 중: {url}")
        driver.get(url)
        
        # 페이지 로딩 대기 (더 긴 대기 시간)
        wait = WebDriverWait(driver, 30)
        time.sleep(5)  # 초기 로딩 대기
        
        # CAPTCHA 확인 및 대기
        try:
            captcha_indicators = [
                "계속하기 전에",
                "길게 누르기",
                "로봇이 아니라 사람인지 확인",
                "verify",
                "captcha",
                "challenge"
            ]
            
            page_text = driver.page_source.lower()
            page_title = driver.title.lower()
            
            captcha_found = False
            for indicator in captcha_indicators:
                if indicator.lower() in page_text or indicator.lower() in page_title:
                    captcha_found = True
                    break
            
            if captcha_found:
                logger.warning("="*60)
                logger.warning("CAPTCHA가 감지되었습니다!")
                logger.warning("브라우저 창에서 CAPTCHA를 수동으로 해결해주세요.")
                logger.warning("CAPTCHA 해결 후 60초 이내에 페이지가 로드되면 자동으로 계속됩니다.")
                logger.warning("="*60)
                
                # CAPTCHA 해결 대기 (최대 60초)
                max_wait_time = 60
                check_interval = 2
                waited_time = 0
                
                while waited_time < max_wait_time:
                    time.sleep(check_interval)
                    waited_time += check_interval
                    
                    # CAPTCHA가 해결되었는지 확인
                    current_text = driver.page_source.lower()
                    current_title = driver.title.lower()
                    captcha_still_present = False
                    
                    for indicator in captcha_indicators:
                        if indicator.lower() in current_text or indicator.lower() in current_title:
                            captcha_still_present = True
                            break
                    
                    if not captcha_still_present:
                        logger.info(f"CAPTCHA가 해결된 것으로 보입니다. 계속 진행합니다. (대기 시간: {waited_time}초)")
                        break
                    
                    if waited_time % 10 == 0:
                        logger.info(f"CAPTCHA 해결 대기 중... ({waited_time}/{max_wait_time}초)")
                
                if waited_time >= max_wait_time:
                    logger.error("CAPTCHA 해결 시간 초과. 스크래핑을 중단합니다.")
                    return []
        except Exception as e:
            logger.warning(f"CAPTCHA 확인 중 오류 (계속 진행): {e}")
        
        time.sleep(3)  # 추가 로딩 대기
        
        # 사람처럼 스크롤 (페이지가 완전히 로드되도록)
        logger.info("페이지 스크롤 중...")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/3);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, 0);")
        time.sleep(2)
        
        # 배당 테이블 찾기
        logger.info("배당 테이블 찾는 중...")
        
        # 동적 콘텐츠 로딩을 위한 추가 대기
        time.sleep(5)
        
        # 페이지가 완전히 로드될 때까지 대기
        try:
            WebDriverWait(driver, 30).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except:
            pass
        
        # 배당 히스토리 섹션으로 스크롤
        try:
            # 여러 가능한 텍스트 패턴으로 섹션 찾기
            history_xpaths = [
                "//*[contains(text(), 'Dividend History')]",
                "//*[contains(text(), 'dividend history')]",
                "//*[contains(text(), 'Dividend') and contains(text(), 'History')]",
                "//h2[contains(text(), 'Dividend')]",
                "//h3[contains(text(), 'Dividend')]",
            ]
            for xpath in history_xpaths:
                try:
                    history_section = driver.find_element(By.XPATH, xpath)
                    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", history_section)
                    time.sleep(3)
                    logger.info(f"Dividend History 섹션을 찾았습니다: {xpath}")
                    break
                except:
                    continue
        except:
            logger.warning("Dividend History 섹션을 찾지 못했습니다. 계속 진행합니다.")
        
        # 추가 대기 (JavaScript 실행 대기)
        time.sleep(5)
        
        # 여러 방법으로 테이블 찾기 시도
        table = None
        
        # 방법 1: 모든 테이블 찾기
        tables = driver.find_elements(By.TAG_NAME, "table")
        logger.info(f"페이지에서 {len(tables)}개의 table 태그를 찾았습니다.")
        
        # 배당 히스토리 테이블 찾기 (헤더에 "Record Date", "Pay Date", "Adj. Amount"가 있는 테이블)
        for tbl in tables:
            try:
                # thead 확인
                thead = tbl.find_element(By.TAG_NAME, "thead")
                header_row = thead.find_element(By.TAG_NAME, "tr")
                header_cells = header_row.find_elements(By.TAG_NAME, "th")
                headers = [cell.text.strip() for cell in header_cells]
                logger.info(f"테이블 헤더 발견: {headers}")
                
                # 배당 히스토리 테이블의 특징적인 헤더 확인
                headers_lower = [h.lower() for h in headers]
                if any('record' in h and 'date' in h for h in headers_lower) and \
                   any('adj' in h and 'amount' in h for h in headers_lower):
                    table = tbl
                    logger.info(f"배당 히스토리 테이블을 찾았습니다! 헤더: {headers}")
                    break
            except Exception as e:
                logger.debug(f"테이블 헤더 확인 중 오류: {e}")
                continue
        
        # 방법 2: 제공된 XPath로 시도
        if not table:
            try:
                xpath = "/html/body/div[3]/div/div[1]/div/main/div[2]/div[2]/div/div/div[1]/div/div[2]/section[4]/div/div[2]/div/div[3]"
                table = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                logger.info("XPath로 테이블을 찾았습니다.")
            except Exception as e:
                logger.warning(f"XPath로 테이블을 찾지 못했습니다: {e}")
        
        # 방법 3: div 기반 테이블 구조 확인
        if not table:
            logger.info("div 기반 테이블 구조를 확인합니다...")
            try:
                # "Record Date" 텍스트가 있는 요소 주변 찾기
                record_date_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Record Date') or contains(text(), 'record date')]")
                logger.info(f"'Record Date' 텍스트를 포함한 요소 {len(record_date_elements)}개를 찾았습니다.")
                
                for elem in record_date_elements:
                    try:
                        # 부모 요소들을 거슬러 올라가서 테이블 구조 찾기
                        parent = elem.find_element(By.XPATH, "./ancestor::table[1]")
                        table = parent
                        logger.info("Record Date 텍스트 근처에서 테이블을 찾았습니다.")
                        break
                    except:
                        try:
                            # div 구조인 경우
                            parent = elem.find_element(By.XPATH, "./ancestor::div[contains(@class, 'table') or contains(@class, 'grid')][1]")
                            table = parent
                            logger.info("Record Date 텍스트 근처에서 div 테이블을 찾았습니다.")
                            break
                        except:
                            continue
            except Exception as e:
                logger.warning(f"div 기반 테이블 찾기 중 오류: {e}")
        
        if not table:
            logger.error(f"배당 히스토리 테이블을 찾을 수 없습니다.")
            logger.error(f"페이지 URL: {driver.current_url}")
            logger.error(f"페이지 제목: {driver.title}")
            
            # 디버깅: 페이지 소스 일부 확인
            try:
                page_source = driver.page_source
                if 'Record Date' in page_source or 'record date' in page_source.lower():
                    logger.info("페이지 소스에 'Record Date' 텍스트가 있습니다.")
                else:
                    logger.warning("페이지 소스에 'Record Date' 텍스트가 없습니다.")
                
                # 페이지 소스 일부 저장 (디버깅용)
                with open(f"debug_page_source_{ticker}.html", "w", encoding="utf-8") as f:
                    f.write(page_source[:50000])  # 처음 50KB만 저장
                logger.info(f"페이지 소스를 debug_page_source_{ticker}.html 파일에 저장했습니다.")
            except Exception as e:
                logger.error(f"페이지 소스 확인 중 오류: {e}")
            
            return []
        
        # 테이블 헤더 찾기
        headers = []
        try:
            thead = table.find_element(By.TAG_NAME, "thead")
            header_row = thead.find_element(By.TAG_NAME, "tr")
            header_cells = header_row.find_elements(By.TAG_NAME, "th")
            headers = [cell.text.strip() for cell in header_cells]
            logger.info(f"테이블 헤더: {headers}")
        except:
            logger.warning("테이블 헤더를 찾을 수 없습니다. 기본 헤더를 사용합니다.")
        
        # 테이블 행 찾기
        rows = []
        try:
            # tbody 내의 행들 찾기
            tbody = table.find_element(By.TAG_NAME, "tbody")
            rows = tbody.find_elements(By.TAG_NAME, "tr")
        except:
            try:
                # tbody가 없으면 직접 tr 찾기 (헤더 행 제외)
                all_rows = table.find_elements(By.TAG_NAME, "tr")
                rows = all_rows[1:] if len(all_rows) > 1 else all_rows
            except:
                logger.error("테이블 행을 찾을 수 없습니다.")
                return []
        
        logger.info(f"총 {len(rows)}개의 데이터 행을 찾았습니다.")
        
        # 데이터프레임을 위한 데이터 리스트
        df_data = []
        
        for idx, row in enumerate(rows, 1):
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) == 0:
                    continue
                
                # 각 셀의 텍스트 추출
                row_data = {}
                for i, cell in enumerate(cells):
                    header_name = headers[i] if i < len(headers) else f"Column_{i}"
                    row_data[header_name] = cell.text.strip()
                
                df_data.append(row_data)
                logger.debug(f"행 {idx} 데이터: {row_data}")
                
            except Exception as e:
                logger.error(f"행 {idx} 처리 중 오류: {e}")
                continue
        
        # 데이터프레임 생성
        if not df_data:
            logger.warning("추출된 데이터가 없습니다.")
            return []
        
        df = pd.DataFrame(df_data)
        logger.info(f"데이터프레임 생성 완료: {len(df)}행, {len(df.columns)}열")
        logger.info(f"컬럼명: {list(df.columns)}")
        
        # 컬럼명 매핑 및 데이터 변환
        dividends_data = []
        
        # 컬럼명 매핑 (대소문자 무시, 공백 무시)
        record_date_col = None
        payment_date_col = None
        dividend_amt_col = None
        
        for col in df.columns:
            col_lower = col.lower().strip()
            if 'record' in col_lower and 'date' in col_lower:
                record_date_col = col
            elif ('pay' in col_lower or 'payment' in col_lower) and 'date' in col_lower:
                payment_date_col = col
            elif 'adj' in col_lower and 'amount' in col_lower:
                dividend_amt_col = col
            elif 'amount' in col_lower and not dividend_amt_col:
                dividend_amt_col = col
        
        logger.info(f"컬럼 매핑: Record Date={record_date_col}, Pay Date={payment_date_col}, Adj. Amount={dividend_amt_col}")
        
        if not record_date_col or not dividend_amt_col:
            logger.error(f"필수 컬럼을 찾을 수 없습니다. Record Date: {record_date_col}, Adj. Amount: {dividend_amt_col}")
            logger.info(f"사용 가능한 컬럼: {list(df.columns)}")
            return []
        
        # 데이터프레임 처리
        for idx, row in df.iterrows():
            try:
                # Record Date 파싱
                record_date_str = str(row[record_date_col]).strip()
                record_date = parse_date(record_date_str)
                
                if not record_date:
                    logger.warning(f"행 {idx}: Record Date 파싱 실패 - {record_date_str}")
                    continue
                
                # 연도 필터링
                if record_date.year not in years:
                    continue
                
                # Pay Date 파싱
                payment_date = None
                if payment_date_col and payment_date_col in row:
                    payment_date_str = str(row[payment_date_col]).strip()
                    payment_date = parse_date(payment_date_str)
                
                # payment_date가 없으면 record_date와 동일하게 설정
                if not payment_date:
                    payment_date = record_date
                
                # Adj. Amount 파싱
                dividend_amt_str = str(row[dividend_amt_col]).strip()
                dividend_amt = parse_dividend_amount(dividend_amt_str)
                
                if not dividend_amt:
                    logger.warning(f"행 {idx}: Adj. Amount 파싱 실패 - {dividend_amt_str}")
                    continue
                
                dividend_info = {
                    'record_date': record_date,
                    'payment_date': payment_date,
                    'dividend_amt': dividend_amt
                }
                
                dividends_data.append(dividend_info)
                logger.info(f"배당 데이터 추출: {record_date} - ${dividend_amt}")
                
            except Exception as e:
                logger.error(f"행 {idx} 처리 중 오류: {e}")
                continue
        
        logger.info(f"총 {len(dividends_data)}개의 배당 데이터를 추출했습니다.")
        
        # 데이터베이스에 저장
        if save_to_db and db and etf and dividends_data:
            try:
                dividends_to_save = []
                for div_data in dividends_data:
                    dividend_data = {
                        'etf_id': etf.id,
                        'record_date': div_data['record_date'],
                        'payment_date': div_data['payment_date'],
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
        logger.error(f"스크래핑 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        if db:
            db.rollback()
        return []
    finally:
        if driver:
            driver.quit()
        if db:
            db.close()


def scrape_all_usa_etf_dividends(ticker: str = None, years: list = [2024, 2025]):
    """
    모든 미국 ETF 또는 특정 티커의 배당 정보를 스크래핑
    
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
            dividends = scrape_usa_etf_dividend(etf.ticker, save_to_db=True, years=years)
            if dividends:
                logger.info(f"[OK] {etf.ticker} 배당 정보 스크래핑 완료: {len(dividends)}개")
                success_count += 1
            else:
                logger.warning(f"[WARN] {etf.ticker} 배당 정보를 찾을 수 없습니다.")
                fail_count += 1
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
    
    scrape_all_usa_etf_dividends(ticker=ticker, years=[2024, 2025])

