from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.session_models import SessionResponse, CreateSessionRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.session import sessions_table
from models.case import cases_table
from utils.db_helper import DBHelper
from config.constants import Constants
from datetime import date

class SessionController:

    def load_session_relations(session_row) -> dict:
        data = dict(session_row._mapping)

        case = DBHelper.execute_query(
            cases_table
            .select()
            .where(
                cases_table.c.id == data['case_id'],
                cases_table.c.is_deleted == False
            )
            .limit(1)
        ).mappings().fetchone()

        return {
            **data,
            'case': {'id': case['id'], 'case_name': case['case_name']} if case else None,
        }

    def get_all_session(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)

        sessions = DBHelper.execute_query(
            sessions_table
            .select()
            .where(sessions_table.c.case_id == case_id)
        ).fetchall()

        if not sessions:
            return APIHelper.send_error_response(
                errorMessageKey="translations.SESSION_NOT_FOUND"
            )

        return APIHelper.send_success_response(
            data=[
            SessionResponse.model_validate(
                SessionController.load_session_relations(session)
            ).model_dump()
            for session in sessions
        ],
            successMessageKey="translations.SUCCESS"
        )

    def get_session_by_id(session_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)
        
        session= DBHelper.execute_query(
            sessions_table
            .select()
            .where(sessions_table.c.id == session_id)
            .limit(1)
        ).fetchone()

        if not session:
            return APIHelper.send_error_response(
                errorMessageKey="translations.SESSION_NOT_FOUND"
            )

        data = SessionResponse.model_validate(
            SessionController.load_session_relations(session)
        ).model_dump()
        return APIHelper.send_success_response(
            data=data,
            successMessageKey="translations.SUCCESS"
        )

    def create_session(
        session_data: CreateSessionRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)
        
        case = DBHelper.execute_query(
            cases_table
            .select()
            .where(
                cases_table.c.id == session_data.case_id,
                cases_table.c.is_deleted == False
            )
            .limit(1)
        ).fetchone()
        
        if not case:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        session_date = session_data.session_date or date.today()

        insert_res = DBHelper.execute_query(
            sessions_table.insert().values(
                case_id=session_data.case_id,
                result=session_data.result,
                session_date=session_date,
                court_type=session_data.court_type
            )
        )

        if hasattr(insert_res, 'inserted_primary_key') and insert_res.inserted_primary_key:
            session_id = insert_res.inserted_primary_key[0]
        else:
            session_id = insert_res.lastrowid

        new_session = DBHelper.execute_query(
            sessions_table
            .select()
            .where(sessions_table.c.id == session_id)
            .limit(1)
        ).fetchone()
        
        return APIHelper.send_success_response(
            data=SessionResponse.model_validate(
                SessionController.load_session_relations(new_session)
            ).model_dump(),
            successMessageKey="translations.SESSION_CREATED"
        )

    def delete_session(session_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], user)

        session = DBHelper.execute_query(
            sessions_table
            .select()
            .where(sessions_table.c.id == session_id)
            .limit(1)
        ).fetchone()
        
        if not session:
            return APIHelper.send_error_response(
                errorMessageKey="translations.SESSION_NOT_FOUND"
            )

        DBHelper.execute_query(
            sessions_table.delete().where(sessions_table.c.id == session_id)
        )
        return APIHelper.send_success_response(
            successMessageKey="translations.SESSION_DELETED"
        )
