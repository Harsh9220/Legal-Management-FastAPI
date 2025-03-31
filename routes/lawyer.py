from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from dtos.auth_models import UserModel
from helper.token_helper import TokenHelper
from controllers.lawyer_controller import LawyerController
from dtos.lawyer_models import CreateLawyerRequest, UpdateLawyerRequest

lawyer=APIRouter(prefix="/lawyer", tags=["lawyer"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@lawyer.get("/", status_code=status.HTTP_200_OK)
async def get_all_lawyers(current_user: user_dependency):
    return LawyerController.get_all_lawyers(current_user)

@lawyer.get("/lawyer/{lawyer_id}", status_code=status.HTTP_200_OK)
async def get_lawyer(lawyer_id: int, current_user: user_dependency):
    return LawyerController.get_lawyer_by_id(lawyer_id,current_user)

@lawyer.post("/create-lawyer", status_code=status.HTTP_201_CREATED)
async def create_lawyer(lawyer_data:CreateLawyerRequest,current_user: user_dependency):
    return LawyerController.create_lawyer(lawyer_data,current_user)

@lawyer.put("/update-lawyer/{lawyer_id}", status_code=status.HTTP_200_OK)
async def update_lawyer(lawyer_id: int,update_data: UpdateLawyerRequest,current_user: user_dependency):
    return LawyerController.update_lawyer(lawyer_id,update_data,current_user)

@lawyer.put("/block-unblock-lawyer/{lawyer_id}", status_code=status.HTTP_200_OK)
async def block_unblock_lawyer(lawyer_id: int, current_user: user_dependency):
    return LawyerController.block_unblock_lawyer(lawyer_id,current_user)

@lawyer.delete("/lawyer/{lawyer_id}", status_code=status.HTTP_200_OK)
async def delete_lawyer(lawyer_id: int, current_user: user_dependency):
    return LawyerController.delete_lawyer(lawyer_id,current_user)