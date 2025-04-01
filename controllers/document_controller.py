from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.document_models import (
    DocumentResponse,
    CreateDocumentRequest,
    UpdateDocumentRequest,
)
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.document import Document
from models.case import Case
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n


class DocumentController:

    def get_all_documents(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:

            documents = db.query(Document).all()

            if not documents:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.DOCUMENT_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=[
                    DocumentResponse.model_validate(document).model_dump()
                    for document in documents
                ],
                successMessageKey="translations.SUCCESS",
            )

    def get_document_by_id(document_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            document = db.query(Document).filter(Document.id == document_id).first()

            if not document:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.DOCUMENT_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=DocumentResponse.model_validate(document).model_dump(),
                successMessageKey="translations.SUCCESS",
            )

    def create_document(
        document_data: CreateDocumentRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:

            case = (
                db.query(Case)
                .filter(Case.id == document_data.case_id, Case.is_deleted == False)
                .first()
            )

            if not case:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND")
                )

            new_document = Document(
                document_name=document_data.document_name,
                uploader_id=user.id,
                case_id=document_data.case_id,
            )

            db.add(new_document)
            db.commit()
            db.refresh(new_document)

            return APIHelper.send_success_response(
                data=DocumentResponse.model_validate(new_document).model_dump(),
                successMessageKey="translations.DOCUMENT_CREATED",
            )

    def update_document(
        document_id: int, update_data: UpdateDocumentRequest, user: UserModel
    ):
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            document = db.query(Document).filter(Document.id == document_id).first()

            if not document:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.DOCUMENT_NOT_FOUND")
                )

            if update_data.document_name is not None:
                document.document_name = update_data.document_name

            db.commit()
            db.refresh(document)

            return APIHelper.send_success_response(
                data={"document_id": document.id},
                successMessageKey="translations.DOCUMENT_UPDATED",
            )

    def delete_document(document_id: int, user: UserModel):
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            document = db.query(Document).filter(Document.id == document_id).first()

            if not document:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.DOCUMENT_NOT_FOUND")
                )

            db.delete(document)
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.DOCUMENT_DELETED"
            )
