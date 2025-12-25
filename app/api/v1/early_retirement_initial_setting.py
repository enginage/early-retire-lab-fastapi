from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.early_retirement_initial_setting import (
    EarlyRetirementInitialSetting,
    EarlyRetirementInitialSettingCreate
)
from app.crud.early_retirement_initial_setting import (
    get_early_retirement_initial_setting as crud_get,
    create_or_update_early_retirement_initial_setting as crud_create_or_update
)

router = APIRouter()

@router.get("/", response_model=EarlyRetirementInitialSetting)
def read_early_retirement_initial_setting(db: Session = Depends(get_db)):
    """조기은퇴 초기설정 조회"""
    setting = crud_get(db)
    if setting is None:
        raise HTTPException(status_code=404, detail="조기은퇴 초기설정을 찾을 수 없습니다")
    return setting

@router.post("/", response_model=EarlyRetirementInitialSetting, status_code=201)
@router.put("/", response_model=EarlyRetirementInitialSetting)
def create_or_update_early_retirement_initial_setting(
    setting: EarlyRetirementInitialSettingCreate,
    db: Session = Depends(get_db)
):
    """조기은퇴 초기설정 생성 또는 업데이트"""
    try:
        return crud_create_or_update(db=db, setting=setting)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(e)}")

