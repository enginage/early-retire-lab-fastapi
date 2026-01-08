from sqlalchemy import Column, Integer, String
from app.database import Base

class DomesticETFs(Base):
    __tablename__ = "domestic_etfs"
    __table_args__ = {'schema': 'stock'}
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)  # 종목코드
    name = Column(String(200), nullable=False)  # 종목명
    etf_type = Column(String(50), nullable=True)  # ETF 유형 (공통코드)
    etf_tax_type = Column(String(50), nullable=True)  # 과세유형 (공통코드)


