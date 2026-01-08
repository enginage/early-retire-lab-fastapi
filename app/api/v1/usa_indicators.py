from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.usa_indicators import USAIndicators, USAIndicatorsCreate, USAIndicatorsUpdate
from app.crud import usa_indicators

router = APIRouter()

@router.get("/", response_model=List[USAIndicators])
def read_usa_indicators(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    indicators = usa_indicators.get_usa_indicators(db, skip=skip, limit=limit)
    return indicators

@router.get("/{indicator_id}", response_model=USAIndicators)
def read_usa_indicator(indicator_id: int, db: Session = Depends(get_db)):
    db_indicator = usa_indicators.get_usa_indicator(db, indicator_id=indicator_id)
    if db_indicator is None:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return db_indicator

@router.post("/", response_model=USAIndicators)
def create_usa_indicator(indicator: USAIndicatorsCreate, db: Session = Depends(get_db)):
    return usa_indicators.create_usa_indicator(db=db, indicator=indicator)

@router.put("/{indicator_id}", response_model=USAIndicators)
def update_usa_indicator(indicator_id: int, indicator: USAIndicatorsUpdate, db: Session = Depends(get_db)):
    db_indicator = usa_indicators.update_usa_indicator(db=db, indicator_id=indicator_id, indicator=indicator)
    if db_indicator is None:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return db_indicator

@router.delete("/{indicator_id}")
def delete_usa_indicator(indicator_id: int, db: Session = Depends(get_db)):
    db_indicator = usa_indicators.delete_usa_indicator(db=db, indicator_id=indicator_id)
    if db_indicator is None:
        raise HTTPException(status_code=404, detail="Indicator not found")
    return {"message": "Indicator deleted successfully"}

