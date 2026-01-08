from sqlalchemy.orm import Session
from app.models.usa_indicators import USAIndicators
from app.schemas.usa_indicators import USAIndicatorsCreate, USAIndicatorsUpdate

def get_usa_indicator(db: Session, indicator_id: int):
    return db.query(USAIndicators).filter(USAIndicators.id == indicator_id).first()

def get_usa_indicators(db: Session, skip: int = 0, limit: int = 100):
    return db.query(USAIndicators).order_by(USAIndicators.order_no.asc(), USAIndicators.id.asc()).offset(skip).limit(limit).all()

def create_usa_indicator(db: Session, indicator: USAIndicatorsCreate):
    db_indicator = USAIndicators(**indicator.model_dump())
    db.add(db_indicator)
    db.commit()
    db.refresh(db_indicator)
    return db_indicator

def update_usa_indicator(db: Session, indicator_id: int, indicator: USAIndicatorsUpdate):
    db_indicator = db.query(USAIndicators).filter(USAIndicators.id == indicator_id).first()
    if db_indicator:
        update_data = indicator.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_indicator, field, value)
        db.commit()
        db.refresh(db_indicator)
    return db_indicator

def delete_usa_indicator(db: Session, indicator_id: int):
    db_indicator = db.query(USAIndicators).filter(USAIndicators.id == indicator_id).first()
    if db_indicator:
        db.delete(db_indicator)
        db.commit()
    return db_indicator

