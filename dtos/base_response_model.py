# Importing Libraries
from pydantic import BaseModel
from typing import Any, Optional

# Initializing
class BaseResponseModel(BaseModel):
    data: Any
    message: Optional[str] = None


class BaseErrorModel(BaseModel):
    data: Any
    error: Optional[str] = None
