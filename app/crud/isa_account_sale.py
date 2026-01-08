from sqlalchemy.orm import Session
from sqlalchemy import join
from app.models.isa_account_sale import ISAAccountSale
from app.models.domestic_etfs import DomesticETFs
from app.schemas.isa_account_sale import ISAAccountSaleCreate, ISAAccountSaleUpdate
from decimal import Decimal

def get_isa_account_sales(db: Session, account_id: int, year_month: str = None, skip: int = 0, limit: int = 100):
    query = db.query(
        ISAAccountSale,
        DomesticETFs.name.label('etf_name')
    ).join(
        DomesticETFs,
        ISAAccountSale.stock_code == DomesticETFs.ticker,
        isouter=False  # INNER JOIN
    ).filter(
        ISAAccountSale.account_id == account_id
    )
    
    if year_month:
        query = query.filter(ISAAccountSale.year_month == year_month)
    
    results = query.offset(skip).limit(limit).all()
    
    # 조인된 결과를 ISAAccountSale 객체에 etf_name을 추가
    sales = []
    for sale, etf_name in results:
        sale.stock_name = etf_name
        sales.append(sale)
    
    return sales

def get_isa_account_sale(db: Session, sale_id: int):
    result = db.query(
        ISAAccountSale,
        DomesticETFs.name.label('etf_name')
    ).join(
        DomesticETFs,
        ISAAccountSale.stock_code == DomesticETFs.ticker,
        isouter=False  # INNER JOIN
    ).filter(
        ISAAccountSale.id == sale_id
    ).first()
    
    if result:
        sale, etf_name = result
        sale.stock_name = etf_name
        return sale
    return None

def create_isa_account_sale(db: Session, sale: ISAAccountSaleCreate):
    # 손익금액 계산: (매도단가 - 매입단가) * 매도수량 - 거래비용
    profit_loss = (sale.sale_price - sale.purchase_price) * sale.sale_quantity - sale.transaction_fee
    
    # 수익률 계산: ((매도단가 - 매입단가) / 매입단가) * 100
    if sale.purchase_price > 0:
        return_rate = ((sale.sale_price - sale.purchase_price) / sale.purchase_price) * Decimal('100')
    else:
        return_rate = Decimal('0')
    
    db_sale = ISAAccountSale(
        account_id=sale.account_id,
        year_month=sale.year_month,
        stock_code=sale.stock_code,
        sale_quantity=sale.sale_quantity,
        purchase_price=sale.purchase_price,
        sale_price=sale.sale_price,
        transaction_fee=sale.transaction_fee,
        profit_loss=Decimal(int(profit_loss)),
        return_rate=return_rate
    )
    db.add(db_sale)
    db.commit()
    db.refresh(db_sale)
    return db_sale

def update_isa_account_sale(db: Session, sale_id: int, sale: ISAAccountSaleUpdate):
    db_sale = db.query(ISAAccountSale).filter(ISAAccountSale.id == sale_id).first()
    if not db_sale:
        return None
    
    # 손익금액 계산
    profit_loss = (sale.sale_price - sale.purchase_price) * sale.sale_quantity - sale.transaction_fee
    
    # 수익률 계산
    if sale.purchase_price > 0:
        return_rate = ((sale.sale_price - sale.purchase_price) / sale.purchase_price) * Decimal('100')
    else:
        return_rate = Decimal('0')
    
    db_sale.account_id = sale.account_id
    db_sale.year_month = sale.year_month
    db_sale.stock_code = sale.stock_code
    db_sale.sale_quantity = sale.sale_quantity
    db_sale.purchase_price = sale.purchase_price
    db_sale.sale_price = sale.sale_price
    db_sale.transaction_fee = sale.transaction_fee
    db_sale.profit_loss = Decimal(int(profit_loss))
    db_sale.return_rate = return_rate
    
    db.commit()
    db.refresh(db_sale)
    return db_sale

def delete_isa_account_sale(db: Session, sale_id: int):
    db_sale = db.query(ISAAccountSale).filter(ISAAccountSale.id == sale_id).first()
    if not db_sale:
        return None
    db.delete(db_sale)
    db.commit()
    return db_sale

