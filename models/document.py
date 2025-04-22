from sqlalchemy import Table, Column, Integer, String, Date, DateTime, ForeignKey, func
from config.db_config import meta

documents_table = Table(
    "documents",
    meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("document_name", String(255), nullable=False),
    Column("upload_date", Date, server_default=func.current_date()),
    Column("uploader_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("case_id", Integer, ForeignKey("cases.id"), nullable=False),
    Column("document_path", String(500), nullable=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
    extend_existing=True
)
