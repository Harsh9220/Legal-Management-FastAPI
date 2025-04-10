from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.invoice_models import (
    InvoiceResponse,
    CreateInvoiceRequest,
    UpdateInvoiceRequest,
)
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.invoice import Invoice
from models.user import User
from datetime import date
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n


class InvoiceController:

    def get_all_invoice(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin", "client"], user)
        with SessionLocal() as db:
            if user.role == "client":
                invoices = db.query(Invoice).filter(Invoice.client_id == user.id).all()
            elif user.role == "admin":
                invoices = db.query(Invoice).all()
            else:
                invoices = db.query(Invoice).filter(Invoice.created_by == user.id).all()

            if not invoices:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.INVOICE_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=[
                    InvoiceResponse.model_validate(invoice).model_dump()
                    for invoice in invoices
                ],
                successMessageKey="translations.SUCCESS",
            )

    def get_invoice_by_id(invoice_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            if user.role != "admin":
                invoice = (
                    db.query(Invoice)
                    .filter(Invoice.id == invoice_id, Invoice.created_by == user.id)
                    .first()
                )
            else:
                invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

            if not invoice:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.INVOICE_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=InvoiceResponse.model_validate(invoice).model_dump(),
                successMessageKey="translations.SUCCESS",
            )

    def create_invoice(
        invoice_data: CreateInvoiceRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            client = (
                db.query(User)
                .filter(
                    User.id == invoice_data.client_id,
                    User.is_deleted == False,
                    User.role == "client",
                )
                .first()
            )

            if not client:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            invoice = (
                db.query(Invoice)
                .filter(Invoice.invoice_number == invoice_data.invoice_number)
                .first()
            )

            if invoice:
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.INVOICE_NUM_EXISTS")
                )

            due_date = invoice_data.due_on_date or date.today()

            new_invoice = Invoice(
                invoice_number=invoice_data.invoice_number,
                client_id=invoice_data.client_id,
                created_by=user.id,
                amount=invoice_data.amount,
                due_on_date=due_date,
            )

            db.add(new_invoice)
            db.commit()
            db.refresh(new_invoice)

            return APIHelper.send_success_response(
                data=InvoiceResponse.model_validate(new_invoice).model_dump(),
                successMessageKey="translations.INVOICE_CREATED",
            )

    def update_invoice(
        invoice_id: int, update_data: UpdateInvoiceRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

            if not invoice:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.INVOICE_NOT_FOUND")
                )

            if invoice.created_by != user.id and user.role == "lawyer":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.UNAUTHORIZED")
                )

            if update_data.client_id is not None:
                new_client = (
                    db.query(User)
                    .filter(
                        User.id == update_data.client_id,
                        User.is_deleted == False,
                        User.role == "client",
                    )
                    .first()
                )
                if not new_client:
                    raise HTTPException(
                        status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                    )
                invoice.client_id = update_data.client_id

            if update_data.amount is not None:
                invoice.amount = update_data.amount
            if update_data.due_on_date is not None:
                invoice.due_on_date = update_data.due_on_date
            if update_data.status is not None:
                invoice.status = update_data.status

            db.commit()
            db.refresh(invoice)

            return APIHelper.send_success_response(
                data={"invoice_id": invoice.id},
                successMessageKey="translations.INVOICE_UPDATED",
            )

    def delete_invoice(invoice_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

            if not invoice:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.INVOICE_NOT_FOUND")
                )

            if invoice.created_by != user.id and user.role == "lawyer":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.UNAUTHORIZED")
                )

            db.delete(invoice)
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.INVOICE_DELETED"
            )
