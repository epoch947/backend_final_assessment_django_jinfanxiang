
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from employees.models import Department, Employee
from attendance.models import Attendance


class ReportsAPITests(APITestCase):
    def setUp(self):
        # Create Groups
        self.admin_group = Group.objects.create(name="Admin")
        self.hr_group = Group.objects.create(name="HR")
        self.emp_group = Group.objects.create(name="Employee")

        # Create an Admin user
        self.admin_user = User.objects.create_user(username="admin", password="pass123")
        self.admin_user.is_staff = True
        self.admin_user.is_superuser = True
        self.admin_user.save()
        self.admin_group.user_set.add(self.admin_user)
        self.admin_token = Token.objects.create(user=self.admin_user)

        # Create an HR user
        self.hr_user = User.objects.create_user(username="hr", password="pass123")
        self.hr_user.is_staff = True
        self.hr_user.save()
        self.hr_group.user_set.add(self.hr_user)
        self.hr_token = Token.objects.create(user=self.hr_user)

        # Create an Employee user
        self.emp_user = User.objects.create_user(username="alice", password="pass123")
        self.emp_user.save()
        self.emp_group.user_set.add(self.emp_user)
        self.emp_token = Token.objects.create(user=self.emp_user)

        # Create Departments (names ≤ 10 chars)
        self.dept_eng = Department.objects.create(name="EngDept")
        self.dept_hr = Department.objects.create(name="AB")

        # Create Employee records
        self.emp_record1 = Employee.objects.create(
            name="Alice",
            email="alice@example.com",
            phone_number="1112223333",
            address="123 St",
            date_of_joining="2024-01-01",
            department=self.dept_eng,
            user=self.emp_user
        )
        # Another employee (for department aggregation)
        self.emp_record2 = Employee.objects.create(
            name="Bob",
            email="bob@example.com",
            phone_number="4445556666",
            address="456 Ave",
            date_of_joining="2024-02-01",
            department=self.dept_hr,
            user=self.hr_user
        )

        # Populate Attendance for June 2025
        Attendance.objects.create(employee=self.emp_record1, date="2025-06-01", status="present")
        Attendance.objects.create(employee=self.emp_record1, date="2025-06-02", status="absent")
        Attendance.objects.create(employee=self.emp_record2, date="2025-06-01", status="present")
        Attendance.objects.create(employee=self.emp_record2, date="2025-06-03", status="present")

    def test_monthly_attendance_chart_access(self):
        """
        All authenticated roles may GET /monthly-attendance-chart/?year=&month=.
        Response should match aggregated data.
        """
        url = reverse('monthly-attendance-chart')
        params = {'year': 2025, 'month': 6}

        # As Employee
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token.key}")
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['year'], 2025)
        self.assertEqual(response.data['month'], 6)
        self.assertEqual(response.data['total_records'], 4)
        self.assertEqual(response.data['present_count'], 3)
        self.assertEqual(response.data['absent_count'], 1)

        # As HR
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['present_count'], 3)

        # As Admin
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['absent_count'], 1)

    def test_monthly_attendance_chart_missing_params(self):
        """
        Omitting year or month returns 400 Bad Request, for any role.
        """
        url = reverse('monthly-attendance-chart')

        # As Employee
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token.key}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # As HR
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.get(url, {'year': 2025})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # As Admin
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(url, {'month': 6})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_monthly_attendance_rate_access(self):
        """
        All authenticated roles may GET /monthly-attendance/?year=&month=.
        Response should be a paginated list of {department, totals, rates}.
        """
        url = reverse('monthly-attendance')
        params = {'year': 2025, 'month': 6}

        # As Employee
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token.key}")
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        dept_names = {item['department_name'] for item in response.data['results']}
        self.assertSetEqual(dept_names, {"EngDept", "AB"})

        # As HR
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for item in response.data['results']:
            self.assertIn('attendance_rate', item)

        # As Admin
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('results', response.data)

    def test_monthly_attendance_rate_missing_params(self):
        """
        Omitting year or month returns 400 Bad Request, for any role.
        """
        url = reverse('monthly-attendance')

        # As Employee
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.emp_token.key}")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # As HR
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.hr_token.key}")
        response = self.client.get(url, {'year': 2025})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # As Admin
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.admin_token.key}")
        response = self.client.get(url, {'month': 6})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
