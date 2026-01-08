from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class USAETFsDailyChartBase(BaseModel):
    etf_id: int
    date: date
    open: Decimal  # NUMERIC(10, 6)
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int  # BigInteger

class USAETFsDailyChartCreate(USAETFsDailyChartBase):
    pass

class USAETFsDailyChartUpdate(BaseModel):
    etf_id: Optional[int] = None
    date: Optional[date] = None
    open: Optional[Decimal] = None
    high: Optional[Decimal] = None
    low: Optional[Decimal] = None
    close: Optional[Decimal] = None
    volume: Optional[int] = None

class USAETFsDailyChart(USAETFsDailyChartBase):
    id: int
    
    class Config:
        from_attributes = True

