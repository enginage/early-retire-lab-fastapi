from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.schemas.usa_etfs_dividend import USAETFsDividend
from app.crud import usa_etfs_dividend

router = APIRouter()

@router.get("/etf/{etf_id}", response_model=List[USAETFsDividend])
def get_dividends_by_etf(etf_id: int, db: Session = Depends(get_db)):
    """ETF의 모든 배당 데이터 조회"""
    dividends = usa_etfs_dividend.get_usa_etf_dividends_by_etf_id(db, etf_id=etf_id)
    return dividends

@router.get("/etf/{etf_id}/period", response_model=List[USAETFsDividend])
def get_dividends_by_period(etf_id: int, months_ago: int = 12, db: Session = Depends(get_db)):
    """ETF의 N개월 전부터 현재까지의 배당 데이터 조회"""
    target_date = datetime.now().date() - timedelta(days=months_ago * 30)
    
    all_dividends = usa_etfs_dividend.get_usa_etf_dividends_by_etf_id(db, etf_id=etf_id, limit=1000)
    
    filtered_dividends = [d for d in all_dividends if d.record_date >= target_date]
    
    # record_date 기준 내림차순 정렬
    filtered_dividends.sort(key=lambda x: x.record_date, reverse=True)
    
    return filtered_dividends

