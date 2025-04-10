from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime



class UpdateDocumentRequest(BaseModel):
    document_name:Optional[str]


class DocumentResponse(BaseModel):
    id: int
    document_name: str
    document_path: str
    uploader_id: int
    case_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
