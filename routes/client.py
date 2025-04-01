from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from dtos.auth_models import UserModel
from helper.token_helper import TokenHelper
from controllers.client_controller import ClientController
from dtos.client_models import CreateClientRequest,UpdateClientRequest

client=APIRouter(prefix="/clients",tags=["clients"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@client.get("/",status_code=status.HTTP_200_OK)
async def get_all_clients(current_user:user_dependency):
    return ClientController.get_all_clients(current_user)
    
@client.get("/client/{client_id}",status_code=status.HTTP_200_OK)
async def get_client(client_id:int,current_user:user_dependency):
    return ClientController.get_client_by_id(client_id,current_user)

@client.post("/create-client",status_code=status.HTTP_201_CREATED)
async def create_client(client_data:CreateClientRequest,current_user:user_dependency):
    return ClientController.create_client(client_data,current_user)

@client.put("/update-client/{client_id}",status_code=status.HTTP_200_OK)
async def update_client(client_id:int, update_data:UpdateClientRequest,current_user:user_dependency):
    return ClientController.update_client(client_id,update_data,current_user)

@client.delete("/delete-client/{client_id}", status_code=status.HTTP_200_OK)
async def delete_client(client_id: int, current_user: user_dependency):
    return ClientController.delete_client(client_id,current_user)

@client.put("/block-unblock-client/{client_id}",status_code=status.HTTP_200_OK)
async def block_unblock_client(client_id:int,current_user:user_dependency):
    return ClientController.block_unblock_client(client_id,current_user)

@client.put("/{client_id}/soft-delete",status_code=status.HTTP_200_OK)
async def soft_delete_client(client_id:int, current_user:user_dependency):
    return ClientController.soft_delete_client(client_id,current_user)

@client.put("/{client_id}/restore", status_code=status.HTTP_200_OK)
async def restore_client(client_id: int, current_user: user_dependency):
    return ClientController.restore_client(client_id,current_user)