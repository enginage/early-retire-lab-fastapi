from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.schemas.domestic_etfs_dividend import DomesticETFsDividend
from app.crud import domestic_etfs_dividend

router = APIRouter()

@router.get("/etf/{etf_id}", response_model=List[DomesticETFsDividend])
def get_dividends_by_etf(etf_id: int, db: Session = Depends(get_db)):
    """ETF의 모든 배당 데이터 조회"""
    dividends = domestic_etfs_dividend.get_domestic_etf_dividends_by_etf_id(db, etf_id=etf_id)
    return dividends

@router.get("/etf/{etf_id}/period", response_model=List[DomesticETFsDividend])
def get_dividends_by_period(etf_id: int, months_ago: int = 12, db: Session = Depends(get_db)):
    """ETF의 N개월 전부터 현재까지의 배당 데이터 조회"""
    # 현재 날짜에서 N개월 전 날짜 계산
    target_date = datetime.now().date() - timedelta(days=months_ago * 30)
    
    # 모든 배당 데이터 조회
    all_dividends = domestic_etfs_dividend.get_domestic_etf_dividends_by_etf_id(db, etf_id=etf_id, limit=1000)
    
    # 해당 기간 이후의 배당만 필터링
    filtered_dividends = [d for d in all_dividends if d.payment_date >= target_date]
    
    # record_date(기준일) 기준 내림차순 정렬 (최신순)
    filtered_dividends.sort(key=lambda x: x.record_date, reverse=True)
    
    return filtered_dividends

