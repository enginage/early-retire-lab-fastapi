from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.usa_etf import USAETF, USAETFCreate, USAETFUpdate
from app.crud import usa_etf

router = APIRouter()

@router.get("/", response_model=List[USAETF])
def read_usa_etfs(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    etfs = usa_etf.get_usa_etfs(db, skip=skip, limit=limit)
    return etfs

@router.get("/{etf_id}", response_model=USAETF)
def read_usa_etf(etf_id: int, db: Session = Depends(get_db)):
    db_etf = usa_etf.get_usa_etf(db, etf_id=etf_id)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return db_etf

@router.post("/", response_model=USAETF)
def create_usa_etf(etf: USAETFCreate, db: Session = Depends(get_db)):
    # 중복 체크
    existing = usa_etf.get_usa_etf_by_ticker(db, ticker=etf.ticker)
    if existing:
        raise HTTPException(status_code=400, detail="ETF with this ticker already exists")
    return usa_etf.create_usa_etf(db=db, etf=etf)

@router.put("/{etf_id}", response_model=USAETF)
def update_usa_etf(etf_id: int, etf: USAETFUpdate, db: Session = Depends(get_db)):
    db_etf = usa_etf.update_usa_etf(db=db, etf_id=etf_id, etf=etf)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return db_etf

@router.delete("/{etf_id}")
def delete_usa_etf(etf_id: int, db: Session = Depends(get_db)):
    db_etf = usa_etf.delete_usa_etf(db=db, etf_id=etf_id)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return {"message": "ETF deleted successfully"}

@router.post("/bulk")
def bulk_create_usa_etfs(etfs: List[USAETFCreate], db: Session = Depends(get_db)):
    """여러 ETF를 한 번에 생성"""
    etf_dicts = [etf.model_dump() for etf in etfs]
    created_count = usa_etf.bulk_create_usa_etfs(db=db, etfs=etf_dicts)
    return {"message": f"{created_count} ETFs created successfully"}

