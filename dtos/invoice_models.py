from pydantic import BaseModel,EmailStr,Field
from typing import Optional
from datetime import datetime, date

class CreateInvoiceRequest(BaseModel):
    invoice_number:int = Field(gt=0)
    client_id:int
    amount:int = Field(gt=0)
    due_on_date : Optional[date]
    
class UpdateInvoiceRequest(BaseModel):
    client_id:Optional[int] = Field(None)
    amount:Optional[int] = Field(None,gt=0)
    due_on_date: Optional[date] = Field(None)
    
class CreatorResponse(BaseModel):
    id:int
    name:str
    
    class Config:
        from_attributes = True

class ClientResponse(BaseModel):
    id:int
    name:str
    
    class Config:
        from_attributes = True

class InvoiceResponse(BaseModel):
    id:int
    invoice_number:int
    amount:int
    due_on_date:Optional[date]=None
    updated_at:datetime
    created_at:datetime
    client:ClientResponse
    creator:CreatorResponse
    
    class Config:
        from_attributes = True