from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.irp_account import IRPAccount, IRPAccountCreate, IRPAccountUpdate
from app.crud.irp_account import (
    get_irp_accounts as crud_get_all,
    get_irp_account as crud_get_one,
    create_irp_account as crud_create,
    update_irp_account as crud_update,
    delete_irp_account as crud_delete
)

router = APIRouter()

@router.get("/", response_model=List[IRPAccount])
def read_irp_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        accounts = crud_get_all(db, skip=skip, limit=limit)
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/{account_id}", response_model=IRPAccount)
def read_irp_account(account_id: int, db: Session = Depends(get_db)):
    account = crud_get_one(db, account_id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="IRP 계좌를 찾을 수 없습니다")
    return account

@router.post("/", response_model=IRPAccount, status_code=201)
def create_irp_account(account: IRPAccountCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, account=account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{account_id}", response_model=IRPAccount)
def update_irp_account(
    account_id: int,
    account: IRPAccountUpdate,
    db: Session = Depends(get_db)
):
    try:
        return crud_update(db=db, account_id=account_id, account=account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{account_id}", status_code=204)
def delete_irp_account(account_id: int, db: Session = Depends(get_db)):
    try:
        crud_delete(db=db, account_id=account_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

