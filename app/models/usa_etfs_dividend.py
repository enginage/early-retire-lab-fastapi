from sqlalchemy import Column, Integer, Date, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class USAETFsDividend(Base):
    __tablename__ = "usa_etfs_dividend"
    __table_args__ = {'schema': 'stock'}
    
    id = Column(Integer, primary_key=True, index=True)
    etf_id = Column(Integer, ForeignKey('stock.usa_etfs.id'), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)  # 기준일자
    dividend_amt = Column(Numeric(10, 4), nullable=False)  # 배당금액
    
    # 관계 설정
    etf = relationship("USAETFs", backref="dividends")

