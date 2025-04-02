from dtos.auth_models import UserModel
from config.db_config import SessionLocal
from helper.api_helper import APIHelper
from helper.role_helper import RoleHelper
from dtos.base_response_model import BaseResponseModel
from models.case import Case
from models.invoice import Invoice
from models.task import Task
from sqlalchemy import func
from datetime import date, timedelta


class AdminController:
    
    def get_open_closed_cases_dashboard(user: UserModel)->BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            open_cases = (
                db.query(Case)
                .filter(Case.case_status == "open", Case.is_deleted == False)
                .count()
            )

            closed_cases = (
                db.query(Case)
                .filter(Case.case_status == "closed", Case.is_deleted == False)
                .count()
            )

            thirty_days_ago = date.today() - timedelta(days=30)

            new_cases = (
                db.query(Case)
                .filter(Case.created_at >= thirty_days_ago, Case.is_deleted == False)
                .count()
            )

            return APIHelper.send_success_response(
                data={
                    "open_cases": open_cases,
                    "closed_cases": closed_cases,
                    "new_cases": new_cases,
                },
                successMessageKey="translations.SUCCESS",
            )

    def get_paid_unpaid_amount_dashboard(user: UserModel)->BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            today = date.today()
            unpaid_amount = (
                db.query(func.sum(Invoice.amount))
                .filter(Invoice.due_on_date < today)
                .scalar()
                or 0
            )
            total_amount = db.query(func.sum(Invoice.amount)).scalar() or 0
            paid_amount = total_amount - unpaid_amount

            return APIHelper.send_success_response(
                data={"paid_amount": paid_amount, "unpaid_amount": unpaid_amount},
                successMessageKey="translations.SUCCESS",
            )

    def get_case_status_change_dashboard(user: UserModel)->BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            thirty_days_ago = date.today() - timedelta(days=30)

            case_status_change = (
                db.query(Case)
                .filter(Case.updated_at >= thirty_days_ago, Case.is_deleted == False)
                .count()
            )

            return APIHelper.send_success_response(
                data={"case_status_changes_last_30_days": case_status_change},
                successMessageKey="translations.SUCCESS",
            )

    def get_task_dashboard(user: UserModel)->BaseResponseModel:
        RoleHelper.require_role(["admin"], user)
        with SessionLocal() as db:
            today = date.today()

            due_today = (
                db.query(Task)
                .filter(Task.due_date == today, Task.status != "complete")
                .count()
            )

            overdue = (
                db.query(Task)
                .filter(Task.due_date < today, Task.status != "complete")
                .count()
            )

            completed = db.query(Task).filter(Task.status == "complete").count()

            return APIHelper.send_success_response(
                data={
                    "due_today_task": due_today,
                    "overdue_task": overdue,
                    "completed_task": completed,
                },
                successMessageKey="translations.SUCCESS",
            )