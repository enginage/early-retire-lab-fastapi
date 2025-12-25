from sqlalchemy import Column, Integer, Numeric, Enum as SQLEnum
from app.database import Base
import enum

class DividendOption(str, enum.Enum):
    MEDIUM = "medium"  # 중배당 5%
    HIGH = "high"  # 고배당 10%
    ULTRA_HIGH = "ultra_high"  # 초고배당 20%

class EarlyRetirementInitialSetting(Base):
    __tablename__ = "early_retirement_initial_setting"
    
    id = Column(Integer, primary_key=True, index=True)
    investable_assets = Column(Numeric(15, 0), nullable=False)  # 투자가능자산
    standby_fund_ratio = Column(Numeric(5, 0), nullable=False)  # 대기자금(여유자금) 비율 (%)
    standby_fund = Column(Numeric(15, 0), nullable=False)  # 대기자금(여유자금) (자동계산)
    dividend_option = Column(SQLEnum(DividendOption), nullable=False)  # 배당옵션
    additional_required_assets = Column(Numeric(15, 0), nullable=True)  # 추가로 필요한 투입자산 (부족금액이 있을 때만)

