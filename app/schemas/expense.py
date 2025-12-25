from pydantic import BaseModel, field_validator
from decimal import Decimal
from app.models.expense import ExpenseType

class ExpenseBase(BaseModel):
    type: ExpenseType
    item: str
    amount: Decimal
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        # 소수점 제거하여 정수로 변환
        if isinstance(v, Decimal):
            return Decimal(int(v))
        return Decimal(int(float(v)))

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    pass

class Expense(ExpenseBase):
    id: int
    
    class Config:
        from_attributes = True

