from sqlalchemy.orm import Session
from app.models.income_target import IncomeTarget, IncomeType
from app.schemas.income_target import IncomeTargetCreate, IncomeTargetUpdate

def get_income_targets(db: Session, income_type: IncomeType = None, skip: int = 0, limit: int = 100):
    query = db.query(IncomeTarget)
    if income_type:
        query = query.filter(IncomeTarget.type == income_type)
    return query.offset(skip).limit(limit).all()

def get_income_target(db: Session, target_id: int):
    return db.query(IncomeTarget).filter(IncomeTarget.id == target_id).first()

def create_income_target(db: Session, target: IncomeTargetCreate):
    db_target = IncomeTarget(**target.model_dump())
    db.add(db_target)
    db.commit()
    db.refresh(db_target)
    return db_target

def update_income_target(db: Session, target_id: int, target: IncomeTargetUpdate):
    db_target = get_income_target(db, target_id)
    if not db_target:
        raise ValueError(f"소득 목표를 찾을 수 없습니다: {target_id}")
    
    db_target.type = target.type
    db_target.item = target.item
    db_target.amount = target.amount
    db.commit()
    db.refresh(db_target)
    return db_target

def delete_income_target(db: Session, target_id: int):
    db_target = get_income_target(db, target_id)
    if not db_target:
        raise ValueError(f"소득 목표를 찾을 수 없습니다: {target_id}")
    
    db.delete(db_target)
    db.commit()
    return db_target

