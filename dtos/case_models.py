from pydantic import BaseModel,EmailStr,Field
from typing import Optional, List
from datetime import datetime

class CreateCaseRequest(BaseModel):
    case_number:str = Field(min_length=3,max_length=50)
    case_name:str = Field(min_length=3,max_length=255)
    case_category:str = Field(pattern="^(theft|fraud|divorce)$")
    case_stage:str = Field(pattern="^(appeal|first degree)$")
    city_name: Optional[str] = Field(min_length=3, max_length=255)
    client_id: int
    remarks: Optional[str]
    staff_ids: Optional[List[int]] = None

    
class UpdateCaseRequest(BaseModel):
    case_name: Optional[str] = Field(None, min_length=3, max_length=255)
    case_category: Optional[str] = Field(None, pattern="^(theft|fraud|divorce)$")
    case_stage: Optional[str] = Field(None, pattern="^(appeal|first degree)$")
    city_name: Optional[str] = Field(None, min_length=3, max_length=255)
    client_id:Optional[int] = Field(None)
    remarks: Optional[str] = Field(None)
    case_status: Optional[str] = Field(None, pattern="^(open|closed)$")
    staff_ids: Optional[List[int]] = None

    
class ClientResponse(BaseModel):
    id: int
    name: str
    

    class Config:
        from_attributes = True

class LawyerResponse(BaseModel):
    id: int
    name: str
    

    class Config:
        from_attributes = True
        
class StaffResponse(BaseModel):
    id: int
    name: str
    

    class Config:
        from_attributes = True        
        

class CaseResponse(BaseModel):
    id: int
    case_number: str
    case_name: str
    case_category: str
    case_stage: str
    case_status: str
    issue_date: Optional[datetime] 
    city_name: Optional[str]
    remarks: Optional[str]
    is_deleted:bool
    lawyer: LawyerResponse
    client: ClientResponse
    staff_members: Optional[List[StaffResponse]] = []

    class Config:
        from_attributes = True