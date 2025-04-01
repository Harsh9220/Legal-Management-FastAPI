from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime, date

class CreateSessionRequest(BaseModel):
    case_id:int
    result:str=Field(min_length=3,max_length=100)
    session_date:Optional[date]
    court_type:str=Field(min_length=3,max_length=100)
    
class CaseResponse(BaseModel):
    id:int
    case_name:str
    
    class Config:
        from_attributes = True
    
class SessionResponse(BaseModel):
    id: int
    case_id: int
    result: str
    session_date: date
    court_type: str
    created_at: datetime
    case:CaseResponse

    class Config:
        from_attributes = True