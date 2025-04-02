from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from dtos.auth_models import UserModel
from helper.token_helper import TokenHelper
from controllers.session_controller import SessionController
from dtos.session_models import CreateSessionRequest

session=APIRouter(tags=["session"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@session.get("/sessions",status_code=status.HTTP_200_OK)
async def get_all_session(current_user:user_dependency):
    return SessionController.get_all_session(current_user)

@session.get("/sessions/{session_id}",status_code=status.HTTP_200_OK)
async def get_session(session_id:int,current_user:user_dependency):
    return SessionController.get_session_by_id(session_id,current_user)

@session.post("/session",status_code=status.HTTP_201_CREATED)
async def create_session(session_data:CreateSessionRequest,current_user:user_dependency):
    return SessionController.create_session(session_data,current_user)

@session.delete("/session/{session_id}",status_code=status.HTTP_200_OK)
async def delete_session(session_id:int,current_user:user_dependency):
    return SessionController.delete_session(session_id,current_user)