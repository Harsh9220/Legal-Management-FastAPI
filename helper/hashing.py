from passlib.context import CryptContext
from helper.api_helper import APIHelper
from dtos.auth_models import UserModel
from utils.db_helper import DBHelper

hash_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Hash:
    def get_hash(text: str):
        return hash_context.hash(text)

    def verify(plain_text: str, hashed_text: str):
        return hash_context.verify(plain_text, hashed_text)

    def authenticate_user(username: str, password: str) -> UserModel:
        user = DBHelper.get_user_by_username(username)
        if not user:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.INVALID_CREDENTIAL"
            )
        if not Hash.verify(password, user.hashed_password):
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )
        if user.is_blocked :
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )
        if user.is_deleted :
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )
        return user
