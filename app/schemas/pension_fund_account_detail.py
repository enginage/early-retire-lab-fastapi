from pydantic import BaseModel, field_validator
from decimal import Decimal
from typing import Optional

class PensionFundAccountDetailBase(BaseModel):
    account_id: int  # 연금저축펀드 계좌 ID
    stock_code: str  # 종목코드
    quantity: Decimal  # 수량
    purchase_avg_price: Decimal  # 매입단가(원화)
    current_price: Decimal  # 현재가(원화)
    purchase_fee: Decimal  # 매수수수료(원화)
    sale_fee: Decimal  # 매도수수료(원화)
    
    @field_validator('quantity', 'purchase_avg_price', 'current_price')
    @classmethod
    def validate_decimal_fields(cls, v):
        # 소수점 0자리까지 허용
        if isinstance(v, Decimal):
            return v
        return Decimal(str(float(v)))
    
    @field_validator('purchase_fee', 'sale_fee')
    @classmethod
    def validate_fee_fields(cls, v):
        # 소수점 제거하여 정수로 변환
        if isinstance(v, Decimal):
            return Decimal(int(v))
        return Decimal(int(float(v)))

class PensionFundAccountDetailCreate(PensionFundAccountDetailBase):
    pass

class PensionFundAccountDetailUpdate(PensionFundAccountDetailBase):
    pass

class PensionFundAccountDetail(PensionFundAccountDetailBase):
    id: int
    stock_name: Optional[str] = None  # 조인된 종목명 (응답용)
    
    class Config:
        from_attributes = True

