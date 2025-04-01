from pydantic import BaseModel,EmailStr,Field
from typing import Optional
from datetime import datetime

class CreateClientRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    name: str = Field(min_length=3, max_length=255)
    mobile_number: str = Field(min_length=7, max_length=20)
    vat_percentage: Optional[str] 
    vat_number : Optional[str]
    CR_number : Optional[str]
    address: Optional[str] = Field(None,min_length=3, max_length=255)
    
class UpdateClientRequest(BaseModel):
    email: Optional[EmailStr] = Field(None)
    name: Optional[str] = Field(None,min_length=3, max_length=255)
    mobile_number: Optional[str] = Field(None,min_length=7, max_length=20)
    vat_percentage: Optional[str] = Field(None)
    vat_number : Optional[str] = Field(None)
    CR_number : Optional[str] = Field(None)
    address: Optional[str] = Field(None,min_length=3, max_length=255)
    
class ClientResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    name: str
    mobile_number: str
    address: Optional[str] = None
    vat_percentage: Optional[str] = None
    vat_number: Optional[str] = None
    CR_number: Optional[str] = None
    is_blocked: bool
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True