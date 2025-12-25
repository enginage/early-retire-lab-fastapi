from pydantic import BaseModel
from typing import List, Optional

class CommonCodeMasterBase(BaseModel):
    code: str  # 코드
    code_name: str  # 코드명
    remark: Optional[str] = None  # 비고

class CommonCodeMasterCreate(CommonCodeMasterBase):
    pass

class CommonCodeMasterUpdate(CommonCodeMasterBase):
    pass

class CommonCodeMaster(CommonCodeMasterBase):
    id: int
    
    class Config:
        from_attributes = True

# CommonCodeDetail 스키마가 정의된 후 CommonCodeMasterWithDetails를 정의
from .common_code_detail import CommonCodeDetail

class CommonCodeMasterWithDetails(CommonCodeMaster):
    details: List[CommonCodeDetail] = []

# 순환 참조 해결
CommonCodeMasterWithDetails.model_rebuild()


