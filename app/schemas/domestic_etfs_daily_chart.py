from pydantic import BaseModel
from datetime import date
from typing import Optional

class DomesticETFsDailyChartBase(BaseModel):
    etf_id: int
    date: date
    open: int  # 데이터베이스는 BigInteger(int8)이지만 Pydantic에서는 int 사용
    high: int
    low: int
    close: int
    volume: int

class DomesticETFsDailyChartCreate(DomesticETFsDailyChartBase):
    pass

class DomesticETFsDailyChartUpdate(BaseModel):
    etf_id: Optional[int] = None
    date: Optional[date] = None
    open: Optional[int] = None
    high: Optional[int] = None
    low: Optional[int] = None
    close: Optional[int] = None
    volume: Optional[int] = None

class DomesticETFsDailyChart(DomesticETFsDailyChartBase):
    id: int
    
    class Config:
        from_attributes = True

