from sqlalchemy.orm import Session
from app.models.usa_etfs_dividend import USAETFsDividend
from app.schemas.usa_etfs_dividend import USAETFsDividendCreate, USAETFsDividendUpdate

def get_usa_etf_dividend(db: Session, dividend_id: int):
    return db.query(USAETFsDividend).filter(USAETFsDividend.id == dividend_id).first()

def get_usa_etf_dividends_by_etf_id(db: Session, etf_id: int, skip: int = 0, limit: int = 100):
    return db.query(USAETFsDividend).filter(USAETFsDividend.etf_id == etf_id).order_by(USAETFsDividend.record_date.desc()).offset(skip).limit(limit).all()

def get_usa_etf_dividends(db: Session, skip: int = 0, limit: int = 100):
    return db.query(USAETFsDividend).offset(skip).limit(limit).all()

def create_usa_etf_dividend(db: Session, dividend: USAETFsDividendCreate):
    db_dividend = USAETFsDividend(**dividend.model_dump())
    db.add(db_dividend)
    db.commit()
    db.refresh(db_dividend)
    return db_dividend

def get_usa_etf_dividend_by_etf_and_date(db: Session, etf_id: int, record_date):
    """etf_id와 record_date로 배당 정보 조회"""
    return db.query(USAETFsDividend).filter(
        USAETFsDividend.etf_id == etf_id,
        USAETFsDividend.record_date == record_date
    ).first()

def bulk_upsert_usa_etf_dividends(db: Session, dividends: list):
    """여러 배당 정보를 한 번에 upsert (etf_id와 record_date가 같으면 업데이트, 없으면 생성)"""
    created_count = 0
    updated_count = 0
    
    for dividend_data in dividends:
        etf_id = dividend_data.get('etf_id')
        record_date = dividend_data.get('record_date')
        
        if not etf_id or not record_date:
            continue
        
        # 기존 데이터 조회
        existing = get_usa_etf_dividend_by_etf_and_date(db, etf_id, record_date)
        
        if existing:
            # 업데이트
            update_data = {k: v for k, v in dividend_data.items() if k not in ['etf_id', 'record_date']}
            for field, value in update_data.items():
                setattr(existing, field, value)
            updated_count += 1
        else:
            # 생성
            db_dividend = USAETFsDividend(**dividend_data)
            db.add(db_dividend)
            created_count += 1
    
    db.commit()
    return {'created': created_count, 'updated': updated_count}

def bulk_create_usa_etf_dividends(db: Session, dividends: list):
    """여러 배당 정보를 한 번에 생성 (기존 함수 유지)"""
    created_count = 0
    for dividend_data in dividends:
        db_dividend = USAETFsDividend(**dividend_data)
        db.add(db_dividend)
        created_count += 1
    db.commit()
    return created_count

def update_usa_etf_dividend(db: Session, dividend_id: int, dividend: USAETFsDividendUpdate):
    db_dividend = db.query(USAETFsDividend).filter(USAETFsDividend.id == dividend_id).first()
    if db_dividend:
        update_data = dividend.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_dividend, field, value)
        db.commit()
        db.refresh(db_dividend)
    return db_dividend

def delete_usa_etf_dividend(db: Session, dividend_id: int):
    db_dividend = db.query(USAETFsDividend).filter(USAETFsDividend.id == dividend_id).first()
    if db_dividend:
        db.delete(db_dividend)
        db.commit()
    return db_dividend

