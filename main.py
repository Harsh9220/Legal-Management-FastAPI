# Loading the .env file
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from os.path import join, dirname
from config.db_config import SessionLocal
from utils import common
from helper.api_helper import APIHelper
from helper.cors_helper import CORSHelper
from helper.logger_helper import setup_logger

# Setting up dotenv
dotenv_path = join(dirname(__file__), ".env")
load_dotenv(dotenv_path)

# Importing libraries
from fastapi import FastAPI, Request
from routes.auth import auth
from routes.admin import admin
from routes.lawyer import lawyer
from routes.staff import staff
from routes.client import client
from routes.case import case
from routes.document import document
from routes.invoice import invoice
from routes.task import task
from routes.session import session
from fastapi.exceptions import RequestValidationError
import i18n

#Setup Logger
setup_logger()

#Setup i18n
i18n.load_path.append('language/')
i18n.set("filename_format", "{namespace}.{locale}.{format}")
i18n.set("file_format", "json")

@asynccontextmanager
async def lifespan(app: FastAPI):
   
    db = SessionLocal()
    try:
        common.create_initial_admin(db)
        yield  
    finally:
        db.close()

# Initializing app
app = FastAPI(
    title="Boilerplate-FastAPI",
    version="0.0.1",
    lifespan=lifespan
)

#Setup CORS
CORSHelper.setup_cors(app)

# Request validation error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if exc.errors()[0]['type'] == 'value_error':
        return APIHelper.send_error_response(
            errorMessageKey =f"{exc.errors()[0]['msg']}"
        )
    else:
        return APIHelper.send_error_response(
            errorMessageKey =f"{exc.errors()[0]['loc'][1]} {exc.errors()[0]['msg']}")
        



# Including the routes
app.include_router(auth)
app.include_router(admin)
app.include_router(lawyer)
app.include_router(staff)
app.include_router(client)
app.include_router(case)
app.include_router(document)
app.include_router(invoice)
app.include_router(task)
app.include_router(session)