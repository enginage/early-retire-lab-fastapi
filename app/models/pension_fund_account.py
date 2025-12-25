from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class PensionFundAccount(Base):
    __tablename__ = "pension_fund_account"
    
    id = Column(Integer, primary_key=True, index=True)
    financial_institution_code = Column(String(50), ForeignKey("financial_institution.code"), nullable=False)  # 금융기관코드
    account_number = Column(String(50), nullable=False)  # 계좌번호
    registration_date = Column(Date, nullable=True)  # 가입년월일
    cash_balance = Column(Numeric(15, 0), nullable=False, default=0)  # 현금잔고
    account_status_code = Column(String(50), nullable=False)  # 계좌상태코드
    
    # 관계 설정
    financial_institution = relationship("FinancialInstitution", foreign_keys=[financial_institution_code])
    details = relationship("PensionFundAccountDetail", back_populates="account", cascade="all, delete-orphan")

