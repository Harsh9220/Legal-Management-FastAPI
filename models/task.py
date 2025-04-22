# models/tasks.py
from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Enum, ForeignKey, func
from config.db_config import meta

tasks_table = Table(
    "tasks",
    meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("task_name", String(255), nullable=False),
    Column("due_date", Date, server_default=func.current_date()),
    Column("priority", Enum("high", "medium", "low", name="priority"), nullable=False),
    Column("assign_to_staff", Integer, ForeignKey("users.id")),
    Column("status", Enum("complete", "need review", "incomplete", name="status"), nullable=False, default="incomplete"),
    Column("case_id", Integer, ForeignKey("cases.id"), nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
    Column("created_at", DateTime, server_default=func.now()),
    extend_existing=True
)