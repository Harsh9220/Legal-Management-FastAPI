# models/invoices.py
from sqlalchemy import Table, Column, Integer, String, Date, DateTime, ForeignKey, func
from config.db_config import meta

invoices_table = Table(
    "invoices",
    meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("invoice_number", Integer, nullable=False, unique=True),
    Column("client_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("amount", Integer, nullable=False),
    Column("due_on_date", Date, server_default=func.current_date()),
    Column("status", String, nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
    extend_existing=True
)
