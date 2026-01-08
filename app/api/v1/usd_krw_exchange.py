from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date
from app.database import get_db
from app.schemas.usd_krw_exchange import USDKRWExchange
from app.crud import usd_krw_exchange

router = APIRouter()

@router.get("/date/{exchange_date}", response_model=USDKRWExchange)
def get_exchange_by_date(exchange_date: date, db: Session = Depends(get_db)):
    """특정 날짜의 USD/KRW 환율 조회"""
    exchange = usd_krw_exchange.get_usd_krw_exchange_by_date(db, exchange_date=exchange_date)
    if exchange is None:
        raise HTTPException(status_code=404, detail="Exchange rate not found for the specified date")
    return exchange

@router.get("/date/{exchange_date}/nearest")
def get_nearest_exchange_by_date(exchange_date: date, db: Session = Depends(get_db)):
    """특정 날짜 또는 그 이전의 가장 가까운 USD/KRW 환율 조회"""
    try:
        # 정확한 날짜 조회 시도
        exchange = usd_krw_exchange.get_usd_krw_exchange_by_date(db, exchange_date=exchange_date)
        if exchange:
            return exchange
        
        # 그 이전의 가장 가까운 데이터 조회 (간단히 최근 데이터 반환)
        from sqlalchemy import desc
        from app.models.usd_krw_exchange import USDKRWExchange as USDKRWExchangeModel
        exchange = db.query(USDKRWExchangeModel).filter(
            USDKRWExchangeModel.date <= exchange_date
        ).order_by(desc(USDKRWExchangeModel.date)).first()
        
        if exchange is None:
            # 데이터가 전혀 없으면 기본값 반환하거나 빈 응답
            return None
        
        return exchange
    except Exception as e:
        # 에러 발생 시 로깅하고 None 반환
        import logging
        logging.error(f"Error fetching nearest exchange rate: {str(e)}")
        return None

