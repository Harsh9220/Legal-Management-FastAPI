from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.session_models import SessionResponse, CreateSessionRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.session import Session as CourtSession
from models.case import Case
from datetime import date
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n

class SessionController:
    
    def get_all_session(user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            sessions = db.query(CourtSession).all()
            
            if not sessions:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.SESSION_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=[
                    SessionResponse.model_validate(session).model_dump()
                    for session in sessions
                ],
                successMessageKey="translations.SUCCESS",
            )
    
    def get_session_by_id(session_id:int,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            session=db.query(CourtSession).filter(CourtSession.id==session_id).first()
    
            if not session:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.SESSION_NOT_FOUND")
                )
            
            return APIHelper.send_success_response(
                data=SessionResponse.model_validate(session).model_dump(),
                successMessageKey="translations.SUCCESS",
            )
    
    def create_session(session_data:CreateSessionRequest,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            case=db.query(Case).filter(Case.id==session_data.case_id,Case.is_deleted==False).first()
    
            if not case:
                raise HTTPException(status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND"))
            
            session_date=session_data.session_date or date.today()
            
            new_session = CourtSession(
                case_id = session_data.case_id,
                result = session_data.result,
                session_date = session_date,
                court_type = session_data.court_type
            )
            
            db.add(new_session)
            db.commit()
            db.refresh(new_session)
            
            return APIHelper.send_success_response(
                data=SessionResponse.model_validate(new_session).model_dump(),
                successMessageKey="translations.SESSION_CREATED",
            )
    
    def delete_session(session_id:int,user:UserModel)->BaseResponseModel:
        RoleHelper.require_role(["lawyer","admin"],user)
        with SessionLocal() as db:
            session=db.query(CourtSession).filter(CourtSession.id==session_id).first()
            
            if not session:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.SESSION_NOT_FOUND")
                )
            
            db.delete(session)
            db.commit()
            
            return APIHelper.send_success_response(
                successMessageKey="translations.SESSION_DELETED"
            )