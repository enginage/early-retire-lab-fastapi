from pydantic import BaseModel
from typing import Optional
from decimal import Decimal

class USAIndicatorsBase(BaseModel):
    ticker: str
    indicator_nm: str
    order_no: int = 0
    weekly_macd_oscillator: Optional[Decimal] = None

class USAIndicatorsCreate(USAIndicatorsBase):
    pass

class USAIndicatorsUpdate(BaseModel):
    ticker: Optional[str] = None
    indicator_nm: Optional[str] = None
    order_no: Optional[int] = None
    weekly_macd_oscillator: Optional[Decimal] = None

class USAIndicators(USAIndicatorsBase):
    id: int
    
    class Config:
        from_attributes = True

