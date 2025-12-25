from sqlalchemy import Column, Integer, String
from app.database import Base

class ExperienceLabStock(Base):
    __tablename__ = "experience_lab_stock"
    
    id = Column(Integer, primary_key=True, index=True)
    experience_service_code = Column(String(50), nullable=False, index=True)  # 체험실 업무코드
    ticker = Column(String(20), nullable=False, index=True)  # 종목코드(티커)

