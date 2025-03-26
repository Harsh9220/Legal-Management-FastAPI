# Importing libraries
from sqlalchemy import MetaData
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Initialization
meta = MetaData()


# Creating engine
auth = f"{os.getenv('DATABASE_USER')}:{os.getenv('DATABASE_PASSWORD')}"
engine = create_engine(
    f"mysql+pymysql://{auth}@{os.getenv('DATABASE_URL')}:{os.getenv('DATABASE_PORT')}/{os.getenv('DATABASE_NAME')}",
    pool_recycle=3600,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
