from models.user import User
from config.db_config import SessionLocal


class DBHelper:
    def get_user_by_email(email: str):
        with SessionLocal() as db:
            return db.query(User).filter(User.email==email).first()

    def get_user_by_id(id: int):
        with SessionLocal() as db:
            return db.query(User).filter(User.id==id).first()
    
    def get_user_by_username(username:str):
        with SessionLocal() as db:
            return db.query(User).filter(User.username==username).first()
