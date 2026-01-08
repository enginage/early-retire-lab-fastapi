from pydantic import BaseModel
from typing import Optional

class USAETFsBase(BaseModel):
    ticker: str
    name: str
    etf_type: Optional[str] = None

class USAETFsCreate(USAETFsBase):
    pass

class USAETFsUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    etf_type: Optional[str] = None

class USAETFs(USAETFsBase):
    id: int
    
    class Config:
        from_attributes = True

