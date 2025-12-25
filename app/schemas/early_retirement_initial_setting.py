from pydantic import BaseModel, field_validator
from decimal import Decimal
from typing import Optional
from app.models.early_retirement_initial_setting import DividendOption

class EarlyRetirementInitialSettingBase(BaseModel):
    investable_assets: Decimal  # 투자가능자산
    standby_fund_ratio: Decimal  # 대기자금 비율 (%)
    standby_fund: Decimal  # 대기자금 (자동계산)
    dividend_option: DividendOption  # 배당옵션
    additional_required_assets: Optional[Decimal] = None  # 추가로 필요한 투입자산 (부족금액이 있을 때만)
    
    @field_validator('investable_assets', 'standby_fund_ratio', 'standby_fund', 'additional_required_assets')
    @classmethod
    def validate_integer_amount(cls, v):
        # None이면 None 반환
        if v is None:
            return None
        # 소수점 제거하여 정수로 변환
        if isinstance(v, Decimal):
            return Decimal(int(v))
        return Decimal(int(float(v)))
    
    # @field_validator('standby_fund_ratio')
    # @classmethod
    # def validate_standby_fund_ratio(cls, v):
    #     # 대기자금 비율은 소수점 2자리까지 허용
    #     if isinstance(v, Decimal):
    #         return v
    #     return Decimal(str(float(v)))

class EarlyRetirementInitialSettingCreate(EarlyRetirementInitialSettingBase):
    pass

class EarlyRetirementInitialSettingUpdate(EarlyRetirementInitialSettingBase):
    pass

class EarlyRetirementInitialSetting(EarlyRetirementInitialSettingBase):
    id: int
    
    class Config:
        from_attributes = True

