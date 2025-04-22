from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.case_models import CaseResponse, CreateCaseRequest, UpdateCaseRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.case import cases_table, case_staff_table
from models.user import users_table
from utils.db_helper import DBHelper
from config.constants import Constants


class CaseController:

    def load_case_relations(case_data):
        cd = dict(case_data._mapping)

        lawyer = (
            DBHelper.execute_query(
                users_table.select().where(
                    users_table.c.id == cd["lawyer_id"],
                    users_table.c.is_deleted == False,
                    users_table.c.role == Constants.LAWYER,
                )
            )
            .mappings()
            .fetchone()
        )

        client = (
            DBHelper.execute_query(
                users_table.select().where(
                    users_table.c.id == cd["client_id"],
                    users_table.c.is_deleted == False,
                    users_table.c.role == Constants.CLIENT,
                )
            )
            .mappings()
            .fetchone()
        )

        creator = (
            DBHelper.execute_query(
                users_table.select().where(
                    users_table.c.id == cd["created_by"],
                    users_table.c.is_deleted == False,
                )
            )
            .mappings()
            .fetchone()
        )

        staff = DBHelper.execute_query(
            users_table.select()
            .select_from(
                case_staff_table.join(
                    users_table, case_staff_table.c.staff_id == users_table.c.id
                )
            )
            .where(
                case_staff_table.c.case_id == cd["id"],
                users_table.c.is_deleted == False,
                users_table.c.role == Constants.STAFF,
            )
        )

        staff_list = staff.mappings().fetchall()

        return {
            **cd,
            "lawyer": {"id": lawyer["id"], "name": lawyer["name"]} if lawyer else None,
            "client": {"id": client["id"], "name": client["name"]} if client else None,
            "creator": (
                {"id": creator["id"], "name": creator["name"]} if creator else None
            ),
            "staff_members": [{"id": s["id"], "name": s["name"]} for s in staff_list],
        }

    def get_all_cases(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF, Constants.CLIENT], user
        )

        if user.role == Constants.STAFF:
            query = (
                cases_table.join(
                    case_staff_table, cases_table.c.id == case_staff_table.c.case_id
                )
                .join(users_table, case_staff_table.c.staff_id == users_table.c.id)
                .select()
                .where(cases_table.c.is_deleted == False, users_table.c.id == user.id)
            )
        elif user.role == Constants.LAWYER:
            query = cases_table.select().where(
                cases_table.c.is_deleted == False, cases_table.c.lawyer_id == user.id
            )
        elif user.role == Constants.CLIENT:
            query = cases_table.select().where(
                cases_table.c.is_deleted == False, cases_table.c.client_id == user.id
            )
        else:
            query = cases_table.select().where(cases_table.c.is_deleted == False)

        cases = DBHelper.execute_query(query).fetchall()

        if not cases:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        return APIHelper.send_success_response(
            data=[
                CaseResponse.model_validate(
                    CaseController.load_case_relations(case)
                ).model_dump()
                for case in cases
            ],
            successMessageKey="translations.SUCCESS",
        )

    def get_case_by_id(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF, Constants.CLIENT], user
        )
        if user.role == Constants.STAFF:
            query = (
                cases_table.join(
                    case_staff_table, cases_table.c.id == case_staff_table.c.case_id
                )
                .join(users_table, case_staff_table.c.staff_id == users_table.c.id)
                .select()
                .where(
                    cases_table.c.id == case_id,
                    cases_table.c.is_deleted == False,
                    users_table.c.id == user.id,
                )
                .limit(1)
            )
        elif user.role == Constants.LAWYER:
            query = (
                cases_table.select()
                .where(
                    cases_table.c.id == case_id,
                    cases_table.c.is_deleted == False,
                    cases_table.c.lawyer_id == user.id,
                )
                .limit(1)
            )
        elif user.role == Constants.CLIENT:
            query = (
                cases_table.select()
                .where(
                    cases_table.c.id == case_id,
                    cases_table.c.is_deleted == False,
                    cases_table.c.client_id == user.id,
                )
                .limit(1)
            )
        else:
            query = (
                cases_table.select()
                .where(cases_table.c.id == case_id, cases_table.c.is_deleted == False)
                .limit(1)
            )

        case = DBHelper.execute_query(query).fetchone()

        if not case:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        return APIHelper.send_success_response(
            data=CaseResponse.model_validate(
                CaseController.load_case_relations(case)
            ).model_dump(),
            successMessageKey="translations.SUCCESS",
        )

    def create_case(case_data: CreateCaseRequest, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)
        print("Checking for existing case number...")

        if DBHelper.execute_query(
            cases_table.select().where(
                cases_table.c.case_number == case_data.case_number
            )
        ).fetchone():
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NUM_EXISTS"
            )
        print("Checking for valid client...")

        if not DBHelper.execute_query(
            users_table.select().where(
                users_table.c.id == case_data.client_id,
                users_table.c.is_deleted == False,
                users_table.c.role == Constants.CLIENT,
            )
        ).fetchone():
            return APIHelper.send_error_response(
                errorMessageKey="translations.CLIENT_NOT_FOUND"
            )

        print("Checking for valid lawyer...")

        lawyer_id = user.id if user.role == Constants.LAWYER else case_data.lawyer_id
        if not DBHelper.execute_query(
            users_table.select().where(
                users_table.c.id == lawyer_id,
                users_table.c.is_deleted == False,
                users_table.c.role == Constants.LAWYER,
            )
        ).fetchone():
            return APIHelper.send_error_response(
                errorMessageKey="translations.LAWYER_NOT_FOUND"
            )

        insert_result = DBHelper.execute_query(
            cases_table.insert().values(
                case_number=case_data.case_number,
                case_name=case_data.case_name,
                case_category=case_data.case_category,
                case_stage=case_data.case_stage,
                client_id=case_data.client_id,
                lawyer_id=lawyer_id,
                created_by=user.id,
                city_name=case_data.city_name,
                remarks=case_data.remarks,
            )
        )
        case_id = None
        if (
            hasattr(insert_result, "inserted_primary_key")
            and insert_result.inserted_primary_key
        ):
            case_id = insert_result.inserted_primary_key[0]
        else:
            case_id = insert_result.lastrowid

        print(f"Checking staff ID: ")

        if case_data.staff_ids:
            for sid in case_data.staff_ids:
                if not DBHelper.execute_query(
                    users_table.select().where(
                        users_table.c.id == sid,
                        users_table.c.is_deleted == False,
                        users_table.c.role == Constants.STAFF,
                    )
                ).fetchone():
                    return APIHelper.send_error_response(
                        errorMessageKey="translations.STAFF_NOT_FOUND"
                    )
                DBHelper.execute_query(
                    case_staff_table.insert().values(case_id=case_id, staff_id=sid)
                )

        # fetch and return
        new_row = DBHelper.execute_query(
            cases_table.select().where(cases_table.c.id == case_id)
        ).fetchone()

        return APIHelper.send_success_response(
            data=CaseResponse.model_validate(
                CaseController.load_case_relations(new_row)
            ).model_dump(),
            successMessageKey="translations.CASE_CREATED",
        )

    def update_case(
        case_id: int, update_data: UpdateCaseRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)

        case = DBHelper.execute_query(
            cases_table.select().where(
                cases_table.c.id == case_id, cases_table.c.is_deleted == False
            )
        ).fetchone()
        if not case:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        if user.role != Constants.ADMIN and case.created_by != user.id:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )

        update_values = {}
        for attr in [
            "case_name",
            "case_category",
            "case_stage",
            "city_name",
            "case_status",
            "remarks",
        ]:
            val = getattr(update_data, attr)
            if val is not None:
                update_values[attr] = val

        if update_data.client_id is not None:
            client = DBHelper.execute_query(
                users_table.select().where(
                    users_table.c.id == update_data.client_id,
                    users_table.c.is_deleted == False,
                    users_table.c.role == Constants.CLIENT,
                )
            ).fetchone()
            if not client:
                return APIHelper.send_error_response(
                    errorMessageKey="translations.CLIENT_NOT_FOUND"
                )
            update_values["client_id"] = update_data.client_id

        if update_data.lawyer_id is not None and user.role == Constants.ADMIN:
            lawyer = DBHelper.execute_query(
                users_table.select().where(
                    users_table.c.id == update_data.lawyer_id,
                    users_table.c.is_deleted == False,
                    users_table.c.role == Constants.LAWYER,
                )
            ).fetchone()
            if not lawyer:
                return APIHelper.send_error_response(
                    errorMessageKey="translations.LAWYER_NOT_FOUND"
                )
            update_values["lawyer_id"] = update_data.lawyer_id

        if update_values:
            DBHelper.execute_query(
                cases_table.update()
                .where(cases_table.c.id == case_id)
                .values(**update_values)
            )

        if hasattr(update_data, "staff_ids") and update_data.staff_ids is not None:

            DBHelper.execute_query(
                case_staff_table.delete().where(case_staff_table.c.case_id == case_id)
            )
            for staff_id in update_data.staff_ids:
                staff = DBHelper.execute_query(
                    users_table.select().where(
                        users_table.c.id == staff_id,
                        users_table.c.role == Constants.STAFF,
                        users_table.c.is_deleted == False,
                    )
                ).fetchone()
                if not staff:
                    return APIHelper.send_error_response(
                        errorMessageKey="translations.STAFF_NOT_FOUND"
                    )

                DBHelper.execute_query(
                    case_staff_table.insert().values(case_id=case_id, staff_id=staff_id)
                )

        return APIHelper.send_success_response(
            data={"case_id": case_id}, successMessageKey="translations.CASE_UPDATED"
        )

    def delete_case(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)

        case = DBHelper.execute_query(
            cases_table.select().where(cases_table.c.id == case_id)
        ).fetchone()
        if not case:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        if user.role != Constants.ADMIN and case.created_by != user.id:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )

        DBHelper.execute_query(cases_table.delete().where(cases_table.c.id == case_id))

        return APIHelper.send_success_response(
            successMessageKey="translations.CASE_DELETED"
        )

    def soft_delete_case(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)

        case = DBHelper.execute_query(
            cases_table.select().where(cases_table.c.id == case_id)
        ).fetchone()

        if not case:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        if user.role != Constants.ADMIN and case.created_by != user.id:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )

        if case.is_deleted:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_ALREADY_DELETED"
            )

        DBHelper.execute_query(
            cases_table.update()
            .where(cases_table.c.id == case_id)
            .values(is_deleted=True)
        )

        return APIHelper.send_success_response(
            data={"case_id": case_id},
            successMessageKey="translations.CASE_SOFT_DELETED",
        )

    def restore_case(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)

        case = DBHelper.execute_query(
            cases_table.select().where(cases_table.c.id == case_id)
        ).fetchone()
        if not case:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        if user.role != Constants.ADMIN and case.created_by != user.id:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )

        if not case.is_deleted:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_DELETED"
            )

        DBHelper.execute_query(
            cases_table.update()
            .where(cases_table.c.id == case_id)
            .values(is_deleted=False)
        )

        return APIHelper.send_success_response(
            data={"case_id": case_id}, successMessageKey="translations.CASE_RESTORED"
        )
