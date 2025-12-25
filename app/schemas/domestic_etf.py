from pydantic import BaseModel
from typing import Optional

class DomesticETFBase(BaseModel):
    ticker: str
    name: str

class DomesticETFCreate(DomesticETFBase):
    pass

class DomesticETFUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None

class DomesticETF(DomesticETFBase):
    id: int
    
    class Config:
        from_attributes = True


