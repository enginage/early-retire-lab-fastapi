from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.expense import Expense, ExpenseCreate, ExpenseUpdate
from app.models.expense import ExpenseType
from app.crud.expense import (
    get_expenses as crud_get_all,
    get_expense as crud_get_one,
    create_expense as crud_create,
    update_expense as crud_update,
    delete_expense as crud_delete
)

router = APIRouter()

@router.get("/", response_model=List[Expense])
def read_expenses(
    expense_type: ExpenseType = Query(None, description="지출 유형 필터 (fixed/variable)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    try:
        expenses = crud_get_all(db, expense_type=expense_type, skip=skip, limit=limit)
        return expenses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/{expense_id}", response_model=Expense)
def read_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = crud_get_one(db, expense_id=expense_id)
    if db_expense is None:
        raise HTTPException(status_code=404, detail="지출 항목을 찾을 수 없습니다")
    return db_expense

@router.post("/", response_model=Expense, status_code=201)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, expense=expense)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{expense_id}", response_model=Expense)
def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db)
):
    try:
        return crud_update(db=db, expense_id=expense_id, expense=expense)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    try:
        crud_delete(db=db, expense_id=expense_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

