from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.lawyer_models import LawyerResponse, CreateLawyerRequest, UpdateLawyerRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from helper.hashing import Hash
from models.user import User
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n


class LawyerController:

    def get_all_lawyers(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            lawyers = (
                db.query(User)
                .filter(User.role == "lawyer", User.is_deleted == False)
                .all()
            )

            if not lawyers:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.LAWYER_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=[
                    LawyerResponse.model_validate(lawyer).model_dump()
                    for lawyer in lawyers
                ],
                successMessageKey="translations.SUCCESS",
            )

    def get_lawyer_by_id(lawyer_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["admin", user], user)
        with SessionLocal() as db:
            lawyer = (
                db.query(User)
                .filter(
                    User.id == lawyer_id,
                    User.role == "lawyer",
                    User.is_deleted == False,
                )
                .first()
            )

            if not lawyer:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.LAWYER_NOT_FOUND")
                )
            return APIHelper.send_success_response(
                data=LawyerResponse.model_validate(lawyer).model_dump(),
                successMessageKey="translations.SUCCESS",
            )

    def create_lawyer(
        lawyer_data: CreateLawyerRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            if db.query(User).filter(User.username == lawyer_data.username).first():
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.USERNAME_EXISTS")
                )

            if db.query(User).filter(User.email == lawyer_data.email).first():
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.EMAIL_EXISTS")
                )

            hash_password = Hash.get_hash(lawyer_data.password)

            new_lawyer = User(
                email=lawyer_data.email,
                username=lawyer_data.username,
                name=lawyer_data.name,
                address=lawyer_data.address,
                hashed_password=hash_password,
                role="lawyer",
                mobile=lawyer_data.mobile,
            )
            db.add(new_lawyer)
            db.commit()
            db.refresh(new_lawyer)

            return APIHelper.send_success_response(
                data=LawyerResponse.model_validate(new_lawyer).model_dump(),
                successMessageKey="translations.LAWYER_CREATED",
            )

    def update_lawyer(
        lawyer_id: int, update_data: UpdateLawyerRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            lawyer = (
                db.query(User)
                .filter(User.id == lawyer_id, User.role == "lawyer")
                .first()
            )
            if not lawyer:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.LAWYER_NOT_FOUND")
                )

            if update_data.email is not None:
                if db.query(User).filter(User.email == update_data.email).first():
                    raise HTTPException(
                        status_code=400, detail=i18n.t("translations.EMAIL_EXISTS")
                    )
                lawyer.email = update_data.email
            if update_data.name is not None:
                lawyer.name = update_data.name
            if update_data.address is not None:
                lawyer.address = update_data.address
            if update_data.mobile is not None:
                lawyer.mobile = update_data.mobile
            if update_data.password is not None:
                hash_password = Hash.get_hash(update_data.password)
                lawyer.hashed_password = hash_password

            db.commit()
            db.refresh(lawyer)

            return APIHelper.send_success_response(
                successMessageKey="translations.LAWYER_UPDATED"
            )

    def block_unblock_lawyer(lawyer_id: int, user: UserModel)->BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            lawyer = (
                db.query(User)
                .filter(User.id == lawyer_id, User.role == "lawyer")
                .first()
            )
            if not lawyer:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.LAWYER_NOT_FOUND")
                )

            lawyer.is_blocked = not lawyer.is_blocked

            db.commit()
            db.refresh(lawyer)

            new_status = "blocked" if lawyer.is_blocked else "unblocked"
            return APIHelper.send_success_response(
                data={"lawyer_id": lawyer.id, "status": new_status},
                successMessageKey="translations.LAWYER_STATUS_UPDATED",
            )

    def delete_lawyer(lawyer_id: int, user: UserModel)->BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            lawyer = (
                db.query(User)
                .filter(User.id == lawyer_id, User.role == "lawyer")
                .first()
            )
            if not lawyer:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.LAWYER_NOT_FOUND")
                )
            db.delete(lawyer)
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.LAWYER_DELETED"
            )
