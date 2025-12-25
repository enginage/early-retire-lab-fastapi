from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.common_code_master import CommonCodeMaster, CommonCodeMasterCreate, CommonCodeMasterUpdate
from app.crud.common_code_master import (
    get_common_code_masters as crud_get_all,
    get_common_code_master as crud_get_one,
    create_common_code_master as crud_create,
    update_common_code_master as crud_update,
    delete_common_code_master as crud_delete
)

router = APIRouter()

@router.get("/", response_model=List[CommonCodeMaster])
def read_common_code_masters(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        masters = crud_get_all(db, skip=skip, limit=limit)
        return masters
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/{master_id}", response_model=CommonCodeMaster)
def read_common_code_master(master_id: int, db: Session = Depends(get_db)):
    db_master = crud_get_one(db, master_id=master_id)
    if db_master is None:
        raise HTTPException(status_code=404, detail="마스터 코드가 존재하지 않습니다")
    return db_master

@router.post("/", response_model=CommonCodeMaster, status_code=201)
def create_common_code_master(master: CommonCodeMasterCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, master=master)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{master_id}", response_model=CommonCodeMaster)
def update_common_code_master(
    master_id: int,
    master: CommonCodeMasterUpdate,
    db: Session = Depends(get_db)
):
    try:
        return crud_update(db=db, master_id=master_id, master=master)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{master_id}", status_code=204)
def delete_common_code_master(master_id: int, db: Session = Depends(get_db)):
    try:
        crud_delete(db=db, master_id=master_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


