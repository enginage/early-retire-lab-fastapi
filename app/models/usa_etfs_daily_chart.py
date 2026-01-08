from sqlalchemy import Column, Integer, Numeric, BigInteger, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class USAETFsDailyChart(Base):
    __tablename__ = "usa_etfs_daily_chart"
    __table_args__ = {'schema': 'stock'}
    
    id = Column(Integer, primary_key=True, index=True)
    etf_id = Column(Integer, ForeignKey('stock.usa_etfs.id'), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 6), nullable=False)
    high = Column(Numeric(10, 6), nullable=False)
    low = Column(Numeric(10, 6), nullable=False)
    close = Column(Numeric(10, 6), nullable=False)
    volume = Column(BigInteger, nullable=False)
    
    # 관계 설정
    etf = relationship("USAETFs", backref="daily_charts")

