from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.case_models import CaseResponse, CreateCaseRequest, UpdateCaseRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.case import Case
from models.client import Client
from models.user import User
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n


class CaseController:

    def get_all_cases(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            if user.role == "staff":
                cases = (
                    db.query(Case)
                    .join(Case.staff_members)
                    .filter(Case.is_deleted == False, User.id == user.id)
                    .all()
                )
            else:
                cases = db.query(Case).filter(Case.is_deleted == False).all()

            if not cases:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=[CaseResponse.model_validate(case).model_dump() for case in cases],
                successMessageKey="translations.SUCCESS",
            )

    def get_case_by_id(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            if user.role == "staff":
                case = (
                    db.query(Case)
                    .join(Case.staff_members)
                    .filter(
                        Case.id == case_id, Case.is_deleted == False, User.id == user.id
                    )
                    .first()
                )
            else:
                case = (
                    db.query(Case)
                    .filter(Case.id == case_id, Case.is_deleted == False)
                    .first()
                )

            if not case:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND")
                )
            return APIHelper.send_success_response(
                data=CaseResponse.model_validate(case).model_dump(),
                successMessageKey="translations.SUCCESS",
            )

    def create_case(case_data: CreateCaseRequest, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            existing_case = (
                db.query(Case).filter(Case.case_number == case_data.case_number).first()
            )
            if existing_case:
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.CASE_NUM_EXISTS")
                )

            client = (
                db.query(Client)
                .filter(Client.id == case_data.client_id, Client.is_deleted == False)
                .first()
            )
            if not client:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            new_case = Case(
                case_number=case_data.case_number,
                case_name=case_data.case_name,
                case_category=case_data.case_category,
                case_stage=case_data.case_stage,
                client_id=case_data.client_id,
                lawyer_id=user.id,
                city_name=case_data.city_name,
                remarks=case_data.remarks,
            )

            if case_data.staff_ids:
                for staff_id in case_data.staff_ids:
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
                            status_code=404,
                            detail=i18n.t("translations.STAFF_NOT_FOUND"),
                        )
                    if staff not in new_case.staff_members:
                        new_case.staff_members.append(staff)

            db.add(new_case)
            db.commit()
            db.refresh(new_case)

            return APIHelper.send_success_response(
                data=CaseResponse.model_validate(new_case).model_dump(),
                successMessageKey="translations.CASE_CREATED",
            )

    def update_case(
        case_id: int, update_data: UpdateCaseRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            case = (
                db.query(Case)
                .filter(Case.id == case_id, Case.is_deleted == False)
                .first()
            )

            if not case:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND")
                )

            if update_data.case_name is not None:
                case.case_name = update_data.case_name
            if update_data.case_category is not None:
                case.case_category = update_data.case_category
            if update_data.case_stage is not None:
                case.case_stage = update_data.case_stage
            if update_data.city_name is not None:
                case.city_name = update_data.city_name
            if update_data.case_status is not None:
                case.case_status = update_data.case_status
            if update_data.remarks is not None:
                case.remarks = update_data.remarks
            if update_data.client_id is not None:
                new_client = (
                    db.query(Client)
                    .filter(
                        Client.id == update_data.client_id, Client.is_deleted == False
                    )
                    .first()
                )

                if not new_client:
                    raise HTTPException(
                        status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                    )

                case.client_id = update_data.client_id

            if hasattr(update_data, "staff_ids") and update_data.staff_ids is not None:
                case.staff_members.clear()
                for staff_id in update_data.staff_ids:
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
                            status_code=404,
                            detail=i18n.t("translations.STAFF_NOT_FOUND"),
                        )

                    case.staff_members.append(staff)

            db.commit()
            db.refresh(case)

            return APIHelper.send_success_response(
                data={"case_id": case.id}, successMessageKey="translations.CASE_UPDATED"
            )

    def delete_case(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            case = db.query(Case).filter(Case.id == case_id).first()

            if not case:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND")
                )

            db.delete(case)
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.CASE_DELETED"
            )

    def soft_delete_case(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            case = db.query(Case).filter(Case.id == case_id).first()

            if not case:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND")
                )

            if case.is_deleted:
                raise HTTPException(
                    status_code=409,
                    detail=i18n.t("translations.CASE_ALREADY_DELETED"),
                )

            case.is_deleted = True

            db.commit()
            db.refresh(case)

            return APIHelper.send_success_response(
                data={"case_id": case.id},
                successMessageKey="translations.CASE_SOFT_DELETED",
            )

    def restore_case(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            case = db.query(Case).filter(Case.id == case_id).first()

            if not case:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND")
                )

            if not case.is_deleted:
                raise HTTPException(
                    status_code=409, detail=i18n.t("translations.CASE_NOT_DELETED")
                )

            case.is_deleted = False

            db.commit()
            db.refresh(case)

            return APIHelper.send_success_response(
                data={"case_id": case.id},
                successMessageKey="translations.CASE_RESTORED",
            )
