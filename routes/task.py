from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from dtos.auth_models import UserModel
from helper.token_helper import TokenHelper
from controllers.task_controller import TaskController
from dtos.task_models import CreateTaskRequest, UpdateTaskRequest

task = APIRouter(tags=["task"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@task.get("/tasks",status_code=status.HTTP_200_OK)
async def get_all_tasks(current_user:user_dependency):
    return TaskController.get_all_tasks(current_user)

@task.get("/tasks/dashboard",status_code=status.HTTP_200_OK)
async def task_dashboard(current_user:user_dependency):
    return TaskController.task_dashboard(current_user)

@task.get("/task/{task_id}",status_code=status.HTTP_200_OK)
async def get_task(task_id:int,current_user:user_dependency):
    return TaskController.get_task_by_id(task_id,current_user)

@task.post("/task",status_code=status.HTTP_201_CREATED)
async def create_task(task_data:CreateTaskRequest,current_user:user_dependency):
    return TaskController.create_task(task_data,current_user)

@task.put("/task/{task_id}",status_code=status.HTTP_200_OK)
async def update_task(task_id:int,update_data:UpdateTaskRequest,current_user:user_dependency):
    return TaskController.update_task(task_id,update_data,current_user)

@task.delete("/task/{task_id}",status_code=status.HTTP_200_OK)
async def delete_task(task_id:int,current_user:user_dependency):
    return TaskController.delete_task(task_id,current_user)

