from pydantic import BaseModel
from typing import Optional

class USAETFBase(BaseModel):
    ticker: str
    name: str

class USAETFCreate(USAETFBase):
    pass

class USAETFUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None

class USAETF(USAETFBase):
    id: int
    
    class Config:
        from_attributes = True

