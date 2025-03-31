from typing import List
from dtos.auth_models import UserModel
from fastapi import HTTPException
import i18n
import locale

class RoleHelper:
    def require_role(required_roles: List[str],user:UserModel):
        if user.role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=i18n.t(key="translations.PERMISSION_DENIED",locale=locale)
            )
        return user
    