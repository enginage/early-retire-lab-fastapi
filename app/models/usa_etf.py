from sqlalchemy import Column, Integer, String
from app.database import Base

class USAETF(Base):
    __tablename__ = "usa_etf"
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)  # 종목코드
    name = Column(String(200), nullable=False)  # 종목명

