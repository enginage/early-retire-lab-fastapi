from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.domestic_etf import DomesticETF, DomesticETFCreate, DomesticETFUpdate
from app.crud import domestic_etf

router = APIRouter()

@router.get("/", response_model=List[DomesticETF])
def read_domestic_etfs(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    etfs = domestic_etf.get_domestic_etfs(db, skip=skip, limit=limit)
    return etfs

@router.get("/{etf_id}", response_model=DomesticETF)
def read_domestic_etf(etf_id: int, db: Session = Depends(get_db)):
    db_etf = domestic_etf.get_domestic_etf(db, etf_id=etf_id)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return db_etf

@router.post("/", response_model=DomesticETF)
def create_domestic_etf(etf: DomesticETFCreate, db: Session = Depends(get_db)):
    # 중복 체크
    existing = domestic_etf.get_domestic_etf_by_ticker(db, ticker=etf.ticker)
    if existing:
        raise HTTPException(status_code=400, detail="ETF with this ticker already exists")
    return domestic_etf.create_domestic_etf(db=db, etf=etf)

@router.put("/{etf_id}", response_model=DomesticETF)
def update_domestic_etf(etf_id: int, etf: DomesticETFUpdate, db: Session = Depends(get_db)):
    db_etf = domestic_etf.update_domestic_etf(db=db, etf_id=etf_id, etf=etf)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return db_etf

@router.delete("/{etf_id}")
def delete_domestic_etf(etf_id: int, db: Session = Depends(get_db)):
    db_etf = domestic_etf.delete_domestic_etf(db=db, etf_id=etf_id)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return {"message": "ETF deleted successfully"}

@router.post("/bulk")
def bulk_create_domestic_etfs(etfs: List[DomesticETFCreate], db: Session = Depends(get_db)):
    """여러 ETF를 한 번에 생성"""
    etf_dicts = [etf.dict() for etf in etfs]
    created_count = domestic_etf.bulk_create_domestic_etfs(db=db, etfs=etf_dicts)
    return {"message": f"{created_count} ETFs created successfully"}

