from sqlalchemy.orm import Session
from app.models.domestic_etfs import DomesticETFs
from app.schemas.domestic_etfs import DomesticETFsCreate, DomesticETFsUpdate

def get_domestic_etf(db: Session, etf_id: int):
    return db.query(DomesticETFs).filter(DomesticETFs.id == etf_id).first()

def get_domestic_etf_by_ticker(db: Session, ticker: str):
    return db.query(DomesticETFs).filter(DomesticETFs.ticker == ticker).first()

def get_domestic_etfs(db: Session, skip: int = 0, limit: int = 100, etf_type: str = None):
    query = db.query(DomesticETFs)
    if etf_type:
        query = query.filter(DomesticETFs.etf_type == etf_type)
    return query.offset(skip).limit(limit).all()

def create_domestic_etf(db: Session, etf: DomesticETFsCreate):
    db_etf = DomesticETFs(**etf.model_dump())
    db.add(db_etf)
    db.commit()
    db.refresh(db_etf)
    return db_etf

def update_domestic_etf(db: Session, etf_id: int, etf: DomesticETFsUpdate):
    db_etf = db.query(DomesticETFs).filter(DomesticETFs.id == etf_id).first()
    if db_etf:
        update_data = etf.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_etf, field, value)
        db.commit()
        db.refresh(db_etf)
    return db_etf

def delete_domestic_etf(db: Session, etf_id: int):
    db_etf = db.query(DomesticETFs).filter(DomesticETFs.id == etf_id).first()
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
            db_etf = DomesticETFs(**etf_data)
            db.add(db_etf)
            created_count += 1
    db.commit()
    return created_count


