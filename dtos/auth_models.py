from pydantic import BaseModel
from typing import Optional

class UserModel(BaseModel):
    id:int
    Username:str
    role:str
    

class TokenModel(BaseModel):
    access_token: str
    token_type: Optional[str] = "Bearer"