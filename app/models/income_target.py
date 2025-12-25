from sqlalchemy import Column, Integer, String, Numeric, Enum as SQLEnum
from app.database import Base
import enum

class IncomeType(str, enum.Enum):
    STOCK_SALE = "stock_sale"  # 주식매도소득
    DIVIDEND = "dividend"  # 배당소득

class IncomeTarget(Base):
    __tablename__ = "income_target"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(IncomeType), nullable=False, index=True)
    item = Column(String(200), nullable=False)  # 항목명
    amount = Column(Numeric(15, 0), nullable=False)  # 금액 (정수만)

