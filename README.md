# 6/2/2025 - 6/6/2025 Employee Management System (Django + DRF) by Jinfan Xiang 

A simple Employee Management System with:

* Departments
* Employees (linked to Django Users)
* Attendance Records
* Performance Reviews
* Role-based API permissions (Admin / HR / Employee)
* Swagger API Docs
* Reports (Charts rendered with Django Templates)
* Seed script to generate fake data + Users + Tokens

---

## 🎯 Project Overview & Objectives

```
employee_project/
├── attendance/          # Attendance app
│   ├── migrations/
│   ├── tests/
│   │   └── test_attendance_viewset.py
│   ├── filters.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── employees/           # Employees app
│   ├── management/
│   │   └── commands/
│   │       ├── create_admin_user.py
│   │       └── seed_data.py
│   ├── migrations/
│   ├── tests/
│   │   └── test_employee_viewset.py
│   ├── filters.py
│   ├── models.py
│   ├── permissions.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── performance/         # Performance app
│   ├── migrations/
│   ├── tests/
│   │   └── test_performance_viewset.py
│   ├── filters.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── reports/             # Reports (API + Templates)
│   ├── migrations/
│   ├── templates/
│   │   └── reports/
│   │       ├── attendance_chart.html
│   │       ├── employees_per_department.html
│   │       ├── monthly_attendance_overview.html
│   │       └── performance_chart.html
│   ├── tests/
│   │   └── test_reports_api.py
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── templates/           # Global templates
│   └── base.html
├── pgdata/              # PostgreSQL data (if used locally)
├── manage.py
├── requirements.txt
├── .env                 # Environment variables (not committed)
├── .env.example         # Sample env file
├── docker-compose.yml   # Docker Compose config (not used in final)
├── Dockerfile           # Dockerfile (not used in final)
├── user_credentials.csv         # Automatically generated user credentials
├── superuser_credentials.csv    # Superuser credentials
└── README.md            # This file
```

### Checklist of Project Goals

* [x] Create Django models with relationships:

  * **Employee**: name, email, phone\_number, address, date\_of\_joining, department (FK), user (FK)
  * **Department**: name
  * **Attendance**: employee (FK), date, status (present/absent/late)
  * **Performance**: employee (FK), rating (1–5), review\_date
* [x] Use **PostgreSQL** as the main database (configured via django-environ)
* [x] Seed at least **60** fake employees and related data using a management command
* [x] CRUD APIs for:

  * Employees, Departments, Attendance, Performance
  * Filtering (e.g., by department, date joined)
  * Pagination for large datasets
  * Sorting where applicable
  * Token-based Authentication (DRF TokenAuth)
* [x] Swagger UI documentation (drf-yasg)
* [x] Reports endpoints (JSON) + Template-rendered charts (Chart.js via Django templates)

  * Employees per Department (Pie Chart)
  * Monthly Attendance Overview (Bar Chart)
  * Performance Chart (Line Chart)
* [x] Role-based permissions:

  * **Admin**: full access (view, create, update, delete)
  * **HR**: view + update any employee, attendance, performance (no delete for HR)
  * **Employee**: view and update only own Employee record; view own attendance and performance; no create/delete
* [x] Unit Tests covering each ViewSet and Report API
* [ ] (Optional) Dockerize stack: Django + PostgreSQL + Redis caching (attempted but not finalized)

---

