from pydantic import BaseModel, field_validator
from decimal import Decimal
from typing import Optional

class ISAAccountDividendBase(BaseModel):
    account_id: int  # ISA 계좌 ID
    year_month: str  # 연월 (YYYY-MM)
    stock_code: str  # 종목코드
    dividend_amount: Decimal  # 배당금
    
    @field_validator('dividend_amount')
    @classmethod
    def validate_dividend_fields(cls, v):
        if isinstance(v, Decimal):
            return Decimal(int(v))
        return Decimal(int(float(v)))

class ISAAccountDividendCreate(ISAAccountDividendBase):
    pass

class ISAAccountDividendUpdate(ISAAccountDividendBase):
    pass

class ISAAccountDividend(ISAAccountDividendBase):
    id: int
    stock_name: Optional[str] = None  # 조인된 종목명 (응답용)
    
    class Config:
        from_attributes = True

