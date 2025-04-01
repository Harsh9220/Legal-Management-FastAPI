from dtos.auth_models import UserModel
from dtos.base_response_model import BaseResponseModel
from dtos.task_models import TaskResponse, CreateTaskRequest, UpdateTaskRequest
from helper.role_helper import RoleHelper
from helper.api_helper import APIHelper
from models.task import Task
from models.case import Case
from models.user import User
from datetime import date
from config.db_config import SessionLocal
from fastapi import HTTPException
import i18n


class TaskController:

    def get_all_tasks(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            tasks = db.query(Task).all()

            if not tasks:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.TASK_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=[TaskResponse.model_validate(task).model_dump() for task in tasks],
                successMessageKey="translations.SUCCESS",
            )

    def get_task_by_id(task_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            task = db.query(Task).filter(Task.id == task_id).first()

            if not task:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.TASK_NOT_FOUND")
                )

            return APIHelper.send_success_response(
                data=TaskResponse.model_validate(task).model_dump(),
                successMessageKey="translations.SUCCESS",
            )

    def create_task(task_data: CreateTaskRequest, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:

            case = (
                db.query(Case)
                .filter(Case.id == task_data.case_id, Case.is_deleted == False)
                .first()
            )

            if not case:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.CLIENT_NOT_FOUND")
                )

            if task_data.assign_to_staff is not None:
                staff = (
                    db.query(User)
                    .filter(
                        User.id == task_data.assign_to_staff,
                        User.role == "staff",
                        User.is_deleted == False,
                    )
                    .first()
                )
                if not staff:
                    raise HTTPException(
                        status_code=404, detail=i18n.t("translations.STAFF_NOT_FOUND")
                    )

            due_date = task_data.due_date or date.today()

            new_task = Task(
                task_name=task_data.task_name,
                due_date=due_date,
                priority=task_data.priority,
                assign_to_staff=task_data.assign_to_staff,
                case_id=task_data.case_id,
                created_by=user.id,
            )

            db.add(new_task)
            db.commit()
            db.refresh(new_task)

            return APIHelper.send_success_response(
                data=TaskResponse.model_validate(new_task).model_dump(),
                successMessageKey="translations.TASK_CREATED",
            )

    def update_task(
        task_id: int, update_data: UpdateTaskRequest, user: UserModel
    ) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            task = db.query(Task).filter(Task.id == task_id).first()

            if not task:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.TASK_NOT_FOUND")
                )

            if update_data.task_name is not None:
                task.task_name = update_data.task_name
            if update_data.due_date is not None:
                task.due_date = update_data.due_date
            if update_data.priority is not None:
                task.priority = update_data.priority
            if update_data.assign_to_staff is not None:
                staff = (
                    db.query(User)
                    .filter(
                        User.id == update_data.assign_to_staff,
                        User.role == "staff",
                        User.is_deleted == False,
                    )
                    .first()
                )
                if not staff:
                    raise HTTPException(
                        status_code=404, detail=i18n.t("translations.SAFF_NOT FOUND")
                    )
                task.assign_to_staff = update_data.assign_to_staff
            if update_data.status is not None:
                task.status = update_data.status

            db.commit()
            db.refresh(task)

            return APIHelper.send_success_response(
                data={"task_id": task.id},
                successMessageKey="translations.TASK_UPDATED",
            )

    def delete_task(task_id: int, user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            task = db.query(Task).filter(Task.id == task_id).first()

            if not task:
                raise HTTPException(
                    status_code=404, detail=i18n.t("translations.TASK_NOT_FOUND")
                )

            db.delete(task)
            db.commit()

            return APIHelper.send_success_response(
                successMessageKey="translations.TASK_DELETED"
            )

    def task_dashboard(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role(["lawyer", "staff", "admin"], user)
        with SessionLocal() as db:
            today=date.today()

            due_today = db.query(Task).filter(Task.due_date==today,Task.status!="complete").count()
            
            overdue = db.query(Task).filter(Task.due_date < today, Task.status!="complete").count()
            
            completed = db.query(Task).filter(Task.status == "complete").count()
            
            return APIHelper.send_success_response(
                data={
                    "due_today_task": due_today,
                    "overdue_task": overdue,
                    "completed_task": completed,
                },
                successMessageKey="translations.SUCCESS",
            )