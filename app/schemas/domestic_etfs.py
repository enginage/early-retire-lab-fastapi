from pydantic import BaseModel
from typing import Optional

class DomesticETFsBase(BaseModel):
    ticker: str
    name: str
    etf_type: Optional[str] = None
    etf_tax_type: Optional[str] = None

class DomesticETFsCreate(DomesticETFsBase):
    pass

class DomesticETFsUpdate(BaseModel):
    ticker: Optional[str] = None
    name: Optional[str] = None
    etf_type: Optional[str] = None
    etf_tax_type: Optional[str] = None

class DomesticETFs(DomesticETFsBase):
    id: int
    
    class Config:
        from_attributes = True


