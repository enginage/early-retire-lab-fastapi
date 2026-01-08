from sqlalchemy.orm import Session
from app.models.domestic_etfs_daily_chart import DomesticETFsDailyChart
from app.schemas.domestic_etfs_daily_chart import DomesticETFsDailyChartCreate, DomesticETFsDailyChartUpdate

def get_domestic_etf_daily_chart(db: Session, chart_id: int):
    return db.query(DomesticETFsDailyChart).filter(DomesticETFsDailyChart.id == chart_id).first()

def get_domestic_etf_daily_charts_by_etf_id(db: Session, etf_id: int, skip: int = 0, limit: int = 100):
    return db.query(DomesticETFsDailyChart).filter(DomesticETFsDailyChart.etf_id == etf_id).order_by(DomesticETFsDailyChart.date.desc()).offset(skip).limit(limit).all()

def get_domestic_etf_daily_charts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DomesticETFsDailyChart).offset(skip).limit(limit).all()

def create_domestic_etf_daily_chart(db: Session, chart: DomesticETFsDailyChartCreate):
    db_chart = DomesticETFsDailyChart(**chart.model_dump())
    db.add(db_chart)
    db.commit()
    db.refresh(db_chart)
    return db_chart

def bulk_create_domestic_etf_daily_charts(db: Session, charts: list):
    """여러 일봉 차트 데이터를 한 번에 생성"""
    created_count = 0
    for chart_data in charts:
        db_chart = DomesticETFsDailyChart(**chart_data)
        db.add(db_chart)
        created_count += 1
    db.commit()
    return created_count

def get_domestic_etf_daily_chart_by_etf_and_date(db: Session, etf_id: int, date):
    """etf_id와 date로 일봉 차트 데이터 조회"""
    return db.query(DomesticETFsDailyChart).filter(
        DomesticETFsDailyChart.etf_id == etf_id,
        DomesticETFsDailyChart.date == date
    ).first()

def get_latest_domestic_etf_daily_chart(db: Session, etf_id: int):
    """etf_id의 가장 최근 일봉 차트 데이터 조회"""
    return db.query(DomesticETFsDailyChart).filter(
        DomesticETFsDailyChart.etf_id == etf_id
    ).order_by(DomesticETFsDailyChart.date.desc()).first()

def get_domestic_etf_daily_chart_by_date_range(db: Session, etf_id: int, start_date, end_date):
    """etf_id와 날짜 범위로 일봉 차트 데이터 조회"""
    return db.query(DomesticETFsDailyChart).filter(
        DomesticETFsDailyChart.etf_id == etf_id,
        DomesticETFsDailyChart.date >= start_date,
        DomesticETFsDailyChart.date <= end_date
    ).order_by(DomesticETFsDailyChart.date.asc()).all()

def bulk_upsert_domestic_etf_daily_charts(db: Session, charts: list):
    """여러 일봉 차트 데이터를 한 번에 upsert (etf_id와 date가 같으면 업데이트, 없으면 생성)"""
    created_count = 0
    updated_count = 0
    
    for chart_data in charts:
        etf_id = chart_data.get('etf_id')
        date = chart_data.get('date')
        
        if not etf_id or not date:
            continue
        
        # 기존 데이터 조회
        existing = get_domestic_etf_daily_chart_by_etf_and_date(db, etf_id, date)
        
        if existing:
            # 업데이트
            update_data = {k: v for k, v in chart_data.items() if k not in ['etf_id', 'date']}
            for field, value in update_data.items():
                setattr(existing, field, value)
            updated_count += 1
        else:
            # 생성
            db_chart = DomesticETFsDailyChart(**chart_data)
            db.add(db_chart)
            created_count += 1
    
    db.commit()
    return {'created': created_count, 'updated': updated_count}

def update_domestic_etf_daily_chart(db: Session, chart_id: int, chart: DomesticETFsDailyChartUpdate):
    db_chart = db.query(DomesticETFsDailyChart).filter(DomesticETFsDailyChart.id == chart_id).first()
    if db_chart:
        update_data = chart.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_chart, field, value)
        db.commit()
        db.refresh(db_chart)
    return db_chart

def delete_domestic_etf_daily_chart(db: Session, chart_id: int):
    db_chart = db.query(DomesticETFsDailyChart).filter(DomesticETFsDailyChart.id == chart_id).first()
    if db_chart:
        db.delete(db_chart)
        db.commit()
    return db_chart

