# employees/management/commands/seed_data.py

import os
import csv
import string
import secrets
import random
from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from django.conf import settings

from employees.models import Department, Employee
from attendance.models import Attendance
from performance.models import Performance

from faker import Faker


class Command(BaseCommand):
    help = (
        "1) Create Department and Employee records (each Employee linked to a new User). "
        "2) Create User accounts and assign them to the 'Employee' group (plus one HR and one Admin). "
        "3) Seed Attendance & Performance for each Employee—ensuring unique review dates per Employee. "
        "4) Generate DRF tokens and random passwords. "
        "5) Write CSV at project root with columns: username,password,token,group."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--num-departments",
            type=int,
            default=5,
            help="Number of fake Departments to create (default: 5)",
        )
        parser.add_argument(
            "--num-employees",
            type=int,
            default=60,
            help="Number of fake Employee records to create (default: 60)",
        )
        parser.add_argument(
            "--attendance-days",
            type=int,
            default=30,
            help="Number of days of Attendance per Employee (default: 30)",
        )
        parser.add_argument(
            "--min-reviews",
            type=int,
            default=2,
            help="Minimum Performance reviews per Employee (default: 2)",
        )
        parser.add_argument(
            "--max-reviews",
            type=int,
            default=5,
            help="Maximum Performance reviews per Employee (default: 5)",
        )

    def handle(self, *args, **options):
        fake = Faker()
        num_departments = options["num_departments"]
        num_employees = options["num_employees"]
        attendance_days = options["attendance_days"]
        min_reviews = options["min_reviews"]
        max_reviews = options["max_reviews"]

        # 1) Ensure Groups exist: Admin, HR, Employee
        group_names = ["Admin", "HR", "Employee"]
        groups = {}
        for name in group_names:
            grp, created = Group.objects.get_or_create(name=name)
            groups[name] = grp
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created group '{name}'"))

        # 2) Create Departments (truncate name to 20 chars)
        departments = []
        for _ in range(num_departments):
            raw_name = fake.company()
            dept_name = raw_name[:20]  # ensure <=20 chars
            dept, created = Department.objects.get_or_create(name=dept_name)
            departments.append(dept)
            if created:
                self.stdout.write(self.style.SUCCESS(f"Created department '{dept_name}'"))

        # 3) For each Employee, first create its User, then create Employee record
        credentials = []  # will collect (username, password, token, group_name)
        created_employees = []

        for _ in range(num_employees):
            # 3a) Generate a unique “fake” name
            raw_name = fake.unique.name()
            name = raw_name[:50]  # truncate to 50 chars if needed

            # 3b) Build a unique username based on name
            base_username = name.replace(" ", "_")[:30]
            username = base_username
            suffix = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{suffix}"
                suffix += 1

            # 3c) Generate random 12-char password
            alphabet = string.ascii_letters + string.digits
            password = "".join(secrets.choice(alphabet) for _ in range(12))

            # 3d) Create User and assign to Employee group
            user = User.objects.create_user(
                username=username,
                password=password,
                email="",  # will set after choosing unique email
            )
            user.groups.add(groups["Employee"])
            user.is_active = True
            user.is_staff = False
            user.save()

            # 3e) Create a DRF token for that user
            token_obj, _ = Token.objects.get_or_create(user=user)
            credentials.append((username, password, token_obj.key, "Employee"))

            # 3f) Generate a unique email for Employee (loop until unique in Employee table)
            while True:
                candidate_email = fake.unique.email()
                if not Employee.objects.filter(email=candidate_email).exists():
                    break

            # 3g) Now update User.email
            user.email = candidate_email
            user.save()

            # 3h) Prepare other Employee fields (truncate where necessary)
            phone = fake.msisdn()[:10]       # ensure <=10 chars
            address = fake.address()[:100]   # truncate to 100 chars
            doj = fake.date_between(start_date="-2y", end_date="today")
            dept = random.choice(departments)

            # 3i) Create the Employee record that links to this user
            emp = Employee.objects.create(
                name=name,
                email=candidate_email,
                phone_number=phone,
                address=address,
                date_of_joining=doj,
                department=dept,
                user=user,
            )
            created_employees.append(emp)

        self.stdout.write(self.style.SUCCESS(f"Created {len(created_employees)} Employee + User pairs."))

        # 4) Seed Attendance for each created Employee
        today = date.today()
        for emp in created_employees:
            for i in range(attendance_days):
                day = today - timedelta(days=i)
                status = random.choice(["present", "absent", "late"])
                Attendance.objects.create(employee=emp, date=day, status=status)
        self.stdout.write(self.style.SUCCESS("Seeded Attendance records."))

        # 5) Seed Performance for each created Employee, ensuring unique review_date per employee
        one_year_ago = today - timedelta(days=365)
        for emp in created_employees:
            # Build a list of all dates between one_year_ago and today
            total_days_range = (today - one_year_ago).days + 1
            all_dates = [
                one_year_ago + timedelta(days=x) for x in range(total_days_range)
            ]
            # Choose a random number of distinct dates for reviews
            num_reviews_for_emp = random.randint(min_reviews, max_reviews)
            # If fewer available dates than num_reviews_for_emp, just use them all
            chosen_dates = random.sample(all_dates, k=min(num_reviews_for_emp, len(all_dates)))

            for review_date in chosen_dates:
                rating = random.randint(1, 5)
                Performance.objects.create(
                    employee=emp, review_date=review_date, rating=rating
                )
        self.stdout.write(self.style.SUCCESS("Seeded Performance records."))

        # 6) Create a single HR user (username = "hr_user")
        hr_username = "hr_user"
        if User.objects.filter(username=hr_username).exists():
            hr_user = User.objects.get(username=hr_username)
            hr_token_obj, _ = Token.objects.get_or_create(user=hr_user)
            # Existing user—don’t override password
        else:
            hr_password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            hr_email = fake.unique.email()
            hr_user = User.objects.create_user(username=hr_username, password=hr_password, email=hr_email)
            hr_user.groups.add(groups["HR"])
            hr_user.is_active = True
            hr_user.is_staff = True
            hr_user.save()
            hr_token_obj, _ = Token.objects.get_or_create(user=hr_user)
            credentials.append((hr_username, hr_password, hr_token_obj.key, "HR"))
            self.stdout.write(self.style.SUCCESS(f"Created HR user '{hr_username}'"))

        # 7) Create a single Admin user (username = "admin_user")
        admin_username = "admin_user"
        if User.objects.filter(username=admin_username).exists():
            admin_user = User.objects.get(username=admin_username)
            admin_token_obj, _ = Token.objects.get_or_create(user=admin_user)
            # Existing user—don’t override password
        else:
            admin_password = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
            admin_email = fake.unique.email()
            admin_user = User.objects.create_user(username=admin_username, password=admin_password, email=admin_email)
            admin_user.groups.add(groups["Admin"])
            admin_user.is_active = True
            admin_user.is_staff = True
            admin_user.is_superuser = True
            admin_user.save()
            admin_token_obj, _ = Token.objects.get_or_create(user=admin_user)
            credentials.append((admin_username, admin_password, admin_token_obj.key, "Admin"))
            self.stdout.write(self.style.SUCCESS(f"Created Admin user '{admin_username}'"))

        # 8) Write CSV to project root
        base_dir = settings.BASE_DIR
        csv_path = os.path.join(base_dir, "user_credentials.csv")

        try:
            with open(csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["username", "password", "token", "group"])
                for username, pwd, tkn, grp_name in credentials:
                    writer.writerow([username, pwd, tkn, grp_name])
            self.stdout.write(self.style.SUCCESS(f"Wrote CSV: {csv_path}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to write CSV: {e}"))
