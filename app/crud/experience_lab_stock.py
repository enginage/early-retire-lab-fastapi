from sqlalchemy.orm import Session
from app.models.experience_lab_stock import ExperienceLabStock
from app.schemas.experience_lab_stock import ExperienceLabStockCreate, ExperienceLabStockUpdate

def get_experience_lab_stock(db: Session, stock_id: int):
    return db.query(ExperienceLabStock).filter(ExperienceLabStock.id == stock_id).first()

def get_experience_lab_stocks(db: Session, skip: int = 0, limit: int = 100, experience_service_code: str = None):
    query = db.query(ExperienceLabStock)
    if experience_service_code:
        query = query.filter(ExperienceLabStock.experience_service_code == experience_service_code)
    return query.offset(skip).limit(limit).all()

def create_experience_lab_stock(db: Session, stock: ExperienceLabStockCreate):
    db_stock = ExperienceLabStock(**stock.dict())
    db.add(db_stock)
    db.commit()
    db.refresh(db_stock)
    return db_stock

def update_experience_lab_stock(db: Session, stock_id: int, stock: ExperienceLabStockUpdate):
    db_stock = db.query(ExperienceLabStock).filter(ExperienceLabStock.id == stock_id).first()
    if db_stock:
        update_data = stock.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_stock, field, value)
        db.commit()
        db.refresh(db_stock)
    return db_stock

def delete_experience_lab_stock(db: Session, stock_id: int):
    db_stock = db.query(ExperienceLabStock).filter(ExperienceLabStock.id == stock_id).first()
    if db_stock:
        db.delete(db_stock)
        db.commit()
    return db_stock

