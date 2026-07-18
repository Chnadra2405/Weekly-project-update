# School Management System

A full-stack School Management System with a Python/FastAPI backend, React.js frontend, and SQL Server database.

---

## Tech Stack

| Layer    | Technology                              |
|----------|-----------------------------------------|
| Backend  | Python 3.11, FastAPI, SQLAlchemy 2.0    |
| Frontend | React 18, Vite, Bootstrap 5, Axios      |
| Database | SQL Server (ODBC Driver 17, Windows Auth)|

---

## Project Structure

```
school-management-system/
 backend/
   app/
     domain/         - Entities and repository interfaces
     application/    - DTOs and service layer
     infrastructure/ - SQLAlchemy models and repo implementations
     presentation/   - FastAPI routers
   main.py           - FastAPI app entry point
   requirements.txt
 frontend/
   src/
     components/     - Sidebar, Navbar
     pages/          - Dashboard, Students, Teachers, etc.
     services/       - Axios API clients
   package.json
 database/
   schema.sql        - SQL Server DDL + seed data
```

---

## Setup

### 1. Database

Run the SQL script against your SQL Server instance:

```
sqlcmd -S localhost -E -i database/schema.sql
```

Or open `database/schema.sql` in SQL Server Management Studio and execute it.

### 2. Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: http://localhost:8000/docs

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at: http://localhost:5173

---

## API Endpoints

| Resource    | Base URL           |
|-------------|--------------------|
| Students    | /api/v1/students   |
| Teachers    | /api/v1/teachers   |
| Classes     | /api/v1/classes    |
| Subjects    | /api/v1/subjects   |
| Enrollments | /api/v1/enrollments|
| Grades      | /api/v1/grades     |
| Attendance  | /api/v1/attendance |
| Dashboard   | /api/v1/dashboard/stats |

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- SQL Server (any edition) with ODBC Driver 17 installed
- Windows Authentication enabled on SQL Server (default config)
