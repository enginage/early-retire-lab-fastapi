from sqlalchemy import Column, Integer, String
from app.database import Base

class FinancialInstitution(Base):
    __tablename__ = "financial_institution"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(50), nullable=False, unique=True, index=True)

