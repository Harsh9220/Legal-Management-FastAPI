# models/user.py
from sqlalchemy import Table, Column, Integer, String, DateTime, Boolean, Enum, func
from config.db_config import meta

users_table = Table(
    "users",
    meta,
    Column("id", Integer, primary_key=True, index=True),
    Column("username", String(100), unique=True, nullable=False),
    Column("name", String(255), nullable=False),
    Column("email", String(100), unique=True, nullable=False),
    Column("hashed_password", String(255), nullable=False),
    Column("mobile", String(20)),
    Column("address", String(255)),
    Column("role", Enum("lawyer", "staff", "admin", "client", name="user_roles"), nullable=False),
    Column("is_blocked", Boolean, default=False),
    Column("is_deleted", Boolean, default=False),
    Column("created_at", DateTime, server_default=func.now()),
    Column("updated_at", DateTime, server_default=func.now(), onupdate=func.now()),
    extend_existing=True
)
