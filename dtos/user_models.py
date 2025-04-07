from typing import Optional
from pydantic import BaseModel, Field, EmailStr

class CreateUserRequest(BaseModel):
    email: EmailStr
    username: str = Field(min_length=3, max_length=50)
    name: str = Field(min_length=3, max_length=255)
    address: Optional[str] = Field(None, min_length=2, max_length=255)
    password: str = Field(min_length=1)
    role: str = Field(pattern="^(lawyer|staff|client)$")
    mobile: Optional[str] = Field(None, min_length=7, max_length=20)
    
class UpdateUserRequest(BaseModel):
    email: Optional[EmailStr] = Field(None)
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    address: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=1)
    mobile: Optional[str] = Field(None, min_length=7, max_length=20)

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    name: str
    mobile: Optional[str] = None
    address: Optional[str] = None
    role: str
    is_blocked: bool
    is_deleted: bool

    class Config:
        from_attributes = True