from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.isa_account import ISAAccount, ISAAccountCreate, ISAAccountUpdate, ISAAccountWithDetails
from app.crud.isa_account import (
    get_isa_accounts as crud_get_all,
    get_isa_account as crud_get_one,
    create_isa_account as crud_create,
    update_isa_account as crud_update,
    delete_isa_account as crud_delete
)

router = APIRouter()

@router.get("/", response_model=List[ISAAccount])
def read_isa_accounts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        accounts = crud_get_all(db, skip=skip, limit=limit)
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/{account_id}", response_model=ISAAccountWithDetails)
def read_isa_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud_get_one(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="ISA 계좌를 찾을 수 없습니다")
    return db_account

@router.post("/", response_model=ISAAccount, status_code=201)
def create_isa_account(account: ISAAccountCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, account=account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{account_id}", response_model=ISAAccount)
def update_isa_account(
    account_id: int,
    account: ISAAccountUpdate,
    db: Session = Depends(get_db)
):
    try:
        return crud_update(db=db, account_id=account_id, account=account)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{account_id}", status_code=204)
def delete_isa_account(account_id: int, db: Session = Depends(get_db)):
    try:
        crud_delete(db=db, account_id=account_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


