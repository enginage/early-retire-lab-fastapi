from sqlalchemy.orm import Session
from app.models.common_code_detail import CommonCodeDetail
from app.schemas.common_code_detail import CommonCodeDetailCreate, CommonCodeDetailUpdate

def get_common_code_details(db: Session, master_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(CommonCodeDetail)
    if master_id:
        query = query.filter(CommonCodeDetail.master_id == master_id)
    return query.offset(skip).limit(limit).all()

def get_common_code_detail(db: Session, detail_id: int):
    return db.query(CommonCodeDetail).filter(CommonCodeDetail.id == detail_id).first()

def create_common_code_detail(db: Session, detail: CommonCodeDetailCreate):
    db_detail = CommonCodeDetail(**detail.model_dump())
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return db_detail

def update_common_code_detail(db: Session, detail_id: int, detail: CommonCodeDetailUpdate):
    db_detail = get_common_code_detail(db, detail_id)
    if not db_detail:
        raise ValueError(f"공통코드 상세를 찾을 수 없습니다: {detail_id}")
    
    db_detail.master_id = detail.master_id
    db_detail.detail_code = detail.detail_code
    db_detail.detail_code_name = detail.detail_code_name
    
    db.commit()
    db.refresh(db_detail)
    return db_detail

def delete_common_code_detail(db: Session, detail_id: int):
    db_detail = get_common_code_detail(db, detail_id)
    if not db_detail:
        raise ValueError(f"공통코드 상세를 찾을 수 없습니다: {detail_id}")
    
    db.delete(db_detail)
    db.commit()
    return db_detail

