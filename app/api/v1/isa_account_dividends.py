from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.isa_account_dividend import ISAAccountDividend, ISAAccountDividendCreate, ISAAccountDividendUpdate
from app.crud.isa_account_dividend import (
    get_isa_account_dividends as crud_get_all,
    get_isa_account_dividend as crud_get_one,
    create_isa_account_dividend as crud_create,
    update_isa_account_dividend as crud_update,
    delete_isa_account_dividend as crud_delete
)

router = APIRouter()

@router.get("/account/{account_id}", response_model=List[ISAAccountDividend])
def read_isa_account_dividends(
    account_id: int,
    year_month: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        dividends = crud_get_all(db, account_id=account_id, year_month=year_month, skip=skip, limit=limit)
        return dividends
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/{dividend_id}", response_model=ISAAccountDividend)
def read_isa_account_dividend(dividend_id: int, db: Session = Depends(get_db)):
    db_dividend = crud_get_one(db, dividend_id=dividend_id)
    if db_dividend is None:
        raise HTTPException(status_code=404, detail="ISA 배당 내역을 찾을 수 없습니다")
    return db_dividend

@router.post("/", response_model=ISAAccountDividend, status_code=201)
def create_isa_account_dividend(dividend: ISAAccountDividendCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, dividend=dividend)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{dividend_id}", response_model=ISAAccountDividend)
def update_isa_account_dividend(dividend_id: int, dividend: ISAAccountDividendUpdate, db: Session = Depends(get_db)):
    try:
        db_dividend = crud_update(db=db, dividend_id=dividend_id, dividend=dividend)
        if db_dividend is None:
            raise HTTPException(status_code=404, detail="ISA 배당 내역을 찾을 수 없습니다")
        return db_dividend
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{dividend_id}", status_code=204)
def delete_isa_account_dividend(dividend_id: int, db: Session = Depends(get_db)):
    db_dividend = crud_delete(db=db, dividend_id=dividend_id)
    if db_dividend is None:
        raise HTTPException(status_code=404, detail="ISA 배당 내역을 찾을 수 없습니다")
    return None

