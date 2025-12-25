from sqlalchemy import Column, Integer, String, Numeric, Enum as SQLEnum
from app.database import Base
import enum

class ExpenseType(str, enum.Enum):
    FIXED = "fixed"  # 고정비
    VARIABLE = "variable"  # 변동비

class Expense(Base):
    __tablename__ = "expense"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(ExpenseType), nullable=False, index=True)
    item = Column(String(200), nullable=False)  # 항목명
    amount = Column(Numeric(15, 0), nullable=False)  # 금액 (정수만)

