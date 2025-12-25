from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.experience_lab_stock import ExperienceLabStock, ExperienceLabStockCreate, ExperienceLabStockUpdate
from app.crud import experience_lab_stock

router = APIRouter()

@router.get("/", response_model=List[ExperienceLabStock])
def read_experience_lab_stocks(
    skip: int = 0, 
    limit: int = 1000, 
    experience_service_code: Optional[str] = Query(None, description="체험실 업무코드로 필터링"),
    db: Session = Depends(get_db)
):
    stocks = experience_lab_stock.get_experience_lab_stocks(
        db, 
        skip=skip, 
        limit=limit, 
        experience_service_code=experience_service_code
    )
    return stocks

@router.get("/{stock_id}", response_model=ExperienceLabStock)
def read_experience_lab_stock(stock_id: int, db: Session = Depends(get_db)):
    db_stock = experience_lab_stock.get_experience_lab_stock(db, stock_id=stock_id)
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Experience lab stock not found")
    return db_stock

@router.post("/", response_model=ExperienceLabStock)
def create_experience_lab_stock(stock: ExperienceLabStockCreate, db: Session = Depends(get_db)):
    return experience_lab_stock.create_experience_lab_stock(db=db, stock=stock)

@router.put("/{stock_id}", response_model=ExperienceLabStock)
def update_experience_lab_stock(stock_id: int, stock: ExperienceLabStockUpdate, db: Session = Depends(get_db)):
    db_stock = experience_lab_stock.update_experience_lab_stock(db=db, stock_id=stock_id, stock=stock)
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Experience lab stock not found")
    return db_stock

@router.delete("/{stock_id}")
def delete_experience_lab_stock(stock_id: int, db: Session = Depends(get_db)):
    db_stock = experience_lab_stock.delete_experience_lab_stock(db=db, stock_id=stock_id)
    if db_stock is None:
        raise HTTPException(status_code=404, detail="Experience lab stock not found")
    return {"message": "Experience lab stock deleted successfully"}

