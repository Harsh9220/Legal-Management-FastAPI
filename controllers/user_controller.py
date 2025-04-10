from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.user_models import UserResponse, CreateUserRequest, UpdateUserRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from helper.hashing import Hash
from helper.validation_helper import ValidationHelper
from models.user import User
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n


class UserController:

    def create_user(
        user_data: CreateUserRequest, current_user: UserModel
    ) -> BaseResponseModel:

        if user_data.role == "admin":
            raise HTTPException(
                status_code=403, detail=i18n.t("translations.PERMISSION_DENIED")
            )

        if user_data.role not in ["lawyer", "staff", "client"]:
            raise HTTPException(
                status_code=400, detail=i18n.t("Invalid role specified")
            )

        if user_data.role == "lawyer":
            RoleHelper.require_role(["admin"], current_user)

        elif user_data.role in ["staff", "client"]:
            RoleHelper.require_role(["admin", "lawyer"], current_user)

        with SessionLocal() as db:
            if db.query(User).filter(User.username == user_data.username).first():
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.USERNAME_EXISTS")
                )

            if db.query(User).filter(User.email == user_data.email).first():
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.EMAIL_EXISTS")
                )
            ValidationHelper.is_valid_password(user_data.password)
            
            new_user = User(
                email=user_data.email,
                username=user_data.username,
                name=user_data.name,
                address=user_data.address,
                hashed_password=Hash.get_hash(user_data.password),
                role=user_data.role,
                mobile=user_data.mobile,
            )

            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            return APIHelper.send_success_response(
                data=UserResponse.model_validate(new_user).model_dump(),
                successMessageKey=f"translations.USER_CREATED",
            )

    def get_users(role: str, current_user: UserModel) -> BaseResponseModel:

        if role == "admin":
            raise HTTPException(
                status_code=403, detail=i18n.t("translations.PERMISSION_DENIED")
            )

        if role not in ["lawyer", "staff", "client"]:
            raise HTTPException(status_code=400, detail="Invalid role specified")

        if role == "lawyer":
            RoleHelper.require_role(["admin"], current_user)
        elif role in ["staff", "client"]:
            RoleHelper.require_role(["admin", "lawyer"], current_user)

        with SessionLocal() as db:
            users = (
                db.query(User)
                .filter(User.role == role)
                .filter(User.is_deleted == False if role != "lawyer" else True)
                .all()
            )

            return APIHelper.send_success_response(
                data=[UserResponse.model_validate(user).model_dump() for user in users],
                successMessageKey="translations.SUCCESS",
            )

    def get_user_by_id(user_id: int, current_user: UserModel) -> BaseResponseModel:

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            if user.role == "admin":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.PERMISSION_DENIED")
                )

            if user.role != "lawyer" and user.is_deleted:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            if user.role == "lawyer":
                if user.id == current_user.id:
                    RoleHelper.require_role(["admin", "lawyer"], current_user)
                else:
                    RoleHelper.require_role(["admin"], current_user)
            elif user.role in ["staff", "client"]:
                if user.id == current_user.id:
                    RoleHelper.require_role(
                        ["admin", "lawyer", "staff", "client"], current_user
                    )
                else:
                    RoleHelper.require_role(["admin", "lawyer"], current_user)

            return APIHelper.send_success_response(
                data=UserResponse.model_validate(user).model_dump(),
                successMessageKey="translations.SUCCESS",
            )

    def update_user(
        user_id: int, update_data: UpdateUserRequest, current_user: UserModel
    ) -> BaseResponseModel:

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            if user.role == "admin":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.PERMISSION_DENIED")
                )

            if user.role != "lawyer" and user.is_deleted:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            if user.role == "lawyer":
                RoleHelper.require_role(["admin"], current_user)

            elif user.role in ["staff", "client"]:
                RoleHelper.require_role(["admin", "lawyer"], current_user)

            if update_data.email and update_data.email != user.email:
                if db.query(User).filter(User.email == update_data.email).first():
                    raise HTTPException(
                        status_code=400, detail=i18n.t("translations.EMAIL_EXISTS")
                    )
                user.email = update_data.email

            if update_data.password:
                ValidationHelper.is_valid_password(update_data.password)
                user.hashed_password = Hash.get_hash(update_data.password)

            for field in ["name", "mobile", "address"]:
                value = getattr(update_data, field, None)
                if value is not None:
                    setattr(user, field, value)

            db.commit()
            db.refresh(user)

            return APIHelper.send_success_response(
                successMessageKey="translations.USER_UPDATED"
            )

    def hard_delete_user(user_id: int, current_user: UserModel) -> BaseResponseModel:

        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()

            if user.role == "admin":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.PERMISSION_DENIED")
                )

            if user.role == "lawyer":
                RoleHelper.require_role(["admin"], current_user)

            elif user.role in ["staff", "client"]:
                RoleHelper.require_role(["admin", "lawyer"], current_user)

            if not user:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            db.delete(user)
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.USER_DELETED"
            )

    def soft_delete_user(user_id: int, current_user: UserModel) -> BaseResponseModel:
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            if user.role == "admin":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.PERMISSION_DENIED")
                )

            if user.role == "lawyer":
                raise HTTPException(
                    status_code=400,
                    detail="Lawyers cannot be soft deleted. Use hard delete instead.",
                )

            RoleHelper.require_role(["admin", "lawyer"], current_user)

            if user.is_deleted:
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.USER_ALREADY_DELETED")
                )

            user.is_deleted = True
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.USER_SOFT_DELETED"
            )

    def restore_user(user_id: int, current_user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["admin", "lawyer"], current_user)
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            if user.role == "admin":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.PERMISSION_DENIED")
                )

            if user.role == "lawyer":
                raise HTTPException(
                    status_code=400,
                    detail="Cannot restore lawyers as they don't support soft delete",
                )

            if not user.is_deleted:
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.USER_NOT_DELETED")
                )

            user.is_deleted = False
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.USER_RESTORED"
            )

    def block_unblock_user(user_id: int, current_user: UserModel) -> BaseResponseModel:
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()

            if not user:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            if user.role == "admin":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.PERMISSION_DENIED")
                )

            if user.role != "lawyer" and user.is_deleted:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.USER_NOT_FOUND")
                )

            if user.role == "lawyer":
                RoleHelper.require_role(["admin"], current_user)

            elif user.role in ["staff", "client"]:
                RoleHelper.require_role(["admin", "lawyer"], current_user)

            user.is_blocked = not user.is_blocked
            db.commit()
            db.refresh(user)

            new_status = "blocked" if user.is_blocked else "unblocked"

            return APIHelper.send_success_response(
                data={"user_id": user.id, "status": new_status},
                successMessageKey="translations.USER_STATUS_UPDATED",
            )
