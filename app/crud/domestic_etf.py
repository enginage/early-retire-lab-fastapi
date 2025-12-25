from sqlalchemy.orm import Session
from app.models.domestic_etf import DomesticETF
from app.schemas.domestic_etf import DomesticETFCreate, DomesticETFUpdate

def get_domestic_etf(db: Session, etf_id: int):
    return db.query(DomesticETF).filter(DomesticETF.id == etf_id).first()

def get_domestic_etf_by_ticker(db: Session, ticker: str):
    return db.query(DomesticETF).filter(DomesticETF.ticker == ticker).first()

def get_domestic_etfs(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DomesticETF).offset(skip).limit(limit).all()

def create_domestic_etf(db: Session, etf: DomesticETFCreate):
    db_etf = DomesticETF(**etf.dict())
    db.add(db_etf)
    db.commit()
    db.refresh(db_etf)
    return db_etf

def update_domestic_etf(db: Session, etf_id: int, etf: DomesticETFUpdate):
    db_etf = db.query(DomesticETF).filter(DomesticETF.id == etf_id).first()
    if db_etf:
        update_data = etf.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_etf, field, value)
        db.commit()
        db.refresh(db_etf)
    return db_etf

def delete_domestic_etf(db: Session, etf_id: int):
    db_etf = db.query(DomesticETF).filter(DomesticETF.id == etf_id).first()
    if db_etf:
        db.delete(db_etf)
        db.commit()
    return db_etf

def bulk_create_domestic_etfs(db: Session, etfs: list):
    """여러 ETF를 한 번에 생성 (중복 체크)"""
    created_count = 0
    for etf_data in etfs:
        existing = get_domestic_etf_by_ticker(db, etf_data['ticker'])
        if not existing:
            db_etf = DomesticETF(**etf_data)
            db.add(db_etf)
            created_count += 1
    db.commit()
    return created_count


