from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.irp_account import IRPAccount
from app.models.financial_institution import FinancialInstitution
from app.schemas.irp_account import IRPAccountCreate, IRPAccountUpdate

def get_irp_accounts(db: Session, skip: int = 0, limit: int = 100):
    # 금융기관과 LEFT JOIN하여 금융기관명 포함 (금융기관이 없어도 오류 없음)
    try:
        accounts = db.query(
            IRPAccount,
            FinancialInstitution.name.label('financial_institution_name')
        ).outerjoin(
            FinancialInstitution,
            IRPAccount.financial_institution_code == FinancialInstitution.code
        ).offset(skip).limit(limit).all()
        
        # 결과를 IRPAccount 객체에 금융기관명 추가
        result = []
        for account, fi_name in accounts:
            # 동적 속성 추가 (금융기관이 없으면 None)
            account.financial_institution_name = fi_name if fi_name else None
            result.append(account)
        
        return result
    except Exception as e:
        # 테이블 구조가 아직 업데이트되지 않은 경우, 기존 방식으로 조회
        accounts = db.query(IRPAccount).offset(skip).limit(limit).all()
        for account in accounts:
            account.financial_institution_name = None
        return accounts

def get_irp_account(db: Session, account_id: int):
    try:
        account = db.query(
            IRPAccount,
            FinancialInstitution.name.label('financial_institution_name')
        ).outerjoin(
            FinancialInstitution,
            IRPAccount.financial_institution_code == FinancialInstitution.code
        ).filter(IRPAccount.id == account_id).first()
        
        if not account:
            return None
        
        account_obj, fi_name = account
        # 동적 속성 추가 (금융기관이 없으면 None)
        account_obj.financial_institution_name = fi_name if fi_name else None
        return account_obj
    except Exception as e:
        # 테이블 구조가 아직 업데이트되지 않은 경우, 기존 방식으로 조회
        account_obj = db.query(IRPAccount).filter(IRPAccount.id == account_id).first()
        if account_obj:
            account_obj.financial_institution_name = None
        return account_obj

def create_irp_account(db: Session, account: IRPAccountCreate):
    db_account = IRPAccount(**account.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    # 금융기관명 조회 (금융기관이 없어도 오류 없음)
    try:
        fi = db.query(FinancialInstitution).filter(
            FinancialInstitution.code == db_account.financial_institution_code
        ).first()
        if fi:
            db_account.financial_institution_name = fi.name
        else:
            db_account.financial_institution_name = None
    except Exception:
        db_account.financial_institution_name = None
    
    return db_account

def update_irp_account(db: Session, account_id: int, account: IRPAccountUpdate):
    try:
        db_account = get_irp_account(db, account_id)
    except Exception as e:
        # 테이블 구조가 아직 업데이트되지 않은 경우, 직접 조회
        db_account = db.query(IRPAccount).filter(IRPAccount.id == account_id).first()
    
    if not db_account:
        raise ValueError(f"IRP 계좌를 찾을 수 없습니다: {account_id}")
    
    db_account.financial_institution_code = account.financial_institution_code
    db_account.account_number = account.account_number
    db_account.registration_date = account.registration_date
    db_account.cash_balance = account.cash_balance
    db_account.account_status_code = account.account_status_code
    
    # 금융기관명 업데이트 (금융기관이 없어도 오류 없음)
    try:
        fi = db.query(FinancialInstitution).filter(
            FinancialInstitution.code == account.financial_institution_code
        ).first()
        if fi:
            db_account.financial_institution_name = fi.name
        else:
            db_account.financial_institution_name = None
    except Exception:
        db_account.financial_institution_name = None
    
    db.commit()
    db.refresh(db_account)
    return db_account

def delete_irp_account(db: Session, account_id: int):
    db_account = db.query(IRPAccount).filter(IRPAccount.id == account_id).first()
    if not db_account:
        raise ValueError(f"IRP 계좌를 찾을 수 없습니다: {account_id}")
    
    db.delete(db_account)
    db.commit()
    return db_account

