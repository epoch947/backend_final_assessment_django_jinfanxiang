# employees/management/commands/seed_data.py
from django.core.management.base import BaseCommand
from employees.models import Department, Employee
from attendance.models import Attendance
from performance.models import Performance
from faker import Faker
import random
from datetime import date, timedelta


class Command(BaseCommand):
    help = "Seed the database with fake Departments, Employees, Attendance, and Performance records."

    def handle(self, *args, **options):
        fake = Faker()

        # 1. Create Departments if they don’t exist
        dept_names = ["Engineering", "HR", "Marketing", "Finance", "Sales"]
        departments = []
        for name in dept_names:
            dept, created = Department.objects.get_or_create(name=name)
            departments.append(dept)

        # 2. Create 30–50 fake employees
        employees = []
        for _ in range(40):
            dept = random.choice(departments)
            raw_phone = fake.phone_number()
            phone = raw_phone[:10]  # cut off any extra length
            emp = Employee.objects.create(
                name=fake.name(),
                email=fake.unique.email(),
                phone_number=phone,
                address=fake.address(),
                date_of_joining=fake.date_between(start_date="-2y", end_date="today"),
                department=dept,
            )
            employees.append(emp)

        # 3. Create Attendance records
        for emp in employees:
            # Randomly generate attendance over the past month
            for i in range(30):
                day = date.today() - timedelta(days=i)
                status = random.choice(["present", "absent", "late"])
                Attendance.objects.create(employee=emp, date=day, status=status)

        # 4. Create Performance records
        for emp in employees:
            # Generate 3–5 performance reviews over the past year
            num_reviews = random.randint(3, 5)
            for _ in range(num_reviews):
                review_date = fake.date_between(start_date="-1y", end_date="today")
                rating = random.randint(1, 5)
                Performance.objects.create(
                    employee=emp, review_date=review_date, rating=rating
                )

        self.stdout.write(self.style.SUCCESS("Successfully seeded data."))
