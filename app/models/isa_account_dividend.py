from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class ISAAccountDividend(Base):
    __tablename__ = "isa_account_dividend"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("isa_account.id"), nullable=False)  # ISA 계좌 ID
    year_month = Column(String(7), nullable=False)  # 연월 (YYYY-MM)
    stock_code = Column(String(20), nullable=False)  # 종목코드
    dividend_amount = Column(Numeric(15, 0), nullable=False, default=0)  # 배당금
    
    # 관계 설정
    account = relationship("ISAAccount", foreign_keys=[account_id])

