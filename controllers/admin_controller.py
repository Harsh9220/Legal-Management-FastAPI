from dtos.auth_models import UserModel
from utils.db_helper import DBHelper
from config.constants import Constants
from helper.api_helper import APIHelper
from helper.role_helper import RoleHelper
from dtos.base_response_model import BaseResponseModel
from models.case import cases_table
from models.invoice import invoices_table
from models.task import tasks_table
from sqlalchemy import func, select
from datetime import date, timedelta


class AdminController:

    def get_open_closed_cases_dashboard(user: UserModel) -> BaseResponseModel:

        RoleHelper.require_role([Constants.ADMIN], user)

        open_cases = DBHelper.execute_query(
            select(func.count(cases_table.c.id)).where(
                cases_table.c.case_status == "open",
                cases_table.c.is_deleted == False,
            )
        ).scalar()

        closed_cases = DBHelper.execute_query(
            select(func.count(cases_table.c.id)).where(
                cases_table.c.case_status == "closed", cases_table.c.is_deleted == False
            )
        ).scalar()

        thirty_days_ago = date.today() - timedelta(days=30)

        new_cases = DBHelper.execute_query(
            select(func.count(cases_table.c.id)).where(
                cases_table.c.created_at >= thirty_days_ago,
                cases_table.c.is_deleted == False,
            )
        ).scalar()

        return APIHelper.send_success_response(
            data={
                "open_cases": open_cases,
                "closed_cases": closed_cases,
                "new_cases": new_cases,
            },
            successMessageKey="translations.SUCCESS",
        )

    def get_paid_unpaid_amount_dashboard(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN], user)

        unpaid_amount = (
            DBHelper.execute_query(
                select(func.sum(invoices_table.c.amount)).where(
                    invoices_table.c.status == "incomplete"
                )
            ).scalar()
            or 0
        )

        total_amount = (
            DBHelper.execute_query(select(func.sum(invoices_table.c.amount))).scalar()
            or 0
        )

        paid_amount = total_amount - unpaid_amount

        return APIHelper.send_success_response(
            data={"paid_amount": paid_amount, "unpaid_amount": unpaid_amount},
            successMessageKey="translations.SUCCESS",
        )

    def get_case_status_change_dashboard(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN], user)
        thirty_days_ago = date.today() - timedelta(days=30)

        case_status_change = DBHelper.execute_query(
            select(func.count(cases_table.c.id)).where(
                cases_table.c.updated_at >= thirty_days_ago,
                cases_table.c.is_deleted == False,
            )
        ).scalar()

        return APIHelper.send_success_response(
            data={"case_status_changes_last_30_days": case_status_change},
            successMessageKey="translations.SUCCESS",
        )

    def get_task_dashboard(user: UserModel) -> BaseResponseModel:
        RoleHelper.require_role([Constants.ADMIN], user)
        today = date.today()

        due_today = DBHelper.execute_query(select(func.count(tasks_table.c.id)).where(tasks_table.c.due_date == today, tasks_table.c.status != "complete")).scalar()
        
        overdue = DBHelper.execute_query(select(func.count(tasks_table.c.id)).where(tasks_table.c.due_date < today, tasks_table.c.status != "complete")).scalar()
        
        completed = DBHelper.execute_query(select(func.count(tasks_table.c.id)).where(tasks_table.c.status == "complete")).scalar()

        return APIHelper.send_success_response(
            data={
                "due_today_task": due_today,
                "overdue_task": overdue,
                "completed_task": completed,
            },
            successMessageKey="translations.SUCCESS",
        )
