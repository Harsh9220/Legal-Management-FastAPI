from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.user_models import UserResponse, CreateUserRequest, UpdateUserRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from helper.hashing import Hash
from helper.validation_helper import ValidationHelper
from models.user import users_table
from utils.db_helper import DBHelper
from config.constants import Constants

class UserController:

    def create_user(
        user_data: CreateUserRequest, current_user: UserModel
    ) -> BaseResponseModel:
        
        if user_data.role == Constants.ADMIN:
            return APIHelper.send_error_response(
                errorMessageKey="translations.PERMISSION_DENIED"
            )
            
        if user_data.role not in [Constants.LAWYER, Constants.STAFF, Constants.CLIENT]:
            return APIHelper.send_error_response(
                errorMessageKey="translations.INVALID_ROLE"
            )
            
        if user_data.role == Constants.LAWYER:
            RoleHelper.require_role([Constants.ADMIN], current_user)
        else:
            RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)

        if DBHelper.execute_query(
            users_table.select().where(users_table.c.username == user_data.username)
        ).fetchone():
            return APIHelper.send_error_response(
                errorMessageKey="translations.USERNAME_EXISTS"
            )
            
        if DBHelper.execute_query(
            users_table.select().where(users_table.c.email == user_data.email)
        ).fetchone():
            return APIHelper.send_error_response(
                errorMessageKey="translations.EMAIL_EXISTS"
            )
        
        ValidationHelper.is_valid_password(user_data.password)
        
        insert_res = DBHelper.execute_query(
            users_table.insert().values(
                email=user_data.email,
                username=user_data.username,
                name=user_data.name,
                address=user_data.address,
                hashed_password=Hash.get_hash(user_data.password),
                role=user_data.role,
                mobile=user_data.mobile
            )
        )
        
        if hasattr(insert_res, 'inserted_primary_key') and insert_res.inserted_primary_key:
            new_id = insert_res.inserted_primary_key[0]
        else:
            new_id = insert_res.lastrowid

        user = DBHelper.execute_query(
            users_table.select().where(users_table.c.id == new_id).limit(1)
        ).mappings().fetchone()
        
        return APIHelper.send_success_response(
            data=UserResponse.model_validate(dict(user)).model_dump(),
            successMessageKey="translations.USER_CREATED"
        )

    def get_users(role: str, current_user: UserModel) -> BaseResponseModel:
        
        if role == Constants.ADMIN:
            return APIHelper.send_error_response(
                errorMessageKey="translations.PERMISSION_DENIED"
            )

        if role not in [Constants.LAWYER, Constants.STAFF, Constants.CLIENT]:
            return APIHelper.send_error_response(
                errorMessageKey="translations.INVALID_ROLE"
            )
        
        if role == Constants.LAWYER:
            RoleHelper.require_role([Constants.ADMIN], current_user)
        else:
            RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)
        
        users = DBHelper.execute_query(
            users_table
            .select()
            .where(
                users_table.c.role == role,
                users_table.c.is_deleted == (False if role != Constants.LAWYER else True)
            )
        ).mappings().fetchall()
        
        return APIHelper.send_success_response(
            data=[UserResponse.model_validate(dict(user)).model_dump() for user in users],
            successMessageKey="translations.SUCCESS"
        )

    def get_user_by_id(user_id: int, current_user: UserModel) -> BaseResponseModel:
        
        user = DBHelper.execute_query(
            users_table.select().where(users_table.c.id == user_id).limit(1)
        ).mappings().fetchone()
        
        if not user:
            return APIHelper.send_error_response(
                errorMessageKey="translations.USER_NOT_FOUND"
            )
        user_data = dict(user)
        
        if user_data['role'] == Constants.ADMIN:
            return APIHelper.send_error_response(
                errorMessageKey="translations.PERMISSION_DENIED"
            )
        
        if user_data['role'] != Constants.LAWYER and data['is_deleted']:
            return APIHelper.send_error_response(
                errorMessageKey="translations.USER_NOT_FOUND"
            )
        
        if user_data['role'] == Constants.LAWYER:
            if user_data['id'] == current_user.id:
                RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)
            else:
                RoleHelper.require_role([Constants.ADMIN], current_user)
        else:
            if user_data['id'] == current_user.id:
                RoleHelper.require_role(
                    [Constants.ADMIN, Constants.LAWYER, Constants.STAFF, Constants.CLIENT], current_user
                )
            else:
                RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)
        return APIHelper.send_success_response(
            data=UserResponse.model_validate(user_data).model_dump(),
            successMessageKey="translations.SUCCESS"
        )

    def update_user(
        user_id: int, update_data: UpdateUserRequest, current_user: UserModel
    ) -> BaseResponseModel:
        
        user = DBHelper.execute_query(
            users_table.select().where(users_table.c.id == user_id).limit(1)
        ).mappings().fetchone()
        
        if not user:
            return APIHelper.send_error_response(
                errorMessageKey="translations.USER_NOT_FOUND"
            )
            
        data = dict(user)

        if data['role'] == Constants.ADMIN or (data['role'] != Constants.LAWYER and data['is_deleted']):
            return APIHelper.send_error_response(
                errorMessageKey="translations.PERMISSION_DENIED" if data['role']==Constants.ADMIN else "translations.USER_NOT_FOUND"
            )

        if data['role'] == Constants.LAWYER:
            RoleHelper.require_role([Constants.ADMIN], current_user)
        else:
            RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)

        if update_data.email and update_data.email != data['email']:
            if DBHelper.execute_query(
                users_table.select().where(users_table.c.email == update_data.email)
            ).fetchone():
                return APIHelper.send_error_response(
                    errorMessageKey="translations.EMAIL_EXISTS"
                )

        update_values = {}
        if update_data.email:
            update_values['email'] = update_data.email
        if update_data.password:
            ValidationHelper.is_valid_password(update_data.password)
            update_values['hashed_password'] = Hash.get_hash(update_data.password)
        for field in ['name', 'mobile', 'address']:
            val = getattr(update_data, field)
            if val is not None:
                update_values[field] = val

        if update_values:
            DBHelper.execute_query(
                users_table.update().where(users_table.c.id==user_id).values(**update_values)
            )
        return APIHelper.send_success_response(
            successMessageKey="translations.USER_UPDATED"
        )

    def hard_delete_user(user_id: int, current_user: UserModel) -> BaseResponseModel:
        user = DBHelper.execute_query(
            users_table.select().where(users_table.c.id == user_id).limit(1)
        ).mappings().fetchone()
        
        if not user or user['role']==Constants.ADMIN:
            return APIHelper.send_error_response(
                errorMessageKey="translations.PERMISSION_DENIED" if user and user['role']==Constants.ADMIN else "translations.USER_NOT_FOUND"
            )
            
        if user['role']==Constants.LAWYER:
            RoleHelper.require_role([Constants.ADMIN], current_user)
        else:
            RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)

        DBHelper.execute_query(
            users_table.delete().where(users_table.c.id==user_id)
        )
        return APIHelper.send_success_response(
            successMessageKey="translations.USER_DELETED"
        )

    def soft_delete_user(user_id: int, current_user: UserModel) -> BaseResponseModel:
        user = DBHelper.execute_query(
            users_table.select().where(users_table.c.id == user_id).limit(1)
        ).mappings().fetchone()
        
        if not user:
            return APIHelper.send_error_response(
                errorMessageKey="translations.USER_NOT_FOUND"
            )
            
        if user['role'] in [Constants.ADMIN, Constants.LAWYER]:
            return APIHelper.send_error_response(
                errorMessageKey="translations.PERMISSION_DENIED"
            )
            
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)
        
        if user['is_deleted']:
            return APIHelper.send_error_response(
                errorMessageKey="translations.USER_ALREADY_DELETED"
            )
            
        DBHelper.execute_query(
            users_table.update().where(users_table.c.id==user_id).values(is_deleted=True)
        )
        
        return APIHelper.send_success_response(
            successMessageKey="translations.USER_SOFT_DELETED"
        )

    def restore_user(user_id: int, current_user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)
        
        user = DBHelper.execute_query(
            users_table.select().where(users_table.c.id == user_id).limit(1)
        ).mappings().fetchone()
        
        if not user:
            return APIHelper.send_error_response(
                errorMessageKey="translations.USER_NOT_FOUND"
            )
            
        if user['role'] in [Constants.ADMIN, Constants.LAWYER]:
            return APIHelper.send_error_response(
                errorMessageKey="translations.PERMISSION_DENIED"
            )
            
        if not user['is_deleted']:
            return APIHelper.send_error_response(
                errorMessageKey="translations.USER_NOT_DELETED"
            )
            
        DBHelper.execute_query(
            users_table.update().where(users_table.c.id==user_id).values(is_deleted=False)
        )
        
        return APIHelper.send_success_response(
            successMessageKey="translations.USER_RESTORED"
        )

    def block_unblock_user(user_id: int, current_user: UserModel) -> BaseResponseModel:
        user = DBHelper.execute_query(
            users_table.select().where(users_table.c.id == user_id).limit(1)
        ).mappings().fetchone()
        
        if not user or user['role']==Constants.ADMIN:
            return APIHelper.send_error_response(
                errorMessageKey="translations.PERMISSION_DENIED" if user and user['role']==Constants.ADMIN else "translations.USER_NOT_FOUND"
            )
            
        if user['role'] not in [Constants.LAWYER, Constants.STAFF, Constants.CLIENT]:
            return APIHelper.send_error_response(
                errorMessageKey="translations.USER_NOT_FOUND"
            )
            
        if user['role']==Constants.LAWYER:
            RoleHelper.require_role([Constants.ADMIN], current_user)
        else:
            RoleHelper.require_role([Constants.ADMIN, Constants.LAWYER], current_user)
            
        new_status = not user['is_blocked']
        
        DBHelper.execute_query(
            users_table.update().where(users_table.c.id==user_id).values(is_blocked=new_status)
        )
        
        return APIHelper.send_success_response(
            data={"user_id": user_id, "status": "blocked" if new_status else "unblocked"},
            successMessageKey="translations.USER_STATUS_UPDATED"
        )
