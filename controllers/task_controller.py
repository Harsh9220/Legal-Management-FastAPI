from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.task_models import TaskResponse, CreateTaskRequest, UpdateTaskRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.task import tasks_table
from models.case import cases_table
from models.user import users_table
from utils.db_helper import DBHelper
from config.constants import Constants
from datetime import date
from sqlalchemy import func, select

class TaskController:
    
    def get_all_tasks(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )
        if user.role == Constants.LAWYER:
            query = (
                tasks_table
                .select()
                .where(tasks_table.c.created_by == user.id)
            )
        elif user.role == Constants.STAFF:
            query = (
                tasks_table
                .select()
                .where(
                    (tasks_table.c.assign_to_staff == user.id) &
                    (tasks_table.c.created_by == user.id)
                )
            )
        else:  
            query = tasks_table.select()

        tasks = DBHelper.execute_query(query).mappings().fetchall()
        
        if not tasks:
            return APIHelper.send_error_response(
                errorMessageKey="translations.TASK_NOT_FOUND"
            )

        return APIHelper.send_success_response(
            data=[
            TaskResponse.model_validate(dict(task)).model_dump()
            for task in tasks
        ],
            successMessageKey="translations.SUCCESS",
        )

    def get_task_by_id(task_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )

        task = DBHelper.execute_query(
            tasks_table
            .select()
            .where(tasks_table.c.id == task_id)
            .limit(1)
        ).mappings().fetchone()
        
        if not task:
            return APIHelper.send_error_response(
                errorMessageKey="translations.TASK_NOT_FOUND"
            )
        
        task_data = dict(task)
        
        if user.role != Constants.ADMIN and task_data['created_by'] != user.id and task_data['assign_to_staff'] != user.id:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )

        return APIHelper.send_success_response(
            data=TaskResponse.model_validate(dict(task)).model_dump(),
            successMessageKey="translations.SUCCESS",
        )

    def create_task(task_data: CreateTaskRequest, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )

        case = DBHelper.execute_query(
            cases_table
            .select()
            .where(
                cases_table.c.id == task_data.case_id,
                cases_table.c.is_deleted == False
            )
            .limit(1)
        ).fetchone()
        
        if not case:
            return APIHelper.send_error_response(
                errorMessageKey="translations.CASE_NOT_FOUND"
            )

        if task_data.assign_to_staff is not None:
            staff = DBHelper.execute_query(
                users_table
                .select()
                .where(
                    users_table.c.id == task_data.assign_to_staff,
                    users_table.c.role == Constants.STAFF,
                    users_table.c.is_deleted == False
                )
            ).fetchone()
            
            if not staff:
                return APIHelper.send_error_response(
                    errorMessageKey="translations.STAFF_NOT_FOUND"
                )

        due = task_data.due_date or date.today()

        insert_res = DBHelper.execute_query(
            tasks_table.insert().values(
                task_name=task_data.task_name,
                due_date=due,
                priority=task_data.priority,
                assign_to_staff=task_data.assign_to_staff,
                case_id=task_data.case_id,
                created_by=user.id
            )
        )
        
        if hasattr(insert_res, 'inserted_primary_key') and insert_res.inserted_primary_key:
            task_id = insert_res.inserted_primary_key[0]
        else:
            task_id = insert_res.lastrowid

        new_task = DBHelper.execute_query(
            tasks_table
            .select()
            .where(tasks_table.c.id == task_id)
            .limit(1)
        ).mappings().fetchone()
        
        return APIHelper.send_success_response(
            data=TaskResponse.model_validate(dict(new_task)).model_dump(),
            successMessageKey="translations.TASK_CREATED"
        )


    def update_task(task_id: int, update_data: UpdateTaskRequest, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )

        task = DBHelper.execute_query(
            tasks_table
            .select()
            .where(tasks_table.c.id == task_id)
            .limit(1)
        ).mappings().fetchone()
        
        if not task:
            return APIHelper.send_error_response(
                errorMessageKey="translations.TASK_NOT_FOUND"
            )
            
        task_data = dict(task)
        if task_data['created_by'] != user.id and task_data['assign_to_staff'] != user.id and user.role != Constants.ADMIN:
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )

        update_value = {}
        if update_data.assign_to_staff is not None:
            staff = DBHelper.execute_query(
                users_table
                .select()
                .where(
                    users_table.c.id == update_data.assign_to_staff,
                    users_table.c.role == Constants.STAFF,
                    users_table.c.is_deleted == False
                )
            ).fetchone()
            
            if not staff:
                return APIHelper.send_error_response(
                    errorMessageKey="translations.STAFF_NOT_FOUND"
                )
            update_value['assign_to_staff'] = update_data.assign_to_staff
            
        for field in ['task_name', 'due_date', 'priority', 'status']:
            val = getattr(update_data, field, None)
            if val is not None:
                update_value[field] = val
                
        if update_value:
            DBHelper.execute_query(
                tasks_table
                .update()
                .where(tasks_table.c.id == task_id)
                .values(**update_value)
            )
            
        return APIHelper.send_success_response(
            data={"task_id": task_id},
            successMessageKey="translations.TASK_UPDATED"
        )

    def delete_task(task_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )
        task = DBHelper.execute_query(
            tasks_table
            .select()
            .where(tasks_table.c.id == task_id)
            .limit(1)
        ).mappings().fetchone()
        
        if not task:
            return APIHelper.send_error_response(
                errorMessageKey="translations.TASK_NOT_FOUND"
            )
        task_data = dict(task)
        
        if task_data['created_by'] != user.id and task_data['assign_to_staff'] != user.id and user.role != Constants.ADMIN :
            return APIHelper.send_unauthorized_error(
                errorMessageKey="translations.UNAUTHORIZED"
            )
            
        DBHelper.execute_query(
            tasks_table.delete().where(tasks_table.c.id == task_id)
        )
        
        return APIHelper.send_success_response(
            successMessageKey="translations.TASK_DELETED"
        )

    def task_dashboard(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(
            [Constants.ADMIN, Constants.LAWYER, Constants.STAFF], user
        )
        today = date.today()
        
        due_today = DBHelper.execute_query(
            select(func.count())
            .select_from(tasks_table)
            .where(
                tasks_table.c.due_date == today,
                tasks_table.c.status != "complete",
                tasks_table.c.created_by == user.id
            )
        ).scalar()
        
        overdue = DBHelper.execute_query(
            select(func.count())
            .select_from(tasks_table)
            .where(
                tasks_table.c.due_date < today,
                tasks_table.c.status != "complete",
                tasks_table.c.created_by == user.id
            )
        ).scalar()

        completed = DBHelper.execute_query(
            select(func.count())
            .select_from(tasks_table)
            .where(
                tasks_table.c.status == "complete",
                tasks_table.c.created_by == user.id
            )
        ).scalar()

        return APIHelper.send_success_response(
            data={
                "due_today_task": due_today,
                "overdue_task": overdue,
                "completed_task": completed,
            },
            successMessageKey="translations.SUCCESS",
        )
