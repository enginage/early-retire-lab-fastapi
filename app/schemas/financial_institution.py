from pydantic import BaseModel

class FinancialInstitutionBase(BaseModel):
    name: str
    code: str

class FinancialInstitutionCreate(FinancialInstitutionBase):
    pass

class FinancialInstitutionUpdate(FinancialInstitutionBase):
    pass

class FinancialInstitution(FinancialInstitutionBase):
    id: int
    
    class Config:
        from_attributes = True

