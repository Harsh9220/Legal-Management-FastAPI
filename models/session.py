# models/sessions.py
from sqlalchemy import Table, Column, Integer, String, Date, DateTime, ForeignKey, func
from config.db_config import meta

sessions_table = Table(
    "sessions",
    meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("case_id", Integer, ForeignKey("cases.id")),
    Column("result", String(100), nullable=False),
    Column("session_date", Date, server_default=func.current_date()),
    Column("court_type", String(100), nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    extend_existing=True
)