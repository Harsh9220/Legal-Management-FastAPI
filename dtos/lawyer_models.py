from pydantic import BaseModel,EmailStr,Field
from typing import Optional
from datetime import datetime

class CreateLawyerRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=3, max_length=255)
    address: Optional[str] = Field(None, min_length=2, max_length=255)
    password: str = Field(min_length=1)
    mobile: Optional[str] = Field(None, min_length=7, max_length=20)


class UpdateLawyerRequest(BaseModel):
    email: Optional[EmailStr] = Field(None)
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    address: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=1)
    mobile: Optional[str] = Field(None, min_length=7, max_length=20)

class LawyerResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str
    address: Optional[str] = None
    mobile: Optional[str] = None
    role: str
    is_blocked: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True