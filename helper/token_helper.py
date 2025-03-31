# Importing libraries
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from dtos.auth_models import UserModel
from helper.api_helper import APIHelper
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import os
from utils.db_helper import DBHelper

# JWT Configuration

"""Please generate a new JWT_SECRET `using openssl rand -hex 32` command and add it in the .env file"""

# Initializing the Hashing alogorith
JWT_SECRET = os.getenv("JWT_SECRET")
ALGORITHM = "HS256"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


class TokenHelper:
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now() + timedelta(days=30)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, JWT_SECRET, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(token: str) -> UserModel:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
            username = payload.get("sub")
            user_id = payload.get("id")
            user_role = payload.get("role")  
            exp = payload.get("exp")
            
            if exp and datetime.now(timezone.utc).timestamp() > exp:
                return APIHelper.send_unauthorized_error(errorMessageKey='translations.TOKEN_EXPIRED')
          
            if not username or not user_id or not user_role:
                return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')
        except JWTError:
            return APIHelper.send_unauthorized_error(errorMessageKey='translations.UNAUTHORIZED')
        user = DBHelper.get_user_by_id(user_id)
        if user is None:
            return APIHelper.send_unauthorized_error(
                errorMessageKey='translations.UNAUTHORIZED')
        return UserModel(id=user.id,Username=user.username,role=user.role)

    def get_current_user(token: str = Depends(oauth2_scheme)) -> UserModel:
        return TokenHelper.verify_token(token)
