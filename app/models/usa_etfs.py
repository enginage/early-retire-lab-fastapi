from sqlalchemy import Column, Integer, String
from app.database import Base

class USAETFs(Base):
    __tablename__ = "usa_etfs"
    __table_args__ = {'schema': 'stock'}
    
    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String(20), unique=True, nullable=False, index=True)  # 종목코드
    name = Column(String(200), nullable=False)  # 종목명
    etf_type = Column(String(50), nullable=True)  # ETF 유형 (공통코드)

