from sqlalchemy.orm import Session
from app.models.common_code_master import CommonCodeMaster
from app.schemas.common_code_master import CommonCodeMasterCreate, CommonCodeMasterUpdate

def get_common_code_masters(db: Session, skip: int = 0, limit: int = 100):
    return db.query(CommonCodeMaster).offset(skip).limit(limit).all()

def get_common_code_master(db: Session, master_id: int):
    return db.query(CommonCodeMaster).filter(CommonCodeMaster.id == master_id).first()

def get_common_code_master_by_code(db: Session, code: str):
    return db.query(CommonCodeMaster).filter(CommonCodeMaster.code == code).first()

def create_common_code_master(db: Session, master: CommonCodeMasterCreate):
    db_master = CommonCodeMaster(**master.model_dump())
    db.add(db_master)
    db.commit()
    db.refresh(db_master)
    return db_master

def update_common_code_master(db: Session, master_id: int, master: CommonCodeMasterUpdate):
    db_master = get_common_code_master(db, master_id)
    if not db_master:
        raise ValueError(f"마스터 코드가 존재하지 않습니다: {master_id}")
    
    db_master.code = master.code
    db_master.code_name = master.code_name
    db_master.remark = master.remark
    
    db.commit()
    db.refresh(db_master)
    return db_master

def delete_common_code_master(db: Session, master_id: int):
    db_master = get_common_code_master(db, master_id)
    if not db_master:
        raise ValueError(f"마스터 코드가 존재하지 않습니다: {master_id}")
    
    db.delete(db_master)
    db.commit()
    return db_master


