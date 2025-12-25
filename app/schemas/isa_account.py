from pydantic import BaseModel, field_validator
from decimal import Decimal
from datetime import date
from typing import List, Optional

class ISAAccountBase(BaseModel):
    financial_institution_code: str  # 금융기관코드
    account_number: str  # 계좌번호
    registration_date: Optional[date] = None  # 가입년월일
    cash_balance: Decimal  # 현금잔고
    account_status_code: Optional[str] = None  # 계좌상태코드
    non_tax_type: str  # 비과세유형
    
    @field_validator('cash_balance')
    @classmethod
    def validate_cash_balance(cls, v):
        # 소수점 제거하여 정수로 변환
        if isinstance(v, Decimal):
            return Decimal(int(v))
        return Decimal(int(float(v)))

class ISAAccountCreate(ISAAccountBase):
    pass

class ISAAccountUpdate(ISAAccountBase):
    pass

class ISAAccount(ISAAccountBase):
    id: int
    financial_institution_name: Optional[str] = None  # 금융기관명 (join 결과)
    
    class Config:
        from_attributes = True

class ISAAccountWithDetails(ISAAccount):
    details: List['ISAAccountDetail'] = []
    
    class Config:
        from_attributes = True

# 순환 참조 해결
from app.schemas.isa_account_detail import ISAAccountDetail
ISAAccountWithDetails.model_rebuild()

