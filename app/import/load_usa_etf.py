"""
미국 ETF 데이터를 FinanceDataReader를 사용해서 가져와서 DB에 저장하는 스크립트
"""
import os
import sys
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.usa_etf import USAETF
from app.database import Base

# 테이블 생성
Base.metadata.create_all(bind=engine)

def load_usa_etf_data():
    """FinanceDataReader를 사용해서 미국 ETF 데이터를 가져와서 DB에 저장"""
    try:
        import FinanceDataReader as fdr
        
        print("미국 ETF 데이터를 가져오는 중...")
        # ETF/US 데이터 가져오기
        df = fdr.StockListing('ETF/US')
        
        if df is None or df.empty:
            print("데이터를 가져올 수 없습니다.")
            return
        
        print(f"총 {len(df)}개의 ETF 데이터를 가져왔습니다.")
        
        db: Session = SessionLocal()
        try:
            created_count = 0
            updated_count = 0
            
            # DataFrame의 컬럼 확인 (ticker와 name 컬럼이 있는지 확인)
            print(f"DataFrame 컬럼: {df.columns.tolist()}")
            
            # 일반적인 컬럼명 매핑
            ticker_col = None
            name_col = None
            
            # 가능한 ticker 컬럼명들
            for col in ['Symbol', 'symbol', 'Ticker', 'ticker', 'Code', 'code']:
                if col in df.columns:
                    ticker_col = col
                    break
            
            # 가능한 name 컬럼명들
            for col in ['Name', 'name', '종목명', 'ETF명']:
                if col in df.columns:
                    name_col = col
                    break
            
            if ticker_col is None or name_col is None:
                print(f"필요한 컬럼을 찾을 수 없습니다. 사용 가능한 컬럼: {df.columns.tolist()}")
                return
            
            print(f"Ticker 컬럼: {ticker_col}, Name 컬럼: {name_col}")
            
            # DataFrame에서 중복된 ticker 제거 (첫 번째 것만 유지)
            df_cleaned = df.drop_duplicates(subset=[ticker_col], keep='first')
            duplicate_count = len(df) - len(df_cleaned)
            if duplicate_count > 0:
                print(f"중복된 ticker {duplicate_count}개를 제거했습니다.")
            
            print(f"처리할 데이터: {len(df_cleaned)}개")
            
            for idx, row in df_cleaned.iterrows():
                ticker = str(row[ticker_col]).strip()
                name = str(row[name_col]).strip()
                
                if not ticker or not name or ticker == 'nan' or name == 'nan':
                    continue
                
                # 기존 데이터 확인
                existing = db.query(USAETF).filter(USAETF.ticker == ticker).first()
                
                if existing:
                    # 업데이트
                    existing.name = name
                    updated_count += 1
                else:
                    # 새로 생성
                    new_etf = USAETF(ticker=ticker, name=name)
                    db.add(new_etf)
                    created_count += 1
            
            db.commit()
            print(f"완료: {created_count}개 생성, {updated_count}개 업데이트")
            
        except Exception as e:
            db.rollback()
            print(f"데이터베이스 저장 중 오류 발생: {str(e)}")
            raise
        finally:
            db.close()
            
    except ImportError:
        print("FinanceDataReader가 설치되지 않았습니다. 'pip install FinanceDataReader' 명령으로 설치해주세요.")
    except Exception as e:
        print(f"오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    load_usa_etf_data()

