from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.document_models import (
    DocumentResponse,
    UpdateDocumentRequest,
)
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.document import Document
from models.case import Case
from config.db_config import SessionLocal
from fastapi import HTTPException, UploadFile
import i18n
import os
import shutil


class DocumentController:
    ROOT_UPLOAD_DIR="uploaded_files"
    
    def get_all_documents(case_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
    
            documents = db.query(Document).filter(Document.case_id == case_id).all()

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
        case_id:int,file: UploadFile, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            
            case = (
                db.query(Case)
                .filter(Case.id ==case_id, Case.is_deleted == False)
                .first()
            )

            if not case:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CASE_NOT_FOUND")
                )
                
            case_folder = os.path.join(DocumentController.ROOT_UPLOAD_DIR,f'case_{case_id}')
            os.makedirs(case_folder,exist_ok=True)
            
            dest=os.path.join(case_folder, file.filename)
            
            if os.path.exists(dest):
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.DOCUMENT_EXISTS")
                )
            with open(dest,"wb") as buf:
                shutil.copyfileobj(file.file,buf)
                
                
            new_document = Document(
                document_name=file.filename,
                document_path=dest,
                uploader_id=user.id,
                case_id=case_id,
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
    ) -> BaseResponseModel:
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

    def delete_document(document_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            document = db.query(Document).filter(Document.id == document_id).first()

            if not document:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.DOCUMENT_NOT_FOUND")
                )
                
            if document.uploader_id != user.id and user.role!="admin":
                raise HTTPException(
                    status_code=403, detail=i18n.t("translations.UNAUTHORIZED")
                )
  
            try:
                os.remove(document.document_path)
            except FileNotFoundError:
                raise HTTPException(status_code=404, detail=i18n.t("translations.DOCUMENT_NOT_FOUND"))

            db.delete(document)
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.DOCUMENT_DELETED"
            )
