from pydantic import BaseModel, field_validator
from decimal import Decimal
from app.models.income_target import IncomeType

class IncomeTargetBase(BaseModel):
    type: IncomeType
    item: str
    amount: Decimal
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        # 소수점 제거하여 정수로 변환
        if isinstance(v, Decimal):
            return Decimal(int(v))
        return Decimal(int(float(v)))

class IncomeTargetCreate(IncomeTargetBase):
    pass

class IncomeTargetUpdate(IncomeTargetBase):
    pass

class IncomeTarget(IncomeTargetBase):
    id: int
    
    class Config:
        from_attributes = True

