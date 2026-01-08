from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.schemas.domestic_etfs_daily_chart import DomesticETFsDailyChart
from app.crud import domestic_etfs_daily_chart

router = APIRouter()

@router.get("/etf/{etf_id}/latest", response_model=DomesticETFsDailyChart)
def get_latest_chart(etf_id: int, db: Session = Depends(get_db)):
    """ETF의 가장 최근 일봉 차트 데이터 조회"""
    chart = domestic_etfs_daily_chart.get_latest_domestic_etf_daily_chart(db, etf_id=etf_id)
    if chart is None:
        raise HTTPException(status_code=404, detail="Chart data not found")
    return chart

@router.get("/etf/{etf_id}/date/{chart_date}", response_model=DomesticETFsDailyChart)
def get_chart_by_date(etf_id: int, chart_date: date, db: Session = Depends(get_db)):
    """ETF의 특정 날짜 일봉 차트 데이터 조회"""
    chart = domestic_etfs_daily_chart.get_domestic_etf_daily_chart_by_etf_and_date(db, etf_id=etf_id, date=chart_date)
    if chart is None:
        raise HTTPException(status_code=404, detail="Chart data not found for the specified date")
    return chart

@router.get("/etf/{etf_id}/period", response_model=Optional[DomesticETFsDailyChart])
def get_chart_by_period(etf_id: int, months_ago: int = 12, db: Session = Depends(get_db)):
    """ETF의 N개월 전 일봉 차트 데이터 조회 (해당 날짜에 가장 가까운 데이터)"""
    # 개월 단위로 계산 (1개월 = 30일로 근사)
    target_date = datetime.now().date() - timedelta(days=months_ago * 30)
    
    # 해당 날짜 또는 그 이전의 가장 가까운 데이터 조회
    charts = domestic_etfs_daily_chart.get_domestic_etf_daily_chart_by_date_range(
        db, etf_id=etf_id, start_date=target_date - timedelta(days=30), end_date=target_date + timedelta(days=30)
    )
    
    if not charts:
        return None
    
    # target_date에 가장 가까운 데이터 찾기
    closest_chart = min(charts, key=lambda x: abs((x.date - target_date).days))
    return closest_chart

@router.get("/etf/{etf_id}", response_model=List[DomesticETFsDailyChart])
def get_charts_by_etf(etf_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """ETF의 일봉 차트 데이터 목록 조회"""
    charts = domestic_etfs_daily_chart.get_domestic_etf_daily_charts_by_etf_id(db, etf_id=etf_id, skip=skip, limit=limit)
    return charts

