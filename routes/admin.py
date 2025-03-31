from fastapi import APIRouter, Depends
from typing import Annotated
from helper.token_helper import TokenHelper
from dtos.auth_models import UserModel
from starlette import status
from controllers.admin_controller import AdminController

admin= APIRouter(prefix="/admin/dashboard", tags=["admin"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@admin.get("/open-closed-cases",status_code=status.HTTP_200_OK)
async def open_closed_cases_dashboard(current_user:user_dependency):
    return AdminController.get_open_closed_cases_dashboard(current_user)

@admin.get("/paid_unpaid_amount",status_code=status.HTTP_200_OK)
async def paid_unpaid_amount_dashboard(current_user:user_dependency):
    return AdminController.get_paid_unpaid_amount_dashboard(current_user)

@admin.get("/case_status_change",status_code=status.HTTP_200_OK)
async def case_status_change_dashboard(current_user:user_dependency):
    return AdminController.get_case_status_change_dashboard(current_user)

@admin.get("/task",status_code=status.HTTP_200_OK)
async def task_dashboard(current_user:user_dependency):
    return AdminController.get_task_dashboard(current_user)