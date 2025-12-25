from sqlalchemy.orm import Session
from app.models.usa_etf import USAETF
from app.schemas.usa_etf import USAETFCreate, USAETFUpdate

def get_usa_etf(db: Session, etf_id: int):
    return db.query(USAETF).filter(USAETF.id == etf_id).first()

def get_usa_etf_by_ticker(db: Session, ticker: str):
    return db.query(USAETF).filter(USAETF.ticker == ticker).first()

def get_usa_etfs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(USAETF).offset(skip).limit(limit).all()

def create_usa_etf(db: Session, etf: USAETFCreate):
    db_etf = USAETF(**etf.model_dump())
    db.add(db_etf)
    db.commit()
    db.refresh(db_etf)
    return db_etf

def update_usa_etf(db: Session, etf_id: int, etf: USAETFUpdate):
    db_etf = db.query(USAETF).filter(USAETF.id == etf_id).first()
    if db_etf:
        update_data = etf.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_etf, field, value)
        db.commit()
        db.refresh(db_etf)
    return db_etf

def delete_usa_etf(db: Session, etf_id: int):
    db_etf = db.query(USAETF).filter(USAETF.id == etf_id).first()
    if db_etf:
        db.delete(db_etf)
        db.commit()
    return db_etf

def bulk_create_usa_etfs(db: Session, etfs: list):
    """여러 ETF를 한 번에 생성 (중복 체크)"""
    created_count = 0
    for etf_data in etfs:
        existing = get_usa_etf_by_ticker(db, etf_data['ticker'])
        if not existing:
            db_etf = USAETF(**etf_data)
            db.add(db_etf)
            created_count += 1
    db.commit()
    return created_count

