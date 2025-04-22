from sqlalchemy import select, Executable
from models.user import users_table
from config.db_config import engine
from sqlalchemy.exc import SQLAlchemyError

class DBHelper:
        
    def execute_query(query:Executable):
        with engine.connect() as db:
            try:
                result = db.execute(query)
                db.commit()
                return result
            except SQLAlchemyError:
                db.rollback()
                raise
    
    def get_user_by_email(email: str):
        user = DBHelper.execute_query(users_table.select().where(users_table.c.email==email)).fetchone()
        return user

    def get_user_by_id(id: int):
        user = DBHelper.execute_query(users_table.select().where(users_table.c.id==id)).fetchone()
        return user

    def get_user_by_username(username: str):
        user = DBHelper.execute_query(users_table.select().where(users_table.c.username==username)).fetchone()
        return user
