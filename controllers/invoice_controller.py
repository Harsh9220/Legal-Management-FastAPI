from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.invoice_models import (
    InvoiceResponse,
    CreateInvoiceRequest,
    UpdateInvoiceRequest,
)
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.invoice import invoices_table
from models.user import users_table
from utils.db_helper import DBHelper
from config.constants import Constants
from datetime import date

class InvoiceController:

    def load_invoice_relations(invoice_row) -> dict:
        
        data = dict(invoice_row._mapping)

        client = DBHelper.execute_query(
            users_table
            .select()
            .where(
                users_table.c.id == data["client_id"],
                users_table.c.is_deleted == False,
                users_table.c.role == Constants.CLIENT
            )
        ).mappings().fetchone()

        creator = DBHelper.execute_query(
            users_table
            .select()
            .where(
                users_table.c.id == data["created_by"],
                users_table.c.is_deleted == False
            )
        ).mappings().fetchone()

        return {
            **data,
            "client": {"id": client["id"], "name": client["name"]} if client else None,
            "creator": {"id": creator["id"], "name": creator["name"]} if creator else None,
        }

    
    def get_all_invoice(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.CLIENT], user
        )
        if user.role == Constants.CLIENT:
            query = (
                invoices_table
                .select()
                .where(invoices_table.c.client_id == user.id)
            )
        elif user.role == Constants.ADMIN:
            query = invoices_table.select()
        else:  
            query = (
                invoices_table
                .select()
                .where(invoices_table.c.created_by == user.id)
            )

        invoices = DBHelper.execute_query(query).fetchall()
        if not invoices:
            return APIHelper.send_error_response(
                errorMessageKey="translations.INVOICE_NOT_FOUND"
            )

        return APIHelper.send_success_response(
            data=[
            InvoiceResponse.model_validate(
                InvoiceController.load_invoice_relations(invoice)
            ).model_dump()
            for invoice in invoices
        ],
            successMessageKey="translations.SUCCESS",
        )

    @staticmethod
    def get_invoice_by_id(invoice_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER], user
        )

        if user.role == Constants.ADMIN:
            query = (
                invoices_table
                .select()
                .where(invoices_table.c.id == invoice_id)
                .limit(1)
            )
        else:
            
            query = (
                invoices_table
                .select()
                .where(
                    invoices_table.c.id == invoice_id,
                    invoices_table.c.created_by == user.id
                )
                .limit(1)
            )
        invoice = DBHelper.execute_query(query).fetchone()
        
        if not invoice:
            return APIHelper.send_error_response(
                errorMessageKey="translations.INVOICE_NOT_FOUND"
            )
        
        return APIHelper.send_success_response(
            data=InvoiceResponse.model_validate(
            InvoiceController.load_invoice_relations(invoice)
        ).model_dump(),
            successMessageKey="translations.SUCCESS",
        )

    def create_invoice(
        invoice_data: CreateInvoiceRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER], user
        )

        client = DBHelper.execute_query(
            users_table
            .select()
            .where(
                users_table.c.id == invoice_data.client_id,
                users_table.c.is_deleted == False,
                users_table.c.role == Constants.CLIENT
            )
        ).fetchone()
        
        if not client:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CLIENT_NOT_FOUND"
            )

        exists_invoice= DBHelper.execute_query(
            invoices_table
            .select()
            .where(invoices_table.c.invoice_number == invoice_data.invoice_number)
        ).fetchone()
        
        if exists_invoice:
            return APIHelper.send_error_response(
                errorMessageKey="translations.INVOICE_NUM_EXISTS"
            )

        due = invoice_data.due_on_date or date.today()

        insert_res = DBHelper.execute_query(
            invoices_table.insert().values(
                invoice_number=invoice_data.invoice_number,
                client_id=invoice_data.client_id,
                created_by=user.id,
                amount=invoice_data.amount,
                due_on_date=due
            )
        )
        
        if hasattr(insert_res, 'inserted_primary_key') and insert_res.inserted_primary_key:
            invoice_id = insert_res.inserted_primary_key[0]
        else:
            invoice_id = insert_res.lastrowid

        new_invoice = (
            invoices_table
            .select()
            .where(invoices_table.c.id == invoice_id)
            .limit(1)
        )
        
        invoice= DBHelper.execute_query(new_invoice).fetchone()
        return APIHelper.send_success_response(
            data=InvoiceResponse.model_validate(
                InvoiceController.load_invoice_relations(invoice)
            ).model_dump(),
            successMessageKey="translations.INVOICE_CREATED"
        )

    def update_invoice(
        invoice_id: int, update_data: UpdateInvoiceRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER], user
        )
        
        invoice = DBHelper.execute_query(
            invoices_table
            .select()
            .where(invoices_table.c.id == invoice_id)
            .limit(1)
        ).mappings().fetchone()
        
        if not invoice:
            return APIHelper.send_error_response(
                errorMessageKey="translations.INVOICE_NOT_FOUND"
            )
        
        if user.role == Constants.LAWYER and invoice['created_by'] != user.id:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )
        
        update_values = {}
        if update_data.client_id is not None:
            client = DBHelper.execute_query(
                users_table
                .select()
                .where(
                    users_table.c.id == update_data.client_id,
                    users_table.c.is_deleted == False,
                    users_table.c.role == Constants.CLIENT
                )
            ).fetchone()
            if not client:
                return APIHelper.send_error_response(
                    errorMessageKey="translations.CLIENT_NOT_FOUND"
                )
            update_values['client_id'] = update_data.client_id
            
        for field in ['amount', 'due_on_date', 'status']:
            val = getattr(update_data, field, None)
            if val is not None:
                update_values[field] = val
                
        if update_values:
            DBHelper.execute_query(
                invoices_table
                .update()
                .where(invoices_table.c.id == invoice_id)
                .values(**update_values)
            )
        return APIHelper.send_success_response(
            data={"invoice_id": invoice_id},
            successMessageKey="translations.INVOICE_UPDATED"
        )

    def delete_invoice(invoice_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER], user
        )

        invoice = DBHelper.execute_query(
            invoices_table
            .select()
            .where(invoices_table.c.id == invoice_id)
            .limit(1)
        ).mappings().fetchone()
        
        if not invoice:
            return APIHelper.send_error_response(
                errorMessageKey="translations.INVOICE_NOT_FOUND"
            )
        
        if user.role == Constants.LAWYER and invoice['created_by'] != user.id:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )
        
        DBHelper.execute_query(
            invoices_table.delete().where(invoices_table.c.id == invoice_id)
        )
        return APIHelper.send_success_response(
            successMessageKey="translations.INVOICE_DELETED"
        )
