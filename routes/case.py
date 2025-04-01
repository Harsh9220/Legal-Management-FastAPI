from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from dtos.auth_models import UserModel
from helper.token_helper import TokenHelper
from controllers.case_controller import CaseController
from dtos.case_models import CreateCaseRequest, UpdateCaseRequest

case=APIRouter(prefix="/cases",tags=["cases"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@case.get("/",status_code=status.HTTP_200_OK)
async def get_all_cases(current_user: user_dependency):
    return CaseController.get_all_cases(current_user)

@case.get("/{case_id}",status_code=status.HTTP_200_OK)
async def get_case(case_id:int,current_user:user_dependency):
    return CaseController.get_case_by_id(case_id,current_user)

@case.post("/create-case",status_code=status.HTTP_201_CREATED)
async def create_case(case_data:CreateCaseRequest,current_user:user_dependency):
    return CaseController.create_case(case_data,current_user)

@case.put("/update-case/{case_id}",status_code=status.HTTP_200_OK)
async def update_case(case_id:int,update_data: UpdateCaseRequest, current_user:user_dependency):
    return CaseController.update_case(case_id,update_data,current_user)

@case.delete("/delete-case/{case_id}",status_code=status.HTTP_200_OK)
async def delete_case(case_id:int,current_user:user_dependency):
    return CaseController.delete_case(case_id,current_user)

@case.put("/{case_id}/soft-delete",status_code=status.HTTP_200_OK)
async def soft_delete_case(case_id:int,current_user:user_dependency):
    return CaseController.soft_delete_case(case_id,current_user)

@case.put("/{case_id}/restore",status_code=status.HTTP_200_OK)
async def restore_case(case_id:int,current_user:user_dependency):
    return CaseController.restore_case(case_id,current_user)