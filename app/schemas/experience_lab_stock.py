from pydantic import BaseModel
from typing import Optional

class ExperienceLabStockBase(BaseModel):
    experience_service_code: str
    ticker: str

class ExperienceLabStockCreate(ExperienceLabStockBase):
    pass

class ExperienceLabStockUpdate(BaseModel):
    experience_service_code: Optional[str] = None
    ticker: Optional[str] = None

class ExperienceLabStock(ExperienceLabStockBase):
    id: int
    
    class Config:
        from_attributes = True

