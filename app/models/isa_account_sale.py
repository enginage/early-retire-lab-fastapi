from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.database import Base

class ISAAccountSale(Base):
    __tablename__ = "isa_account_sale"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("isa_account.id"), nullable=False)  # ISA 계좌 ID
    year_month = Column(String(7), nullable=False)  # 연월 (YYYY-MM)
    stock_code = Column(String(20), nullable=False)  # 종목코드
    sale_quantity = Column(Numeric(15, 2), nullable=False)  # 매도수량
    purchase_price = Column(Numeric(15, 2), nullable=False)  # 매입단가
    sale_price = Column(Numeric(15, 2), nullable=False)  # 매도단가
    transaction_fee = Column(Numeric(15, 0), nullable=False, default=0)  # 거래비용
    profit_loss = Column(Numeric(15, 0), nullable=False, default=0)  # 손익금액
    return_rate = Column(Numeric(10, 4), nullable=False, default=0)  # 수익률
    
    # 관계 설정
    account = relationship("ISAAccount", foreign_keys=[account_id])

