from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.staff_models import StaffResponse, CreateStaffRequest, UpdateStaffRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from helper.hashing import Hash
from models.user import User
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n

class StaffController:
    
    def get_all_staffs(user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            staffs = (
                db.query(User)
                .filter(User.role == "staff", User.is_deleted == False)
                .all()
            )

            if not staffs:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.STAFF_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=[
                    StaffResponse.model_validate(staff).model_dump()
                    for staff in staffs
                ],
                successMessageKey="translations.SUCCESS",
            )
    
    def get_staff_by_id(staff_id:int,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            staff = (
                db.query(User)
                .filter(
                    User.id == staff_id,
                    User.role == "staff",
                    User.is_deleted == False,
                )
                .first()
            )

            if not staff:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.STAFF_NOT_FOUND")
                )
            return APIHelper.send_success_response(
                data=StaffResponse.model_validate(staff).model_dump(),
                successMessageKey="translations.SUCCESS",
            )
    
    def create_staff(staff_data:CreateStaffRequest,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            
            if db.query(User).filter(User.username == staff_data.username).first():
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.USERNAME_EXISTS")
                )
            if db.query(User).filter(User.email == staff_data.email).first():
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.EMAIL_EXISTS")
                )
            
            hash_password = Hash.get_hash(staff_data.password)

            new_staff = User(
                email=staff_data.email,
                username=staff_data.username,
                name=staff_data.name,
                address=staff_data.address,
                hashed_password=hash_password,
                role="staff",
                mobile=staff_data.mobile,
            )
            db.add(new_staff)
            db.commit()
            db.refresh(new_staff)
            
            return APIHelper.send_success_response(
                data=StaffResponse.model_validate(new_staff).model_dump(),
                successMessageKey="translations.STAFF_CREATED",
            )
            
    def update_staff(staff_id:int,update_data:UpdateStaffRequest,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            staff = db.query(User).filter(User.id == staff_id, User.role == "staff",User.is_deleted==False).first()

            if not staff:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.STAFF_NOT_FOUND")
                )

            if update_data.email is not None:
                if db.query(User).filter(User.email == update_data.email).first():
                    raise HTTPException(
                    status_code=400, detail=i18n.t("translations.EMAIL_EXISTS")
                    )
                staff.email = update_data.email
            if update_data.name is not None:
                staff.name = update_data.name
            if update_data.address is not None:
                staff.address = update_data.address
            if update_data.mobile is not None:
                staff.mobile = update_data.mobile
            if update_data.password is not None:
                hash_password=Hash.get_hash(update_data.password)
                staff.hashed_password = hash_password

            db.commit()
            db.refresh(staff)
            
            return APIHelper.send_success_response(
                successMessageKey="translations.STAFF_UPDATED"
            )
    def delete_staff(staff_id,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            staff = db.query(User).filter(User.id == staff_id, User.role == "staff").first()

            if not staff:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.STAFF_NOT_FOUND")
                )

            db.delete(staff)
            db.commit()
            return APIHelper.send_success_response(
                successMessageKey="translations.STAFF_DELETED"
            )
    
    def block_unblock_staff(staff_id:int,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            staff = (
                db.query(User)
                .filter(User.id == staff_id, User.role == "staff", User.is_deleted == False)
                .first()
            )

            if not staff:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.STAFF_NOT_FOUND")
                )
            staff.is_blocked = not staff.is_blocked

            db.commit()
            db.refresh(staff)

            new_status = "blocked" if staff.is_blocked else "unblocked"
            return APIHelper.send_success_response(
                data={"staff_id": staff.id, "status": new_status},
                successMessageKey="translations.STAFF_STATUS_UPDATED",
            )
    
    def soft_delete_staff(staff_id:int,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            staff = db.query(User).filter(User.id == staff_id, User.role == "staff").first()

            if not staff:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.STAFF_NOT_FOUND")
                )

            if staff.is_deleted:
                raise HTTPException(
                    status_code=409,
                    detail=i18n.t("translations.STAFF_ALREADY_DELETED"),
                )

            staff.is_deleted = True

            db.commit()
            db.refresh(staff)
            return APIHelper.send_success_response(
                data={"staff_id": staff.id},
                successMessageKey="translations.STAFF_SOFT_DELETED",
            )
            
    def restore_staff(staff_id:int,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            staff = db.query(User).filter(User.id == staff_id, User.role == "staff").first()

            if not staff:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.STAFF_NOT_FOUND")
                )
            if not staff.is_deleted:
                raise HTTPException(
                    status_code=409,
                    detail=i18n.t("translations.STAFF_NOT_DELETED"),
                )

            staff.is_deleted = False

            db.commit()
            db.refresh(staff)
            
            return APIHelper.send_success_response(
                data={"staff_id": staff.id},
                successMessageKey="translations.STAFF_RESTORED",
            )