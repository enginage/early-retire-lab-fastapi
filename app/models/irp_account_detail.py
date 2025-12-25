from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class IRPAccountDetail(Base):
    __tablename__ = "irp_account_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("irp_account.id"), nullable=False)  # IRP 계좌 ID
    stock_code = Column(String(20), nullable=False)  # 종목코드
    quantity = Column(Numeric(15, 0), nullable=False)  # 수량
    purchase_avg_price = Column(Numeric(15, 0), nullable=False)  # 매입단가(원화)
    current_price = Column(Numeric(15, 0), nullable=False)  # 현재가(원화)
    purchase_fee = Column(Numeric(15, 0), nullable=False, default=0)  # 매수수수료(원화)
    sale_fee = Column(Numeric(15, 0), nullable=False, default=0)  # 매도수수료(원화)
    
    # 관계 설정
    account = relationship("IRPAccount", back_populates="details")

