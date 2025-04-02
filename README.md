# Legal Management FastAPI Project Setup Guide

## Prerequisites
- Python (>=3.8)
- pip (latest version recommended)
- Virtual environment (optional but recommended)
- Liquibase
- MySQL
- Git

## Installation Steps

### 1. Clone the Repository
```bash
git clone https://github.com/Harsh9220/Legal-Management-FastAPI.git
cd Legal-Management-FastAPI
```

### 2. Create a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

**For Windows (PowerShell)**
```bash
python -m venv venv
venv\Scripts\activate
```

**For macOS/Linux**
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Database
```sql
CREATE DATABASE legal_management;
```

### 5. Environment Setup
Copy the example environment file and update it with your values:
```bash
cp .env.example .env
```

Update the `.env` file with your specific configuration:
```env
DATABASE_USER=your_database_username
DATABASE_PASSWORD=your_database_password
DATABASE_URL=localhost
DATABASE_PORT=3306
DATABASE_NAME=legal_management
JWT_SECRET=your_jwt_secret_key  # Generate using: openssl rand -hex 32
CORS_DOMAIN=your_frontend_domain
```

### 6. Liquibase Setup
Copy the example properties file and update it with your database credentials:
```bash
cp liquibase/liquibase.properties.example liquibase/liquibase.properties
```

Update `liquibase.properties` with your database credentials:
```properties
driver=com.mysql.cj.jdbc.Driver
url=jdbc:mysql://localhost:3306/legal_management
username=your_username
password=your_password
changeLogFile=changelog/db.changelog-master.xml
```

Then run the migrations:
```bash
cd liquibase
liquibase update
```

## Running the FastAPI Application

### Start the Application
```bash
uvicorn main:app --reload
```

### Start Application on Specific Port
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation
Once the application is running, you can access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure
```
Legal-Management-FastAPI/
├── config/             # Database configuration
├── controllers/        # Business logic for each module
│   ├── auth_controller.py
│   ├── case_controller.py
│   ├── client_controller.py
│   ├── document_controller.py
│   ├── invoice_controller.py
│   ├── lawyer_controller.py
│   ├── session_controller.py
│   ├── staff_controller.py
│   └── task_controller.py
├── dtos/              # Data transfer objects
├── helper/            # Helper functions
│   ├── api_helper.py
│   ├── cors_helper.py
│   ├── date_helper.py
│   ├── hashing.py
│   ├── logger_helper.py
│   ├── role_helper.py
│   ├── token_helper.py
│   └── validation_helper.py
├── language/          # Internationalization files
├── liquibase/         # Database migrations
│   ├── changelog/
│   └── liquibase.properties.example
├── models/           # Database models
├── routes/           # API endpoints
├── utils/            # Utility functions
├── .env.example      # Example environment variables
├── .gitignore       # Git ignore rules
├── main.py          # Application entry point
└── requirements.txt  # Project dependencies
```

## Features
- 👥 User Management (Admin, Lawyer, Staff)
- 📁 Case Management
- 👤 Client Management
- 📄 Document Management
- 📋 Task Management
- 💰 Invoice Management
- 📅 Session Management
- 🔐 Role-based Access Control
- 🌐 Internationalization Support
- 🔒 JWT Authentication
- 📝 Database Migrations with Liquibase

## Security Features
- JWT Authentication
- Password Hashing with bcrypt
- Role-based Access Control
- Environment Variable Protection
- Database Credentials Security

## Additional Notes
- The `.env` and `liquibase.properties` files are not tracked in git for security
- Use the provided `.env.example` and `liquibase.properties.example` as templates
- All API endpoints except login/register require JWT authentication
- The system supports multiple languages through i18n
- Database migrations are handled through Liquibase

## Troubleshooting

If you encounter any issues, try:
1. Checking Python and pip versions:
   ```bash
   python --version
   pip --version
   ```
2. Ensuring dependencies are installed correctly:
   ```bash
   pip list
   ```
3. Verifying database connection:
   ```bash
   mysql -u your_username -p -h localhost
   ```
4. Checking environment variables are set correctly in `.env`
5. Ensuring Liquibase migrations are up to date
6. Verifying the virtual environment is activated

To exit the virtual environment when done, use:
```bash
deactivate
```
