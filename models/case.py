from sqlalchemy import Table, Column, Integer, String, Date, DateTime, Boolean, Enum, ForeignKey, func
from config.db_config import meta

case_staff_table = Table(
    "case_staff",
    meta,
    Column("case_id", Integer, ForeignKey("cases.id", ondelete="CASCADE"), primary_key=True),
    Column("staff_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    extend_existing=True
)

cases_table = Table(
    "cases",
    meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("case_number", String(255), nullable=False, unique=True),
    Column("case_name", String(255), nullable=False),
    Column("case_category", Enum("theft", "fraud", "divorce", name="case_category"), nullable=False),
    Column("case_stage", Enum("appeal", "first degree", name="case_stage"), nullable=False),
    Column("case_status", Enum("open", "closed", name="case_status"), nullable=False, server_default="open"),
    Column("issue_date", Date, server_default=func.current_date()),
    Column("city_name", String(255)),
    Column("client_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("lawyer_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("created_by", Integer, ForeignKey("users.id"), nullable=False),
    Column("remarks", String),
    Column("is_deleted", Boolean, nullable=False, server_default="false"),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
    extend_existing=True
)
