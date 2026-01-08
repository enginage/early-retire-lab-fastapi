from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.domestic_etfs import DomesticETFs, DomesticETFsCreate, DomesticETFsUpdate
from app.crud import domestic_etfs

router = APIRouter()

@router.get("/", response_model=List[DomesticETFs])
def read_domestic_etfs(skip: int = 0, limit: int = 1000, etf_type: str = None, db: Session = Depends(get_db)):
    etfs = domestic_etfs.get_domestic_etfs(db, skip=skip, limit=limit, etf_type=etf_type)
    return etfs

@router.get("/{etf_id}", response_model=DomesticETFs)
def read_domestic_etf(etf_id: int, db: Session = Depends(get_db)):
    db_etf = domestic_etfs.get_domestic_etf(db, etf_id=etf_id)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return db_etf

@router.post("/", response_model=DomesticETFs)
def create_domestic_etf(etf: DomesticETFsCreate, db: Session = Depends(get_db)):
    # 중복 체크
    existing = domestic_etfs.get_domestic_etf_by_ticker(db, ticker=etf.ticker)
    if existing:
        raise HTTPException(status_code=400, detail="ETF with this ticker already exists")
    return domestic_etfs.create_domestic_etf(db=db, etf=etf)

@router.put("/{etf_id}", response_model=DomesticETFs)
def update_domestic_etf(etf_id: int, etf: DomesticETFsUpdate, db: Session = Depends(get_db)):
    db_etf = domestic_etfs.update_domestic_etf(db=db, etf_id=etf_id, etf=etf)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return db_etf

@router.delete("/{etf_id}")
def delete_domestic_etf(etf_id: int, db: Session = Depends(get_db)):
    db_etf = domestic_etfs.delete_domestic_etf(db=db, etf_id=etf_id)
    if db_etf is None:
        raise HTTPException(status_code=404, detail="ETF not found")
    return {"message": "ETF deleted successfully"}

@router.post("/bulk")
def bulk_create_domestic_etfs(etfs: List[DomesticETFsCreate], db: Session = Depends(get_db)):
    """여러 ETF를 한 번에 생성"""
    etf_dicts = [etf.model_dump() for etf in etfs]
    created_count = domestic_etfs.bulk_create_domestic_etfs(db=db, etfs=etf_dicts)
    return {"message": f"{created_count} ETFs created successfully"}

