from pydantic import BaseModel,EmailStr,Field
from typing import Optional
from datetime import datetime, date

class CreateTaskRequest(BaseModel):
    task_name:str = Field(min_length=3,max_length=255)
    due_date:Optional[date]
    priority:str = Field(pattern="^(high|medium|low)$")
    assign_to_staff : Optional[int]=None
    case_id:int
    
    
class UpdateTaskRequest(BaseModel):
    task_name:Optional[str] = Field(None,min_length=3,max_length=255)
    due_date:Optional[date] = Field(None)
    priority: Optional[str] = Field(None,pattern="^(high|medium|low)$")
    assign_to_staff: Optional[int] = Field(None)
    status: Optional[str] = Field(None,pattern="^(complete|need review|incomplete)$")
    
    
class TaskResponse(BaseModel):
    id: int
    task_name: str
    due_date: date
    priority: str
    status: str
    case_id: int
    assign_to_staff: Optional[int] = None
    created_by: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
