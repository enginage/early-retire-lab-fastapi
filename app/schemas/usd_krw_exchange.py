from pydantic import BaseModel
from datetime import date
from typing import Optional
from decimal import Decimal

class USDKRWExchangeBase(BaseModel):
    date: date
    exchange_rate: Decimal

class USDKRWExchangeCreate(USDKRWExchangeBase):
    pass

class USDKRWExchangeUpdate(BaseModel):
    date: Optional[date] = None
    exchange_rate: Optional[Decimal] = None

class USDKRWExchange(USDKRWExchangeBase):
    id: int
    
    class Config:
        from_attributes = True

