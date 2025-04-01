from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from controllers.staff_controller import StaffController
from dtos.auth_models import UserModel
from dtos.staff_models import CreateStaffRequest,UpdateStaffRequest
from helper.token_helper import TokenHelper

staff = APIRouter(prefix="/staff", tags=["staff"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@staff.get("/staffs", status_code=status.HTTP_200_OK)
async def get_all_staffs(current_user: user_dependency):
    return StaffController.get_all_staffs(current_user)
    
@staff.get("/{staff_id}", status_code=status.HTTP_200_OK)
async def get_staff(staff_id: int, current_user: user_dependency):
    return StaffController.get_staff_by_id(staff_id,current_user)
    
@staff.post("/create-staff", status_code=status.HTTP_201_CREATED)
async def lawyer_create_staff(
    staff_data: CreateStaffRequest, current_user: user_dependency
):
    return StaffController.create_staff(staff_data,current_user)

@staff.put("/update-staff/{staff_id}", status_code=status.HTTP_200_OK)
async def update_staff(
    staff_id: int,
    update_data: UpdateStaffRequest,
    current_user: user_dependency
):
    return StaffController.update_staff(staff_id,update_data,current_user)

@staff.delete("/delete-staff/{staff_id}", status_code=status.HTTP_200_OK)
async def delete_staff(staff_id: int, current_user: user_dependency):
    return StaffController.delete_staff(staff_id,current_user)

@staff.put("/block-unblock-staff/{staff_id}", status_code=status.HTTP_200_OK)
async def block_unblock_staff(staff_id: int, current_user: user_dependency):
    return StaffController.block_unblock_staff(staff_id,current_user)

@staff.put("/{staff_id}/soft-delete", status_code=status.HTTP_200_OK)
async def soft_delete_staff(staff_id: int, current_user: user_dependency):
    return StaffController.soft_delete_staff(staff_id,current_user)

@staff.put("/{staff_id}/restore", status_code=status.HTTP_200_OK)
async def restore_staff(staff_id: int, current_user: user_dependency):
    return StaffController.restore_staff(staff_id,current_user)