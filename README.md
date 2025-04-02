# Legal Management FastAPI

A role-based legal management system built with FastAPI.

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

#### For Windows (PowerShell)
```bash
python -m venv venv
venv\Scripts\activate
```

#### For macOS/Linux
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
Create a `.env` file in the root directory with the following content:

```
DB_URL=mysql+pymysql://username:password@localhost:3306/legal_management
JWT_SECRET=your_jwt_secret_key  # Generate using: openssl rand -hex 32
LOG_LEVEL=info
```

### 6. Run Liquibase Migrations
```bash
cd liquibase
liquibase update
```

#### Note: Before running the Liquibase update, create the `liquibase.properties` file in the `liquibase` directory with the following content:
```
driver=com.mysql.cj.jdbc.Driver
url=jdbc:mysql://localhost:3306/legal_management
username=your_username
password=your_password
changeLogFile=changelog/db.changelog-master.xml
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
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Project Structure
```
Legal-Management-FastAPI/
├── config/             # Database and configuration files
├── controllers/        # Business logic
├── dtos/              # Data transfer objects
├── helper/            # Helper functions and utilities
├── language/          # Internationalization files
├── liquibase/         # Database migration files
├── models/            # Database models
├── routes/            # API routes
├── utils/             # Utility functions
├── .env               # Environment variables
├── main.py           # Application entry point
└── requirements.txt   # Project dependencies
```

## Additional Notes
- Ensure all required environment variables are set before running the application.
- The system uses role-based access with **Admin, Lawyer, and Staff** roles.
- All API endpoints require **JWT authentication** except for login and registration.
- The system supports **internationalization** for error messages.

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

3. Verifying database connection and credentials in `.env` file.
4. Checking if Liquibase migrations were successful.
5. Ensuring the virtual environment is activated before running commands.
6. Verifying `JWT_SECRET` is properly set in `.env`.

To exit the virtual environment when done, use:
```bash
deactivate
```

## License
This project is licensed under the MIT License.

---
