from sqlalchemy.orm import Session
from sqlalchemy import join
from app.models.isa_account_dividend import ISAAccountDividend
from app.models.domestic_etf import DomesticETF
from app.schemas.isa_account_dividend import ISAAccountDividendCreate, ISAAccountDividendUpdate

def get_isa_account_dividends(db: Session, account_id: int, year_month: str = None, skip: int = 0, limit: int = 100):
    query = db.query(
        ISAAccountDividend,
        DomesticETF.name.label('etf_name')
    ).join(
        DomesticETF,
        ISAAccountDividend.stock_code == DomesticETF.ticker,
        isouter=False  # INNER JOIN
    ).filter(
        ISAAccountDividend.account_id == account_id
    )
    
    if year_month:
        query = query.filter(ISAAccountDividend.year_month == year_month)
    
    results = query.offset(skip).limit(limit).all()
    
    # 조인된 결과를 ISAAccountDividend 객체에 etf_name을 추가
    dividends = []
    for dividend, etf_name in results:
        dividend.stock_name = etf_name
        dividends.append(dividend)
    
    return dividends

def get_isa_account_dividend(db: Session, dividend_id: int):
    result = db.query(
        ISAAccountDividend,
        DomesticETF.name.label('etf_name')
    ).join(
        DomesticETF,
        ISAAccountDividend.stock_code == DomesticETF.ticker,
        isouter=False  # INNER JOIN
    ).filter(
        ISAAccountDividend.id == dividend_id
    ).first()
    
    if result:
        dividend, etf_name = result
        dividend.stock_name = etf_name
        return dividend
    return None

def create_isa_account_dividend(db: Session, dividend: ISAAccountDividendCreate):
    db_dividend = ISAAccountDividend(
        account_id=dividend.account_id,
        year_month=dividend.year_month,
        stock_code=dividend.stock_code,
        dividend_amount=dividend.dividend_amount
    )
    db.add(db_dividend)
    db.commit()
    db.refresh(db_dividend)
    return db_dividend

def update_isa_account_dividend(db: Session, dividend_id: int, dividend: ISAAccountDividendUpdate):
    db_dividend = db.query(ISAAccountDividend).filter(ISAAccountDividend.id == dividend_id).first()
    if not db_dividend:
        return None
    
    db_dividend.account_id = dividend.account_id
    db_dividend.year_month = dividend.year_month
    db_dividend.stock_code = dividend.stock_code
    db_dividend.dividend_amount = dividend.dividend_amount
    
    db.commit()
    db.refresh(db_dividend)
    return db_dividend

def delete_isa_account_dividend(db: Session, dividend_id: int):
    db_dividend = db.query(ISAAccountDividend).filter(ISAAccountDividend.id == dividend_id).first()
    if not db_dividend:
        return None
    db.delete(db_dividend)
    db.commit()
    return db_dividend

