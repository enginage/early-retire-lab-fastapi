from sqlalchemy.orm import Session
from sqlalchemy import join
from app.models.irp_account_detail import IRPAccountDetail
from app.models.domestic_etf import DomesticETF
from app.schemas.irp_account_detail import IRPAccountDetailCreate, IRPAccountDetailUpdate

def get_irp_account_details(db: Session, account_id: int, skip: int = 0, limit: int = 100):
    results = db.query(
        IRPAccountDetail,
        DomesticETF.name.label('etf_name')
    ).join(
        DomesticETF,
        IRPAccountDetail.stock_code == DomesticETF.ticker,
        isouter=False  # INNER JOIN
    ).filter(
        IRPAccountDetail.account_id == account_id
    ).offset(skip).limit(limit).all()
    
    # 조인된 결과를 IRPAccountDetail 객체에 etf_name을 추가
    details = []
    for detail, etf_name in results:
        detail.stock_name = etf_name  # 조인된 name을 stock_name에 할당
        details.append(detail)
    
    return details

def get_irp_account_detail(db: Session, detail_id: int):
    result = db.query(
        IRPAccountDetail,
        DomesticETF.name.label('etf_name')
    ).join(
        DomesticETF,
        IRPAccountDetail.stock_code == DomesticETF.ticker,
        isouter=False  # INNER JOIN
    ).filter(
        IRPAccountDetail.id == detail_id
    ).first()
    
    if result:
        detail, etf_name = result
        detail.stock_name = etf_name  # 조인된 name을 stock_name에 할당
        return detail
    return None

def get_irp_account_detail_by_stock_code(db: Session, account_id: int, stock_code: str):
    """account_id와 stock_code로 기존 레코드 찾기"""
    return db.query(IRPAccountDetail).filter(
        IRPAccountDetail.account_id == account_id,
        IRPAccountDetail.stock_code == stock_code
    ).first()

def create_irp_account_detail(db: Session, detail: IRPAccountDetailCreate):
    # stock_name은 제외하고 저장
    detail_dict = detail.model_dump()
    detail_dict.pop('stock_name', None)  # stock_name이 있으면 제거
    db_detail = IRPAccountDetail(**detail_dict)
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    # 조인된 name을 가져오기 위해 다시 조회
    return get_irp_account_detail(db, db_detail.id)

def update_irp_account_detail(db: Session, detail_id: int, detail: IRPAccountDetailUpdate):
    # 먼저 기존 데이터 조회 (조인 없이)
    db_detail = db.query(IRPAccountDetail).filter(IRPAccountDetail.id == detail_id).first()
    if not db_detail:
        raise ValueError(f"IRP 계좌 상세를 찾을 수 없습니다: {detail_id}")
    
    # stock_name은 제외하고 업데이트
    detail_dict = detail.model_dump()
    detail_dict.pop('stock_name', None)  # stock_name이 있으면 제거
    
    db_detail.account_id = detail_dict['account_id']
    db_detail.stock_code = detail_dict['stock_code']
    db_detail.quantity = detail_dict['quantity']
    db_detail.purchase_avg_price = detail_dict['purchase_avg_price']
    db_detail.current_price = detail_dict['current_price']
    db_detail.purchase_fee = detail_dict['purchase_fee']
    db_detail.sale_fee = detail_dict['sale_fee']
    db.commit()
    db.refresh(db_detail)
    # 조인된 name을 가져오기 위해 다시 조회
    return get_irp_account_detail(db, detail_id)

def delete_irp_account_detail(db: Session, detail_id: int):
    db_detail = get_irp_account_detail(db, detail_id)
    if not db_detail:
        raise ValueError(f"IRP 계좌 상세를 찾을 수 없습니다: {detail_id}")
    
    db.delete(db_detail)
    db.commit()
    return db_detail

