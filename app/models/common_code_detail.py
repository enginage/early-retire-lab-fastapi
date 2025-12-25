from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CommonCodeDetail(Base):
    __tablename__ = "common_code_detail"
    
    id = Column(Integer, primary_key=True, index=True)
    master_id = Column(Integer, ForeignKey("common_code_master.id"), nullable=False)  # 마스터 ID
    detail_code = Column(String(50), nullable=False)  # 상세코드
    detail_code_name = Column(String(200), nullable=False)  # 상세코드명
    
    # 관계 설정
    master = relationship("CommonCodeMaster", back_populates="details")

