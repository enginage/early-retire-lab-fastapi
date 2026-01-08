from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.database import Base

class CommonCodeMaster(Base):
    __tablename__ = "common_code_master"
    __table_args__ = {'schema': 'basic'}
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), nullable=False, unique=True, index=True)  # 코드
    code_name = Column(String(200), nullable=False)  # 코드명
    remark = Column(String(500), nullable=True)  # 비고
    
    # 관계 설정
    details = relationship("CommonCodeDetail", back_populates="master", cascade="all, delete-orphan")


