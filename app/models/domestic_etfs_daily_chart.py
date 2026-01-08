from sqlalchemy import Column, Integer, BigInteger, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class DomesticETFsDailyChart(Base):
    __tablename__ = "domestic_etfs_daily_chart"
    __table_args__ = {'schema': 'stock'}
    
    id = Column(Integer, primary_key=True, index=True)
    etf_id = Column(Integer, ForeignKey('stock.domestic_etfs.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(BigInteger, nullable=False)
    high = Column(BigInteger, nullable=False)
    low = Column(BigInteger, nullable=False)
    close = Column(BigInteger, nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # 관계 설정
    etf = relationship("DomesticETFs", backref="daily_charts")

