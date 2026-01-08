from pydantic import BaseModel

class CommonCodeDetailBase(BaseModel):
    master_id: int  # 마스터 ID
    detail_code: str  # 상세코드
    detail_code_name: str  # 상세코드명
    order_no: int  # 정렬순서

class CommonCodeDetailCreate(CommonCodeDetailBase):
    pass

class CommonCodeDetailUpdate(CommonCodeDetailBase):
    pass

class CommonCodeDetail(CommonCodeDetailBase):
    id: int
    
    class Config:
        from_attributes = True

