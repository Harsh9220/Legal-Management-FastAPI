from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from dtos.auth_models import UserModel
from helper.token_helper import TokenHelper
from controllers.document_controller import DocumentController
from dtos.document_models import CreateDocumentRequest, UpdateDocumentRequest

document=APIRouter(prefix="/document",tags=["document"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@document.get("/",status_code=status.HTTP_200_OK)
async def get_all_documents(current_user:user_dependency):
    return DocumentController.get_all_documents(current_user)

@document.get("/{document_id}",status_code=status.HTTP_200_OK)
async def get_document(document_id:int,current_user:user_dependency):
    return DocumentController.get_document_by_id(document_id,current_user)

@document.post("/create-document",status_code=status.HTTP_201_CREATED)
async def create_document(document_data:CreateDocumentRequest,current_user:user_dependency):
    return DocumentController.create_document(document_data,current_user)

@document.put("/update-document/{document_id}",status_code=status.HTTP_200_OK)
async def update_document(document_id:int,update_data:UpdateDocumentRequest, current_user:user_dependency):
    return DocumentController.update_document(document_id,update_data,current_user)

@document.delete("/delete-document/{document_id}",status_code=status.HTTP_200_OK)
async def delete_document(document_id:int,current_user:user_dependency):
    return DocumentController.delete_document(document_id,current_user)