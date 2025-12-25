from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.isa_account_sale import ISAAccountSale, ISAAccountSaleCreate, ISAAccountSaleUpdate
from app.crud.isa_account_sale import (
    get_isa_account_sales as crud_get_all,
    get_isa_account_sale as crud_get_one,
    create_isa_account_sale as crud_create,
    update_isa_account_sale as crud_update,
    delete_isa_account_sale as crud_delete
)

router = APIRouter()

@router.get("/account/{account_id}", response_model=List[ISAAccountSale])
def read_isa_account_sales(
    account_id: int,
    year_month: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        sales = crud_get_all(db, account_id=account_id, year_month=year_month, skip=skip, limit=limit)
        return sales
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/{sale_id}", response_model=ISAAccountSale)
def read_isa_account_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = crud_get_one(db, sale_id=sale_id)
    if db_sale is None:
        raise HTTPException(status_code=404, detail="ISA 매도 내역을 찾을 수 없습니다")
    return db_sale

@router.post("/", response_model=ISAAccountSale, status_code=201)
def create_isa_account_sale(sale: ISAAccountSaleCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, sale=sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{sale_id}", response_model=ISAAccountSale)
def update_isa_account_sale(sale_id: int, sale: ISAAccountSaleUpdate, db: Session = Depends(get_db)):
    try:
        db_sale = crud_update(db=db, sale_id=sale_id, sale=sale)
        if db_sale is None:
            raise HTTPException(status_code=404, detail="ISA 매도 내역을 찾을 수 없습니다")
        return db_sale
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{sale_id}", status_code=204)
def delete_isa_account_sale(sale_id: int, db: Session = Depends(get_db)):
    db_sale = crud_delete(db=db, sale_id=sale_id)
    if db_sale is None:
        raise HTTPException(status_code=404, detail="ISA 매도 내역을 찾을 수 없습니다")
    return None

