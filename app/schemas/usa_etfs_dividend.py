from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class USAETFsDividendBase(BaseModel):
    etf_id: int
    record_date: date
    dividend_amt: Decimal  # NUMERIC(10, 4)

class USAETFsDividendCreate(USAETFsDividendBase):
    pass

class USAETFsDividendUpdate(BaseModel):
    etf_id: Optional[int] = None
    record_date: Optional[date] = None
    dividend_amt: Optional[Decimal] = None

class USAETFsDividend(USAETFsDividendBase):
    id: int
    
    class Config:
        from_attributes = True

