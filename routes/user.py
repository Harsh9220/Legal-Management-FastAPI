from fastapi import APIRouter, Depends, Query
from typing import Annotated
from dtos.auth_models import UserModel
from dtos.user_models import CreateUserRequest, UpdateUserRequest
from controllers.user_controller import UserController
from helper.token_helper import TokenHelper

user = APIRouter(tags=["user"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]


@user.post("/users")
def create_user(user_data: CreateUserRequest, current_user: user_dependency):
    return UserController.create_user(user_data, current_user)


@user.get("/users/{role}")
def get_users_by_role(role: str, current_user: user_dependency):
    return UserController.get_users(role, current_user)


@user.get("/users/id/{user_id}")
def get_user_by_id(user_id: int, current_user: user_dependency):
    return UserController.get_user_by_id(user_id, current_user)


@user.post("/users/{user_id}")
def update_user(
    user_id: int, update_data: UpdateUserRequest, current_user: user_dependency
):
    return UserController.update_user(user_id, update_data, current_user)


@user.delete("/users/{user_id}/hard-delete")
def hard_delete_user(user_id: int, current_user: user_dependency):
    return UserController.hard_delete_user(user_id, current_user)


@user.delete("/users/{user_id}/soft-delete")
def soft_delete_user(user_id: int, current_user: user_dependency):
    return UserController.soft_delete_user(user_id, current_user)


@user.post("/users/{user_id}/restore")
def restore_user(user_id: int, current_user: user_dependency):
    return UserController.restore_user(user_id, current_user)


@user.post("/users/{user_id}/block-unblock")
def block_unblock_user(user_id: int, current_user: user_dependency):
    return UserController.block_unblock_user(user_id, current_user)
