from sqlalchemy import Column, Integer, String, DateTime, func, Date,Enum, ForeignKey
from config.db_config import Base

class Document(Base):
    __tablename__='documents'
    
    id= Column(Integer, primary_key=True, index=True)
    document_name= Column(String(255),nullable=False)
    upload_date=Column(Date,server_default=func.current_date())
    uploader_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    case_id=Column(Integer,ForeignKey("cases.id"),nullable=False)
    updated_at=Column(DateTime, server_default=func.now(),onupdate=func.now())
    created_at= Column(DateTime, server_default=func.now())