from pydantic import BaseModel, EmailStr
from typing import Optional


class UserModel(BaseModel):
    id: int
    email: EmailStr
    role: str


class TokenModel(BaseModel):
    access_token: str
    token_type: Optional[str] = "Bearer"
