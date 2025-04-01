from pydantic import BaseModel,EmailStr,Field
from typing import Optional
from datetime import datetime

class CreateDocumentRequest(BaseModel):
    document_name:str = Field(min_length=3,max_length=255)
    case_id:int

class UpdateDocumentRequest(BaseModel):
    document_name: Optional[str] = Field(None,min_length=3,max_length=255)
    
class DocumentResponse(BaseModel):
    id: int
    document_name: str
    uploader_id: int
    case_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True