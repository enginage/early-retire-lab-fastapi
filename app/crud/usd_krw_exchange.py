from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import date
from app.models.usd_krw_exchange import USDKRWExchange
from app.schemas.usd_krw_exchange import USDKRWExchangeCreate, USDKRWExchangeUpdate
from decimal import Decimal

def get_usd_krw_exchange(db: Session, exchange_id: int) -> Optional[USDKRWExchange]:
    """ID로 환율 조회"""
    return db.query(USDKRWExchange).filter(USDKRWExchange.id == exchange_id).first()

def get_usd_krw_exchange_by_date(db: Session, exchange_date: date) -> Optional[USDKRWExchange]:
    """날짜로 환율 조회"""
    return db.query(USDKRWExchange).filter(USDKRWExchange.date == exchange_date).first()

def get_usd_krw_exchanges(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
) -> List[USDKRWExchange]:
    """환율 목록 조회 (날짜 역순)"""
    query = db.query(USDKRWExchange)
    
    if start_date:
        query = query.filter(USDKRWExchange.date >= start_date)
    if end_date:
        query = query.filter(USDKRWExchange.date <= end_date)
    
    return query.order_by(desc(USDKRWExchange.date)).offset(skip).limit(limit).all()

def create_usd_krw_exchange(db: Session, exchange: USDKRWExchangeCreate) -> USDKRWExchange:
    """환율 생성"""
    db_exchange = USDKRWExchange(
        date=exchange.date,
        exchange_rate=exchange.exchange_rate
    )
    db.add(db_exchange)
    db.commit()
    db.refresh(db_exchange)
    return db_exchange

def update_usd_krw_exchange(
    db: Session, 
    exchange_id: int, 
    exchange: USDKRWExchangeUpdate
) -> Optional[USDKRWExchange]:
    """환율 업데이트"""
    db_exchange = get_usd_krw_exchange(db, exchange_id)
    if not db_exchange:
        return None
    
    update_data = exchange.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_exchange, field, value)
    
    db.commit()
    db.refresh(db_exchange)
    return db_exchange

def delete_usd_krw_exchange(db: Session, exchange_id: int) -> bool:
    """환율 삭제"""
    db_exchange = get_usd_krw_exchange(db, exchange_id)
    if not db_exchange:
        return False
    
    db.delete(db_exchange)
    db.commit()
    return True

def bulk_upsert_usd_krw_exchanges(
    db: Session, 
    exchanges: List[USDKRWExchangeCreate]
) -> int:
    """
    환율 일괄 upsert (날짜 기준으로 존재하면 업데이트, 없으면 생성)
    
    Returns:
        생성/업데이트된 레코드 수
    """
    created_count = 0
    updated_count = 0
    
    for exchange_data in exchanges:
        existing = get_usd_krw_exchange_by_date(db, exchange_data.date)
        
        if existing:
            # 업데이트
            existing.exchange_rate = exchange_data.exchange_rate
            updated_count += 1
        else:
            # 생성
            db_exchange = USDKRWExchange(
                date=exchange_data.date,
                exchange_rate=exchange_data.exchange_rate
            )
            db.add(db_exchange)
            created_count += 1
    
    db.commit()
    return created_count + updated_count

