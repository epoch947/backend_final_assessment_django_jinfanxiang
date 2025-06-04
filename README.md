# backend_final_assessment_django_jinfanxiang
Django Internship Project Challenge

# Employee Management System (Django + DRF)

## Overview
This Django-based Employee Management System exposes RESTful endpoints to manage:
- Departments
- Employees
- Attendance
- Performance
- (Reports/Analytics)

It uses PostgreSQL as the database and is configured via `django-environ` (`.env`).

## Features
1. **CRUD APIs** for Departments, Employees, Attendance, and Performance.
2. **Token-based (JWT) Authentication** for all endpoints.
3. **Filtering, Searching, & Ordering** using `django-filter`.
4. **Swagger UI** via `drf-yasg` at `/swagger/`.
5. **Analytics Endpoints**:
   - `/api/reports/average-performance/`
   - `/api/reports/monthly-attendance/`
   - (Optional) `/api/reports/monthly-attendance-chart/` (PNG)

## Getting Started

### Prerequisites
- Python 3.8+ (tested with 3.9/3.10)
- PostgreSQL (e.g., 12.x or newer)
- `pip` and `virtualenv` (or `venv`)

### Installation
1. **Clone the repo**  
   ```bash
   git clone <REPO_URL>
   cd employee_project
2. **Create & activate a virtual environment**  
   ```bash
    python -m venv venv
    source venv/bin/activate    # for Linux/Mac
    # On Windows PowerShell:
    # .\venv\Scripts\Activate.ps1
3. **Install dependencies**
    pip install -r requirements.txt
4. **Set up environment variables**
    - Copy .env and fill in:
    ```
    DEBUG=True
    SECRET_KEY=your-secret-key-here
    DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DB_NAME
    ```
5. **Run migrations & seed data**
    ```bash
    python manage.py migrate
    python manage.py seed_data
6. **Create a superuser (optional, but recommended for admin)**
    ```bash
    python manage.py createsuperuser
7. **Start the server**
    ```bash
    python manage.py runserver
Swagger UI → http://127.0.0.1:8000/swagger/
