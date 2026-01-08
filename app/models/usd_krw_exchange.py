from sqlalchemy import Column, Integer, Date, Numeric
from app.database import Base

class USDKRWExchange(Base):
    __tablename__ = "usd_krw_exchange"
    __table_args__ = {'schema': 'basic'}
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, unique=True, index=True)  # 날짜 (unique 제약)
    exchange_rate = Column(Numeric(10, 2), nullable=False)  # 환율 (USD 1달러당 원화)

