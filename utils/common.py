from sqlalchemy.orm import session
from helper.hashing import hash_context
from models.user import users_table
from utils.db_helper import DBHelper


def create_initial_admin(db: session):
    admin_exists = DBHelper.execute_query(users_table.select().where(users_table.c.role=="admin")).fetchone()
    if not admin_exists:
        admin_user = User(
            username="admin12",
            email="harsh@gmail.com",
            name="Harsh",
            hashed_password=hash_context.hash("12"),
            role="admin",
            mobile="9945673422",
            address="Default Address",
        )
        db.add(admin_user)
        db.commit()
