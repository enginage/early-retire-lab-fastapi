from pydantic import BaseModel
from datetime import date
from typing import Optional

class DomesticETFsDividendBase(BaseModel):
    etf_id: int
    record_date: date
    payment_date: date
    dividend_amt: int  # 배당금액
    taxable_amt: int  # 주당과세표준액

class DomesticETFsDividendCreate(DomesticETFsDividendBase):
    pass

class DomesticETFsDividendUpdate(BaseModel):
    etf_id: Optional[int] = None
    record_date: Optional[date] = None
    payment_date: Optional[date] = None
    dividend_amt: Optional[int] = None
    taxable_amt: Optional[int] = None

class DomesticETFsDividend(DomesticETFsDividendBase):
    id: int
    
    class Config:
        from_attributes = True

