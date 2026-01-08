from sqlalchemy import Column, Integer, String, Numeric
from app.database import Base

class USAIndicators(Base):
    __tablename__ = "usa_indicators"
    __table_args__ = {'schema': 'basic'}
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), nullable=False, index=True)  # 종목코드(티커)
    indicator_nm = Column(String(200), nullable=False)  # 지표명
    order_no = Column(Integer, nullable=False, default=0)  # 정렬순서
    weekly_macd_oscillator = Column(Numeric(10, 4), nullable=True)  # 주봉MACD오실레이터

