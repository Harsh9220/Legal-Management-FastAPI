from sqlalchemy.orm import session
from helper.hashing import hash_context
from models.user import User

def create_initial_admin(db:session):
        admin_exists = db.query(User).filter(User.role == "admin").first()
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