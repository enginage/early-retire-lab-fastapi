from sqlalchemy.orm import Session
from app.models.expense import Expense, ExpenseType
from app.schemas.expense import ExpenseCreate, ExpenseUpdate

def get_expenses(db: Session, expense_type: ExpenseType = None, skip: int = 0, limit: int = 100):
    query = db.query(Expense)
    if expense_type:
        query = query.filter(Expense.type == expense_type)
    return query.offset(skip).limit(limit).all()

def get_expense(db: Session, expense_id: int):
    return db.query(Expense).filter(Expense.id == expense_id).first()

def create_expense(db: Session, expense: ExpenseCreate):
    db_expense = Expense(**expense.model_dump())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

def update_expense(db: Session, expense_id: int, expense: ExpenseUpdate):
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        raise ValueError(f"지출 항목을 찾을 수 없습니다: {expense_id}")
    
    db_expense.type = expense.type
    db_expense.item = expense.item
    db_expense.amount = expense.amount
    db.commit()
    db.refresh(db_expense)
    return db_expense

def delete_expense(db: Session, expense_id: int):
    db_expense = get_expense(db, expense_id)
    if not db_expense:
        raise ValueError(f"지출 항목을 찾을 수 없습니다: {expense_id}")
    
    db.delete(db_expense)
    db.commit()
    return db_expense

