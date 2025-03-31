import i18n
import re
from helper.api_helper import APIHelper
from utils.db_helper import DBHelper


class ValidationHelper:
    def is_valid_email(v):
        EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"  
        if not re.fullmatch(EMAIL_REGEX, v):
            raise ValueError(i18n.t(key="translations.INVALID_EMAIL"))
        user = DBHelper.get_user_by_email(v)
        if user:
            raise APIHelper.send_error_response(
                errorMessageKey="translations.USER_EXISTS"
            )
        return v

    def is_mobile(v):
        MOBILE_NUMBER_REGEX = r"^\+?[1-9]\d{1,14}$" 
        if not re.fullmatch(MOBILE_NUMBER_REGEX, v):
            raise ValueError(i18n.t(key="translations.INVALID_MOBILE"))
        return v

    def is_valid_password(v):
        PASSWORD_REGEX = (
            r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$" 
        )
        if not re.fullmatch(PASSWORD_REGEX, v):
            raise ValueError(i18n.t(key="translations.INVALID_PASSWORD"))
        return v