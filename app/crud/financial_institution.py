from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.financial_institution import FinancialInstitution
from app.schemas.financial_institution import FinancialInstitutionCreate, FinancialInstitutionUpdate

def get_financial_institutions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(FinancialInstitution).offset(skip).limit(limit).all()

def get_financial_institution(db: Session, institution_id: int):
    return db.query(FinancialInstitution).filter(FinancialInstitution.id == institution_id).first()

def get_financial_institution_by_code(db: Session, code: str):
    return db.query(FinancialInstitution).filter(FinancialInstitution.code == code).first()

def create_financial_institution(db: Session, institution: FinancialInstitutionCreate):
    # 코드 중복 확인
    existing = get_financial_institution_by_code(db, institution.code)
    if existing:
        raise ValueError(f"이미 존재하는 코드입니다: {institution.code}")
    
    db_institution = FinancialInstitution(**institution.model_dump())
    db.add(db_institution)
    db.commit()
    db.refresh(db_institution)
    return db_institution

def update_financial_institution(db: Session, institution_id: int, institution: FinancialInstitutionUpdate):
    db_institution = get_financial_institution(db, institution_id)
    if not db_institution:
        raise ValueError(f"금융기관을 찾을 수 없습니다: {institution_id}")
    
    # 코드가 변경되었고, 새 코드가 이미 존재하는지 확인
    if db_institution.code != institution.code:
        existing = get_financial_institution_by_code(db, institution.code)
        if existing:
            raise ValueError(f"이미 존재하는 코드입니다: {institution.code}")
    
    db_institution.name = institution.name
    db_institution.code = institution.code
    db.commit()
    db.refresh(db_institution)
    return db_institution

def delete_financial_institution(db: Session, institution_id: int):
    db_institution = get_financial_institution(db, institution_id)
    if not db_institution:
        raise ValueError(f"금융기관을 찾을 수 없습니다: {institution_id}")
    
    db.delete(db_institution)
    db.commit()
    return db_institution

