from sqlalchemy.orm import Session
from sqlalchemy import join
from app.models.pension_fund_account_detail import PensionFundAccountDetail
from app.models.domestic_etfs import DomesticETFs
from app.schemas.pension_fund_account_detail import PensionFundAccountDetailCreate, PensionFundAccountDetailUpdate

def get_pension_fund_account_details(db: Session, account_id: int, skip: int = 0, limit: int = 100):
    results = db.query(
        PensionFundAccountDetail,
        DomesticETFs.name.label('etf_name')
    ).join(
        DomesticETFs,
        PensionFundAccountDetail.stock_code == DomesticETFs.ticker,
        isouter=False  # INNER JOIN
    ).filter(
        PensionFundAccountDetail.account_id == account_id
    ).offset(skip).limit(limit).all()
    
    # 조인된 결과를 PensionFundAccountDetail 객체에 etf_name을 추가
    details = []
    for detail, etf_name in results:
        detail.stock_name = etf_name  # 조인된 name을 stock_name에 할당
        details.append(detail)
    
    return details

def get_pension_fund_account_detail(db: Session, detail_id: int):
    result = db.query(
        PensionFundAccountDetail,
        DomesticETFs.name.label('etf_name')
    ).join(
        DomesticETFs,
        PensionFundAccountDetail.stock_code == DomesticETFs.ticker,
        isouter=False  # INNER JOIN
    ).filter(
        PensionFundAccountDetail.id == detail_id
    ).first()
    
    if result:
        detail, etf_name = result
        detail.stock_name = etf_name  # 조인된 name을 stock_name에 할당
        return detail
    return None

def get_pension_fund_account_detail_by_stock_code(db: Session, account_id: int, stock_code: str):
    """account_id와 stock_code로 기존 레코드 찾기"""
    return db.query(PensionFundAccountDetail).filter(
        PensionFundAccountDetail.account_id == account_id,
        PensionFundAccountDetail.stock_code == stock_code
    ).first()

def create_pension_fund_account_detail(db: Session, detail: PensionFundAccountDetailCreate):
    # stock_name은 제외하고 저장
    detail_dict = detail.model_dump()
    detail_dict.pop('stock_name', None)  # stock_name이 있으면 제거
    db_detail = PensionFundAccountDetail(**detail_dict)
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    # 조인된 name을 가져오기 위해 다시 조회
    return get_pension_fund_account_detail(db, db_detail.id)

def update_pension_fund_account_detail(db: Session, detail_id: int, detail: PensionFundAccountDetailUpdate):
    # 먼저 기존 데이터 조회 (조인 없이)
    db_detail = db.query(PensionFundAccountDetail).filter(PensionFundAccountDetail.id == detail_id).first()
    if not db_detail:
        raise ValueError(f"연금저축펀드 계좌 상세를 찾을 수 없습니다: {detail_id}")
    
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
    return get_pension_fund_account_detail(db, detail_id)

def delete_pension_fund_account_detail(db: Session, detail_id: int):
    db_detail = get_pension_fund_account_detail(db, detail_id)
    if not db_detail:
        raise ValueError(f"연금저축펀드 계좌 상세를 찾을 수 없습니다: {detail_id}")
    
    db.delete(db_detail)
    db.commit()
    return db_detail

