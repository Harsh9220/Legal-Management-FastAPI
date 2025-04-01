from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.client_models import ClientResponse, CreateClientRequest, UpdateClientRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.client import Client
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n


class ClientController:

    def get_all_clients(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            clients = db.query(Client).filter(Client.is_deleted == False).all()

            if not clients:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=[
                    ClientResponse.model_validate(client).model_dump()
                    for client in clients
                ],
                successMessageKey="translations.SUCCESS",
            )

    def get_client_by_id(client_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            client = (
                db.query(Client)
                .filter(Client.id == client_id, Client.is_deleted == False)
                .first()
            )

            if not client:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=ClientResponse.model_validate(client).model_dump(),
                successMessageKey="translations.SUCCESS",
            )

    def create_client(client_data: CreateClientRequest, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            if db.query(Client).filter(Client.username == client_data.username).first():
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.USERNAME_EXISTS")
                )

            if db.query(Client).filter(Client.email == client_data.email).first():
                raise HTTPException(
                    status_code=400, detail=i18n.t("translations.EMAIL_EXISTS")
                )

            new_client = Client(
                username=client_data.username,
                email=client_data.email,
                name=client_data.name,
                address=client_data.address,
                mobile_number=client_data.mobile_number,
                vat_percentage=client_data.vat_percentage,
                vat_number=client_data.vat_number,
                CR_number=client_data.CR_number,
            )

            db.add(new_client)
            db.commit()
            db.refresh(new_client)

            return APIHelper.send_success_response(
                data=ClientResponse.model_validate(new_client).model_dump(),
                successMessageKey="translations.CLIENT_CREATED",
            )

    def update_client(client_id: int, update_data: UpdateClientRequest, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            client = (
                db.query(Client)
                .filter(Client.id == client_id, Client.is_deleted == False)
                .first()
            )

            if not client:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            if update_data.email is not None:
                if db.query(Client).filter(Client.email == update_data.email).first():
                    raise HTTPException(
                        status_code=400, detail=i18n.t("translations.EMAIL_EXISTS")
                    )
                client.email = update_data.email
            if update_data.name is not None:
                client.name = update_data.name
            if update_data.mobile_number is not None:
                client.mobile_number = update_data.mobile_number
            if update_data.vat_percentage is not None:
                client.vat_percentage = update_data.vat_percentage
            if update_data.vat_number is not None:
                client.vat_number = update_data.vat_number
            if update_data.CR_number is not None:
                client.CR_number = update_data.CR_number
            if update_data.address is not None:
                client.address = update_data.address

            db.commit()
            db.refresh(client)

            return APIHelper.send_success_response(
                data={"client_id":client.id},
                successMessageKey="translations.CLIENT_UPDATED"
            )

    def delete_client(client_id: int, user: UserModel)-> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            client = db.query(Client).filter(Client.id == client_id).first()

            if not client:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            db.delete(client)
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.CLIENT_DELETED"
            )

    def block_unblock_client(client_id: int, user: UserModel)-> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            client = (
                db.query(Client)
                .filter(Client.id == client_id, Client.is_deleted == False)
                .first()
            )

            if not client:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            client.is_blocked = not client.is_blocked

            db.commit()
            db.refresh(client)

            new_status = "blocked" if client.is_blocked else "unblocked"
            return APIHelper.send_success_response(
                data={"client_id": client.id, "status": new_status},
                successMessageKey="translations.CLIENT_STATUS_UPDATED",
            )

    def soft_delete_client(client_id: int, user: UserModel)-> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            client = db.query(Client).filter(Client.id == client_id).first()

            if not client:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            if client.is_deleted:
                raise HTTPException(
                    status_code=409,
                    detail=i18n.t("translations.CLIENT_ALREADY_DELETED"),
                )

            client.is_deleted = True

            db.commit()
            db.refresh(client)

            return APIHelper.send_success_response(
                data={"client_id": client.id},
                successMessageKey="translations.CLIENT_SOFT_DELETED",
            )

    def restore_client(client_id: int, user: UserModel)-> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "admin"], user)
        with SessionLocal() as db:
            client = db.query(Client).filter(Client.id == client_id).first()

            if not client:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )
            if not client.is_deleted:
                raise HTTPException(
                    status_code=409, detail=i18n.t("translations.CLIENT_NOT_DELETED")
                )

            client.is_deleted = False

            db.commit()
            db.refresh(client)

            return APIHelper.send_success_response(
                data={"client_id": client.id},
                successMessageKey="translations.CLIENT_RESTORED",
            )
