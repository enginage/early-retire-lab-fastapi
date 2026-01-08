from sqlalchemy import Column, Integer, Date, BigInteger, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DomesticETFsDividend(Base):
    __tablename__ = "domestic_etfs_dividend"
    __table_args__ = {'schema': 'stock'}
    
    id = Column(Integer, primary_key=True, index=True)
    etf_id = Column(Integer, ForeignKey('stock.domestic_etfs.id'), nullable=False, index=True)
    record_date = Column(Date, nullable=False, index=True)  # 기준일자 (etf_id와 함께 unique)
    payment_date = Column(Date, nullable=False)  # 실지급일자
    dividend_amt = Column(BigInteger, nullable=False)  # 배당금액
    taxable_amt = Column(BigInteger, nullable=False)  # 주당과세표준액

    # 관계 설정
    etf = relationship("DomesticETFs", backref="dividends")

