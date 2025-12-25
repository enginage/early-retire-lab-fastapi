from sqlalchemy.orm import Session
from app.models.early_retirement_initial_setting import EarlyRetirementInitialSetting
from app.schemas.early_retirement_initial_setting import (
    EarlyRetirementInitialSettingCreate,
    EarlyRetirementInitialSettingUpdate
)

def get_early_retirement_initial_setting(db: Session):
    """단일 설정 조회 (id=1만 존재)"""
    return db.query(EarlyRetirementInitialSetting).filter(
        EarlyRetirementInitialSetting.id == 1
    ).first()

def create_or_update_early_retirement_initial_setting(
    db: Session,
    setting: EarlyRetirementInitialSettingCreate
):
    """설정이 있으면 업데이트, 없으면 생성"""
    db_setting = get_early_retirement_initial_setting(db)
    
    if db_setting:
        # 업데이트
        db_setting.investable_assets = setting.investable_assets
        db_setting.standby_fund_ratio = setting.standby_fund_ratio
        db_setting.standby_fund = setting.standby_fund
        db_setting.dividend_option = setting.dividend_option
        db_setting.additional_required_assets = setting.additional_required_assets
    else:
        # 생성 (id=1로 고정)
        db_setting = EarlyRetirementInitialSetting(
            id=1,
            investable_assets=setting.investable_assets,
            standby_fund_ratio=setting.standby_fund_ratio,
            standby_fund=setting.standby_fund,
            dividend_option=setting.dividend_option,
            additional_required_assets=setting.additional_required_assets
        )
        db.add(db_setting)
    
    db.commit()
    db.refresh(db_setting)
    return db_setting