### Please see the demo video for my Final Project Walkthrough
[▶️ Click here to watch the demo video](https://drive.google.com/file/d/1cnwgQ3E2xLPa1Vxp7FwzwhSLpuPKUoYM/view?usp=sharing)



## 🛠️ Setup Instructions

### 1. Clone & Install Dependencies

```bash
git clone <project-repo-url>
cd employee_project
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and update values.

```bash
cp .env.example .env
```

#### Sample `.env.example`

```ini
# .env.example

# SECURITY
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
POSTGRES_DB=employee_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# Redis (for caching)
REDIS_URL=redis://127.0.0.1:6379/0

# Email (for future use)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
EMAIL_USE_TLS=True
```

> **Note**: Ensure that PostgreSQL is running and a database named `employee_db` exists. You can create it via:
>
> ```bash
> psql -U postgres -c "CREATE DATABASE employee_db;"
> ```

### 3. Apply Migrations & Create Superuser

```bash
python manage.py migrate
python manage.py create_admin_user  # Generates superuser and writes credentials to superuser_credentials.csv
```

### 4. Seed Fake Data

```bash
python manage.py seed_data
```

This command will:

* Create Departments (names truncated to 20 chars).
* Create Employee records (unique email, phone, address).
* For each Employee:

  * Create a Django **User** (group = **Employee**) with random 12-character password.
  * Link `Employee.user` to that User.
  * Create a DRF **Token** for that User.
* Seed 30 days of Attendance (present/absent/late) per Employee.
* Seed 2–5 Performance reviews per Employee on unique dates within the last year.
* Create exactly 1 HR user (`username=hr_user`) with random password.
* Create exactly 1 Admin user (`username=admin_user`, `is_superuser=True`, `is_staff=True`) with random password.
* Export `user_credentials.csv` at project root, containing something like:

  ```csv
  username,password,token,group
  alice123,SecurePass!23,f3a8c9...,Employee
  hr_user,RandomHR!78,b7d2e1...,HR
  admin_user,AdminPass!42,5e7d1c...,Admin
  ```

### 5. Run Development Server

```bash
python manage.py runserver
```

* Swagger UI: [http://127.0.0.1:8000/api/swagger/](http://127.0.0.1:8000/api/swagger/)
* ReDoc:       [http://127.0.0.1:8000/api/redoc/](http://127.0.0.1:8000/api/redoc/)
* Django Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)  (use `superuser_credentials.csv`)
* Reports (Employees per Department | Pie Chart): [http://127.0.0.1:8000/reports/employees-per-department/ ] 
* Reports (Monthly Attendance Overview | Bar Chart): [http://127.0.0.1:8000/reports/monthly-attendance-overview/ ] 


---

## 📋 API Usage Guide (APIs could be tested using tools like Postman)

API Guidance URL: `http://127.0.0.1:8000/api/redoc/`

### Authentication

* Find token (in `user_credentials.csv`) after creating users.
* Include header: `Authorization: Token <your-token>` in subsequent requests.

### Departments

```
GET    /api/departments/          # List all (Admin, HR)
POST   /api/departments/          # Create new (Admin, HR)
GET    /api/departments/{id}/     # Retrieve (Admin, HR)
PUT    /api/departments/{id}/     # Update (Admin, HR)
DELETE /api/departments/{id}/     # Delete (Admin, HR)
```

### Employees

```
GET    /api/employees/            # List all (Admin, HR), or own only (Employee)
POST   /api/employees/            # Create new (Admin, HR)
GET    /api/employees/{id}/       # Retrieve (Admin, HR, Employee self)
PUT    /api/employees/{id}/       # Update (Admin, HR, Employee self)
PATCH  /api/employees/{id}/       # Partial update
DELETE /api/employees/{id}/       # Delete (Admin only)
```

**How to use Filtering / Pagination / Search with APIs (Can be achieved using tools like Postman)**

* Filter by department: `/api/employees/?department__name=Engineering`
* Filter by date joined range: `/api/employees/?date_of_joining_min=2024-01-01&date_of_joining_max=2024-03-31`
* Search by name/email: `/api/employees/?search=alice`
* Ordering by name or date: `/api/employees/?ordering=name`
* Pagination: default `/api/employees/?page=1&size=10`

### Attendance

```
GET    /api/attendance/           # List (Admin, HR), or own (Employee)
POST   /api/attendance/           # Create (Admin, HR)
GET    /api/attendance/{id}/      # Retrieve (Admin, HR, Employee self)
PUT    /api/attendance/{id}/      # Update (Admin, HR)
PATCH  /api/attendance/{id}/      # Partial update
DELETE /api/attendance/{id}/      # Delete (Admin, HR)
```

* Filter by employee: `/api/attendance/?employee_id=12`
* Filter by date/status: `/api/attendance/?date=2025-05-01&status=present`

### Performance

```
GET    /api/performance/          # List (Admin, HR), or own (Employee)
POST   /api/performance/          # Create (Admin, HR)
GET    /api/performance/{id}/     # Retrieve (Admin, HR, Employee self)
PUT    /api/performance/{id}/     # Update (Admin, HR)
PATCH  /api/performance/{id}/     # Partial update
DELETE /api/performance/{id}/     # Delete (Admin, HR)
```

* Filter by employee: `/api/performance/?employee_id=12`
* Filter by rating/date: `/api/performance/?rating=5&review_date=2025-04-15`

### Reports (JSON APIs)

```
GET /api/reports/average-performance/             # Avg performance per department
GET /api/reports/monthly-attendance-rate/?year=2025&month=5      # Attendance rates by department
GET /api/reports/monthly-attendance-chart/?year=2025&month=5     # Monthly attendance counts
GET /api/reports/employees-per-department/          # Counts per department (pie data)
GET /api/reports/monthly-attendance-overview/?year=2025&month=5  # Daily present counts (bar data)
```

### Reports (Template-Rendered Charts)

```
GET /reports/attendance-chart/?year=2025&month=5       # Bar chart (HTML)
GET /reports/performance-chart/?start_year=2024&start_month=11&end_year=2025&end_month=4  # Line chart (HTML)
GET /reports/employees-per-department/               # Pie chart (HTML)
GET /reports/monthly-attendance-overview/?year=2025&month=5  # Bar chart (HTML)
```

---

## 👥 Role-based Authentication & Permissions

* **Admin** (group: Admin; `is_superuser=True`, `is_staff=True`):

  * Full CRUD on Departments, Employees, Attendance, Performance
  * Access to Django Admin panel
* **HR** (group: HR; `is_staff=True`):

  * Can list, retrieve, create, update Departments, Employees
  * Can list, retrieve, create, update Attendance & Performance
  * Cannot delete Employees or Performance or Attendance
* **Employee** (group: Employee):

  * Can retrieve or update *only own* Employee record
  * Can list, retrieve *only own* Attendance & Performance
  * Cannot create or delete any records

Permissions enforced via custom permission classes in `employees/permissions.py`:

* `IsAdminGroup` (Admin only)
* `IsHRGroup` (HR only)
* `IsEmployeeSelfOrHRorAdmin` (view or edit rules per role)

---

## 🧪 Unit Tests

Test suites exist in each app under `*/tests/`:

* `employees/tests/test_employee_viewset.py`
* `attendance/tests/test_attendance_viewset.py`
* `performance/tests/test_performance_viewset.py`
* `reports/tests/test_reports_api.py`

Run all tests with coverage:

```bash
coverage run --source='.' manage.py test
coverage report --omit="*/migrations/*,*/__init__.py"
```

---

## 📦 Docker (Attempted & Abandoned)

Docker-related files are included for reference but are **not** used in final deployment due to persistent issues during development.

* `Dockerfile`          # Django container build (not used)
* `docker-compose.yml` # PostgreSQL + Redis + Django services (not used)

If Docker is attempted, services need correct env vars and network configuration. Ultimately, local setup is recommended.

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

Once again, thank you for your time! I will definitely try my best to work on my backend software engineering internship.
