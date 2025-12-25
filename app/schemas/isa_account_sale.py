from pydantic import BaseModel, field_validator
from decimal import Decimal
from typing import Optional

class ISAAccountSaleBase(BaseModel):
    account_id: int  # ISA 계좌 ID
    year_month: str  # 연월 (YYYY-MM)
    stock_code: str  # 종목코드
    sale_quantity: Decimal  # 매도수량
    purchase_price: Decimal  # 매입단가
    sale_price: Decimal  # 매도단가
    transaction_fee: Decimal  # 거래비용
    
    @field_validator('sale_quantity', 'purchase_price', 'sale_price')
    @classmethod
    def validate_decimal_fields(cls, v):
        if isinstance(v, Decimal):
            return v
        return Decimal(str(float(v)))
    
    @field_validator('transaction_fee')
    @classmethod
    def validate_fee_fields(cls, v):
        if isinstance(v, Decimal):
            return Decimal(int(v))
        return Decimal(int(float(v)))

class ISAAccountSaleCreate(ISAAccountSaleBase):
    pass

class ISAAccountSaleUpdate(ISAAccountSaleBase):
    pass

class ISAAccountSale(ISAAccountSaleBase):
    id: int
    profit_loss: Decimal  # 손익금액
    return_rate: Decimal  # 수익률
    stock_name: Optional[str] = None  # 조인된 종목명 (응답용)
    
    class Config:
        from_attributes = True

