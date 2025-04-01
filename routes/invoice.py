from fastapi import APIRouter, Depends
from starlette import status
from typing import Annotated
from dtos.auth_models import UserModel
from helper.token_helper import TokenHelper
from controllers.invoice_controller import InvoiceController
from dtos.invoice_models import CreateInvoiceRequest, UpdateInvoiceRequest

invoice=APIRouter(prefix="/invoice",tags=["invoice"])

user_dependency = Annotated[UserModel, Depends(TokenHelper.get_current_user)]

@invoice.get("/",status_code=status.HTTP_200_OK)
async def get_all_invoice(current_user:user_dependency):
    return InvoiceController.get_all_invoice(current_user)

@invoice.get("/{invoice_id}",status_code=status.HTTP_200_OK)
async def get_invoice(invoice_id:int,current_user:user_dependency):
    return InvoiceController.get_invoice_by_id(invoice_id,current_user)

@invoice.post("/create-invoice",status_code=status.HTTP_201_CREATED)
async def create_invoice(invoice_data:CreateInvoiceRequest,current_user:user_dependency):
    return InvoiceController.create_invoice(invoice_data,current_user)

@invoice.put("/update-invoice/{invoice_id}",status_code=status.HTTP_200_OK)
async def update_invoice(invoice_id:int,update_data:UpdateInvoiceRequest,current_user:user_dependency):
    return InvoiceController.update_invoice(invoice_id,update_data,current_user)

@invoice.delete("/delete-invoice/{invoice_id}",status_code=status.HTTP_200_OK)
async def delete_invoice(invoice_id:int,current_user:user_dependency):
    return InvoiceController.delete_invoice(invoice_id,current_user)