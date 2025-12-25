from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.income_target import IncomeTarget, IncomeTargetCreate, IncomeTargetUpdate
from app.models.income_target import IncomeType
from app.crud.income_target import (
    get_income_targets as crud_get_all,
    get_income_target as crud_get_one,
    create_income_target as crud_create,
    update_income_target as crud_update,
    delete_income_target as crud_delete
)

router = APIRouter()

@router.get("/", response_model=List[IncomeTarget])
def read_income_targets(
    income_type: IncomeType = Query(None, description="소득 유형 필터 (stock_sale/dividend)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    try:
        targets = crud_get_all(db, income_type=income_type, skip=skip, limit=limit)
        return targets
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/{target_id}", response_model=IncomeTarget)
def read_income_target(target_id: int, db: Session = Depends(get_db)):
    db_target = crud_get_one(db, target_id=target_id)
    if db_target is None:
        raise HTTPException(status_code=404, detail="소득 목표를 찾을 수 없습니다")
    return db_target

@router.post("/", response_model=IncomeTarget, status_code=201)
def create_income_target(target: IncomeTargetCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, target=target)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{target_id}", response_model=IncomeTarget)
def update_income_target(
    target_id: int,
    target: IncomeTargetUpdate,
    db: Session = Depends(get_db)
):
    try:
        return crud_update(db=db, target_id=target_id, target=target)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{target_id}", status_code=204)
def delete_income_target(target_id: int, db: Session = Depends(get_db)):
    try:
        crud_delete(db=db, target_id=target_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

