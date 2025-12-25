from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.financial_institution import FinancialInstitution, FinancialInstitutionCreate, FinancialInstitutionUpdate
from app.crud.financial_institution import (
    get_financial_institutions as crud_get_all,
    get_financial_institution as crud_get_one,
    create_financial_institution as crud_create,
    update_financial_institution as crud_update,
    delete_financial_institution as crud_delete
)

router = APIRouter()

@router.get("/", response_model=List[FinancialInstitution])
def read_financial_institutions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    institutions = crud_get_all(db, skip=skip, limit=limit)
    return institutions

@router.get("/{institution_id}", response_model=FinancialInstitution)
def read_financial_institution(institution_id: int, db: Session = Depends(get_db)):
    db_institution = crud_get_one(db, institution_id=institution_id)
    if db_institution is None:
        raise HTTPException(status_code=404, detail="금융기관을 찾을 수 없습니다")
    return db_institution

@router.post("/", response_model=FinancialInstitution, status_code=201)
def create_financial_institution(institution: FinancialInstitutionCreate, db: Session = Depends(get_db)):
    try:
        return crud_create(db=db, institution=institution)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{institution_id}", response_model=FinancialInstitution)
def update_financial_institution(
    institution_id: int, 
    institution: FinancialInstitutionUpdate, 
    db: Session = Depends(get_db)
):
    try:
        return crud_update(db=db, institution_id=institution_id, institution=institution)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{institution_id}", status_code=204)
def delete_financial_institution(institution_id: int, db: Session = Depends(get_db)):
    try:
        crud_delete(db=db, institution_id=institution_id)
        return None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

