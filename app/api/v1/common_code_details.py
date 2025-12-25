from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.common_code_detail import CommonCodeDetail, CommonCodeDetailCreate, CommonCodeDetailUpdate
from app.crud.common_code_detail import (
    get_common_code_details as crud_get_all,
    get_common_code_detail as crud_get_one,
    create_common_code_detail as crud_create,
    update_common_code_detail as crud_update,
    delete_common_code_detail as crud_delete
)

router = APIRouter()

@router.get("/", response_model=List[CommonCodeDetail])
def read_common_code_details(
    master_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    try:
        details = crud_get_all(db, master_id=master_id, skip=skip, limit=limit)
        return details
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

@router.get("/{detail_id}", response_model=CommonCodeDetail)
def read_common_code_detail(detail_id: int, db: Session = Depends(get_db)):
    db_detail = crud_get_one(db, detail_id=detail_id)
    if db_detail is None:
        raise HTTPException(status_code=404, detail="공통코드 상세를 찾을 수 없습니다")
    return db_detail

@router.post("/", response_model=CommonCodeDetail, status_code=201)
def create_common_code_detail(detail: CommonCodeDetailCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, detail=detail)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{detail_id}", response_model=CommonCodeDetail)
def update_common_code_detail(
    detail_id: int,
    detail: CommonCodeDetailUpdate,
    db: Session = Depends(get_db)
):
    try:
        return crud_update(db=db, detail_id=detail_id, detail=detail)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{detail_id}", status_code=204)
def delete_common_code_detail(detail_id: int, db: Session = Depends(get_db)):
    try:
        crud_delete(db=db, detail_id=detail_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

