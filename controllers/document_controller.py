from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.document_models import (
    DocumentResponse,
    UpdateDocumentRequest,
)
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.document import documents_table
from models.case import cases_table
from utils.db_helper import DBHelper
from config.constants import Constants
from fastapi import UploadFile
import os
import shutil

class DocumentController:
    ROOT_UPLOAD_DIR = "uploaded_files"

    def get_all_documents(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )

        documents= DBHelper.execute_query(
            documents_table
            .select()
            .where(
                documents_table.c.case_id == case_id
            )
        ).mappings().fetchall()

        if not documents:
            return APIHelper.send_error_response(
                errorMessageKey="translations.DOCUMENT_NOT_FOUND"
            )

        return APIHelper.send_success_response(
            data=[
                DocumentResponse.model_validate(document).model_dump()
                for document in documents
            ],
            successMessageKey="translations.SUCCESS",
        )

    def get_document_by_id(document_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )
        document= DBHelper.execute_query(
                documents_table
                .select()
                .where(documents_table.c.id == document_id)
                .limit(1)
            ).mappings().fetchone()

        if not document:
            return APIHelper.send_error_response(
                errorMessageKey="translations.DOCUMENT_NOT_FOUND"
            )

        return APIHelper.send_success_response(
            data=DocumentResponse.model_validate(document).model_dump(),
            successMessageKey="translations.SUCCESS",
        )

    def create_document(
        case_id: int,
        file: UploadFile,
        user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )
        
        case = DBHelper.execute_query(
                cases_table
                .select()
                .where(
                    cases_table.c.id == case_id,
                    cases_table.c.is_deleted == False
                )
            ).fetchone()
        
        if not case:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        case_folder = os.path.join(DocumentController.ROOT_UPLOAD_DIR, f'case_{case_id}')
        os.makedirs(case_folder, exist_ok=True)
        dest = os.path.join(case_folder, file.filename)
        
        if os.path.exists(dest):
            return APIHelper.send_error_response(
                errorMessageKey="translations.DOCUMENT_EXISTS"
            )
            
        with open(dest, "wb") as buf:
            shutil.copyfileobj(file.file, buf)

        insert_result = DBHelper.execute_query(
            documents_table.insert().values(
                document_name=file.filename,
                document_path=dest,
                uploader_id=user.id,
                case_id=case_id
            )
        )
        if hasattr(insert_result, 'inserted_primary_key') and insert_result.inserted_primary_key:
            doc_id = insert_result.inserted_primary_key[0]
        else:
            doc_id = insert_result.lastrowid

        new_document= DBHelper.execute_query(
                documents_table
                .select()
                .where(documents_table.c.id == doc_id)
                .limit(1)
            ).mappings().fetchone()

        return APIHelper.send_success_response(
            data=DocumentResponse.model_validate(new_document).model_dump(),
            successMessageKey="translations.DOCUMENT_CREATED"
        )

    def update_document(
        document_id: int,
        update_data: UpdateDocumentRequest,
        user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )
        document = DBHelper.execute_query(
            documents_table
            .select()
            .where(documents_table.c.id == document_id)
            .limit(1)
        ).fetchone()
        
        if not document:
            return APIHelper.send_error_response(
                errorMessageKey="translations.DOCUMENT_NOT_FOUND"
            )

        update_values = {}
        if update_data.document_name is not None:
            update_values['document_name'] = update_data.document_name

        if update_values:
            DBHelper.execute_query(
                documents_table
                .update()
                .where(documents_table.c.id == document_id)
                .values(**update_values)
            )

        return APIHelper.send_success_response(
            data={"document_id": document_id},
            successMessageKey="translations.DOCUMENT_UPDATED"
        )

    def delete_document(document_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )
        
        document = DBHelper.execute_query(
            documents_table
            .select()
            .where(documents_table.c.id == document_id)
            .limit(1)
        ).mappings().fetchone()
        
        if not document:
            return APIHelper.send_error_response(
                errorMessageKey="translations.DOCUMENT_NOT_FOUND"
            )
        if document['uploader_id'] != user.id and user.role != Constants.ADMIN:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )

        try:
            os.remove(document['document_path'])
        except FileNotFoundError:
            return APIHelper.send_error_response(
                errorMessageKey="translations.DOCUMENT_NOT_FOUND"
            )

        DBHelper.execute_query(
            documents_table.delete().where(documents_table.c.id == document_id)
        )

        return APIHelper.send_success_response(
            successMessageKey="translations.DOCUMENT_DELETED"
        )
